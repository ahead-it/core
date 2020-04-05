import os
import socket
import asyncio
import tornado.web
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.log
import tornado.escape
import ssl
import uuid
import json
from OpenSSL import crypto
import core.application
import core.session
import core.process
import core.utility.system
from core.utility.convert import Convert
from core.language import label
from core.utility.proxy import Proxy


def _write_accesslog(handler):
    """
    Writes access log of the http requests
    """
    cl = 0
    if "Content-Length" in handler._headers:
        cl = handler._headers["Content-Length"]

    fn = core.application.Application.base_path + 'var/log/' +\
         core.application.Application.instance['name'] + '.webserver-' + Convert.formatdatetime2() + '.log'
    try:
        fs = open(fn, 'a')
        fs.write(Convert.formatdatetime1() + " " +
                 handler.request.method + " " +
                 handler.request.uri + " " +
                 handler.request.remote_ip + " " +
                 str(handler.get_status()) + " " +
                 str(cl) + " " + 
                 str(int(handler.request.request_time() * 1000)) + '\n')
        fs.close()
    except:
        pass


def _rpc_dispatcher(path, kwargs, token):
    """
    Dispatch GET/POST requests in separate process
    """
    core.session.Session.type = 'web'
    core.session.Session.set_auth_token(token)

    parts = path.split('/')
    if len(parts) != 2:
        raise Exception('Invalid request \'{0}\''.format(path))

    classname = 'app.codeunit.' + parts[0]
    method = parts[1]

    proxy = Proxy(classname)
    proxy.create()
    result = proxy.invoke(method, **kwargs)
    return result
    

class RpcHandler(tornado.web.RequestHandler):
    """
    Serves Core in REST mode
    """
    def initialize(self):
        self.ctlproxy = core.process.ControlProxy(self._receive_callback)

    async def get(self, path):
        await self._handle('GET', path)

    async def post(self, path):
        await self._handle('POST', path)

    async def options(self, path):
        self._set_headers()
        self.set_status(204)        
        self.finish()

    def _set_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')    

    def _receive_callback(self, message):
        """
        Receive callback from child process and send to client
        """
        try:
            if message['action'] == 'saveauthtoken':
                self.set_cookie('core-auth-token', message['token'], expires_days=message['days'])

            elif message['action'] == 'delauthtoken':
                self.clear_cookie('core-auth-token')

            else:
                raise Exception(core.language.label('Invalid message \'{0}\' for client'.format(message['action'])))

        except:     
            core.application.Application.logexception('webservr')

    async def _handle(self, method, path):
        """
        Generic GET/POST handler
        """
        self._set_headers()
        
        try:
            if (method == 'POST') and \
               ('Content-Type' in self.request.headers) and \
               (self.request.headers['Content-Type'] == "application/json"):
                kwargs = json.loads(self.request.body)
            else:
                kwargs = {}
                for k in self.request.arguments:
                    val = self.request.arguments[k][0].decode("utf8")
                    try:
                        kwargs[k] = json.loads(val) 
                    except:
                        kwargs[k] = val

            token = WebServer.get_authtoken(self)
            if not token:
                self.set_cookie('core-auth-token', str(uuid.uuid4()))

            self.set_header("Content-Type", 'application/json')
            
            result = await core.application.Application.process_pool.enqueue(self.ctlproxy, _rpc_dispatcher, 
                path, kwargs, token)

            if result is not None:
                self.write(json.dumps(result).encode("utf8"))

        except core.process.RemoteError as ex:
            self._send_error(ex.fmt_exception)

        except:
            self._send_error(Convert.formatexception())

    def _send_error(self, exc):
        """
        Returns error 500 in case of exception
        """
        exc['type'] = 'exception'

        self.set_header("Content-Type", 'application/json')
        self.write(json.dumps(exc).encode("utf8"))
        self.set_status(500)


def _ws_dispatcher(action, session_id, token, message):
    """
    Dispatch websocket requests is separate process
    """
    if action == 'open':
        core.session.Session.type = 'socket'
        core.session.Session.register()
        return core.session.Session.id    

    elif action == 'close':
        core.session.Session.unregister(session_id)
    
    elif action == 'message':
        core.session.Session.load(session_id)
        result = None

        if message['type'] == 'invoke':
            if 'classname' in message:
                proxy = Proxy(message['classname'])
                proxy.create()
            else:
                proxy = core.session.Session.objects[message['objectid']]

            result = proxy.invoke(message['method'], **message['arguments'])

        elif message['type'] == 'create':
            proxy = Proxy(message['classname'])
            proxy.create()  
            core.session.Session.objects[proxy.object._id] = proxy
            result = proxy.object._id

        elif message['type'] == 'destroy':
            del core.session.Session.objects[message['objectid']]

        else:
            raise Exception(label('Invalid message type'))  

        core.session.Session.register()
        return result

    else:
        raise Exception(label('Invalid request'))


class WsHandler(tornado.websocket.WebSocketHandler):
    """
    Handles websocket
    """
    def initialize(self):
        self.ctlproxy = core.process.ControlProxy(self._receive_callback)
        self.session_id = ''
        self.token = ''

    def check_origin(self, origin):
        return True

    async def get(self):
        self.token = WebServer.get_authtoken(self)
        await super().get()

    async def open(self):
        try:
            self.session_id = await core.application.Application.process_pool.enqueue(self.ctlproxy, 
                _ws_dispatcher, 'open', None, self.token, None)

        except core.process.RemoteError as ex:
            self._send_error(ex.fmt_exception)

        except:
            self._send_error(Convert.formatexception())            

    async def on_message(self, message):
        # Asynchronous on message
        # https://github.com/tornadoweb/tornado/blob/master/docs/releases/v4.5.0.rst#tornadowebsocket
        # WebServer._loop.spawn_callback(self._handle_message, message)
        await self._handle_message(message)

    async def _handle_message(self, message):
        try:
            message = json.loads(message)

            result = await core.application.Application.process_pool.enqueue(self.ctlproxy, 
                _ws_dispatcher, 'message', self.session_id, self.token, message)
            
            msg = {
                'type': 'result',
                'value': result
            }
            self.write_message(json.dumps(msg))

        except core.process.RemoteError as ex:
            self._send_error(ex.fmt_exception)

        except:
            self._send_error(Convert.formatexception())          
        
    def on_close(self):
        try:
            asyncio.create_task(
                core.application.Application.process_pool.enqueue(self.ctlproxy, 
                    _ws_dispatcher, 'close', self.session_id, self.token, None))
        except:
            pass

    def _receive_callback(self, message):
        """
        Receive callback from child process and send to websocket
        """
        msg = {
            'type': 'message',
            'value': message
        }
        self.write_message(json.dumps(message))

    def _send_error(self, exc):
        """
        Returns JSON error in case of exception
        """
        exc['type'] = 'exception'
        self.write_message(json.dumps(exc))


class StaticHandler(tornado.web.StaticFileHandler):
    async def get(self, path):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET, OPTIONS')   
        await super().get(path);


class WebServer:
    """
    Defines the application web server
    """
    _loop = None

    @staticmethod
    def start():
        """
        Start the webserver
        """
        try:
            app = tornado.web.Application(log_function=_write_accesslog)

            paths = []

            paths.append(("/rpc/(.*)", RpcHandler, {})) 

            paths.append(("/ws", WsHandler, {}))

            dn = core.application.Application.instance['path'] + 'webroot'
            if not os.path.isdir(dn):
                os.mkdir(dn)
            paths.append(('/?(.*)', StaticHandler, 
                {
                    'path': dn, 
                    'default_filename': 'index.html'
                }))

            app.add_handlers('.*', paths)

            sslctx = None
            if core.application.Application.instance['webserver_secure']:
                sslctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                if 'certificate' in core.application.Application.instance:
                    sslctx.load_cert_chain(
                        certfile=core.application.Application.instance['certificate'],
                        keyfile=core.application.Application.instance['certificate_key']
                    )
                else:
                    crts = WebServer._createcertificate()
                    sslctx.load_cert_chain(
                        certfile=crts[0],
                        keyfile=crts[1]
                    )

            hn = tornado.log.logging.NullHandler()
            hn.setLevel(tornado.log.logging.DEBUG)
            tornado.log.logging.getLogger("tornado.general").addHandler(hn)
            tornado.log.logging.getLogger("tornado.general").propagate = False

            server = tornado.httpserver.HTTPServer(app, ssl_options=sslctx)
            server.listen(core.application.Application.instance['webserver_port'])

            core.application.Application.log('webservr', 'I', label('Started {0} server on port {1}'.format(
                'https' if sslctx else 'http', 
                core.application.Application.instance['webserver_port'])))

            tornado.ioloop.PeriodicCallback(WebServer._check, 2000).start() 
            WebServer._loop = tornado.ioloop.IOLoop.current()
            WebServer._loop.start()   

        except:     
            core.application.Application.logexception('webservr')

    @staticmethod
    def stop():
        """
        Request stop of the webserver
        """
        try:
            if WebServer._loop is not None:
                WebServer._loop.stop()
                core.application.Application.log('webservr', 'I', label('Server stopped'))
        except:
            core.application.Application.logexception('webservr')

    @staticmethod
    def _check():
        """
        Cyclic callback of the webserver to process signals
        """
        return

    @staticmethod
    def _createcertificate():
        """
        Creates self signed certificate
        """
        fnc = core.application.Application.instance['path'] + socket.gethostname() + ".crt"
        fnk = core.application.Application.instance['path'] + socket.gethostname() + ".key"

        if not os.path.isfile(fnc):
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 2048)
            
            cert = crypto.X509()
            cert.get_subject().CN = "localhost"
            cert.set_serial_number(0)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.sign(k, 'sha1')
                    
            f = open(fnc, "wb")
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            f.close()

            f = open(fnk, "wb")
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
            f.close()

        return (fnc, fnk)
        
    @staticmethod
    def get_authtoken(handler: tornado.web.RequestHandler):
        if 'X-Core-AuthToken' in handler.request.headers:
            return handler.request.headers['X-Core-AuthToken']

        return handler.get_cookie("core-auth-token")

