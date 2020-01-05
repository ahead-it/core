import os
import socket
import tornado.web
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.log
import tornado.escape
import ssl
import json
from OpenSSL import crypto
import core.application
import core.session
import core.process
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


def _rpc_dispatcher(control, path, kwargs, cookie):
    """
    Dispatch GET/POST requests is separate process
    """
    parts = path.split('/')
    if len(parts) != 2:
        raise Exception('Invalid request \'{0}\''.format(path))

    proxy = Proxy('app.codeunit.' + parts[0])
    proxy.create()
    return proxy.invoke(parts[1], **kwargs)
    

class RpcHandler(tornado.web.RequestHandler):
    """
    Serves Core in REST mode
    """
    async def get(self, path):
        await self._handle('GET', path)

    async def post(self, path):
        await self._handle('POST', path)

    async def _handle(self, method, path):
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

            cookie = self.get_cookie("core-sessid")

            self.set_header("Content-Type", 'application/json')

            result = await core.application.Application.process_pool.enqueue_wait(None, _rpc_dispatcher, 
                path, kwargs, cookie)

            self.write(json.dumps(result).encode("utf8"))

        except core.process.RemoteError as ex:
            self._send_error(ex.fmt_exception)

        except:
            self._send_error(Convert.formatexception())

    def _send_error(self, exc):
        exc['type'] = 'exception'

        self.set_header("Content-Type", 'application/json')
        self.write(json.dumps(exc).encode("utf8"))
        self.set_status(500)
            

class WsHandler(tornado.websocket.WebSocketHandler):
    pass


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
            paths.append(('/?(.*)', tornado.web.StaticFileHandler, 
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
        
