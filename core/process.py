import multiprocessing
import multiprocessing.connection
import threading
import asyncio
import sys
import uuid
from typing import List, Callable
import core.application
import core.language
import core.session
from core.utility.convert import Convert, RemoteError
from core.utility.proxy import Reloader, Proxy


class Control:
    """
    Wrapper around pipe to exchange values between child process and parent process.
    This class should be used by *child process*.
    """
    pipe = None

    @staticmethod
    def setpipe(pipe: multiprocessing.Pipe):
        Control.pipe = pipe

    @staticmethod
    def send(obj):
        """
        Send an object to parent 
        """
        msg = {
            'message': 'send',
            'value': obj
        }
        Control.pipe.send(msg)

    @staticmethod
    def sendrecv(obj):
        """
        Send an object to parent and wait for response
        """        
        msg = {
            'message': 'sendrecv',
            'value': obj
        }
        Control.pipe.send(msg)

        res = Control.waitfor('answer')
        return res['value']

    @staticmethod
    def response(obj):
        """
        Send a respone to parent
        """
        msg = {
            'message': 'response',
            'value': obj
        }  
        Control.pipe.send(msg)

    @staticmethod
    def error(err):
        """
        Send an error to parent
        """        
        try:
            msg = {
                'message': 'error',
                'value': err
            }
            Control.pipe.send(msg)

        except:
            pass

    @staticmethod
    def waitfor(tag):
        """
        Receive a specific message from the parent, handling special methods
        """
        while True:
            obj = Control.pipe.recv()

            if obj['message'] == 'reload':
                Reloader.reload_module(obj['value'])
                continue

            elif obj['message'] == 'error':
                raise Exception(obj['value'])

            elif obj['message'] == tag:
                return obj
            
            else:
                raise Exception(core.language.label('Received \'{0}\' message, waiting for \'{1}\''.format(obj['message'], tag)))

        
def worker_loop(args):
    """
    Process worker loop
    """

    try:
        core.application.Application.initialize()
        core.application.Application._cli_loglevel = args['cli_loglevel']
        core.application.Application._log_lock = args['log_lock']
        
        core.application.Application.load_instance(args['instname'])

        Control.setpipe(args['pipe'])

        core.session.Session.connect()

        core.application.Application.log('prcwrker', 'I', core.language.label('Process ready to work'))

        while True:
            try:
                obj = Control.waitfor('request')

                if not obj['keepalive']:
                    core.session.Session.initialize()

                result = obj['function'](*obj['args'])
                core.utility.system.commit()   
                Control.response(result)                        
    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except:
                core.application.Application.logexception('prcwrker')
                Control.error(Convert.formatexception(1))   

    except:
        core.application.Application.logexception('prcwrker')

    # cleanup
    try:
        core.session.Session.disconnect()
    except:
        pass

    core.application.Application.log('prcwrker', 'I', core.language.label('Process shutdown'))      


class Worker:
    """
    Defines a worker process
    """
    def __init__(self):
        pipe_pair = multiprocessing.Pipe()

        args = {
            'instname': core.application.Application.instance['name'],
            'cli_loglevel': core.application.Application._cli_loglevel,
            'log_lock': core.application.Application._log_lock,
            'pipe': pipe_pair[1]
        }  

        self.id = str(uuid.uuid4())
        self.process = multiprocessing.Process(target=worker_loop, args=(args, ))
        self.pipe_pair = pipe_pair
        self.pipe = self.pipe_pair[0]

        self.busy = False
        self.recv_callback = None # type: Callable[[any], None]
        self.keep_alive = False

    def cleanup(self):
        """
        Prepare a worker for next cycle
        """
        self.busy = False
        self.recv_callback = None
        self.keep_alive = False

    def start(self):
        """
        Start the worker process
        """
        self.process.start()

    def kill(self):
        """
        Kill itself
        """
        self.process.kill()

    def recv_sync(self):
        """
        Receive a message from the child (sync)
        """
        try:
            if not self.process.is_alive():
                raise Exception('Process {0} killed'.format(self.process.pid))

            if not self.pipe.poll():
                return None

            msg = self.pipe.recv()

            if msg['message'] not in ['error', 'response']:
                raise Exception(core.language.label('Invalid message {0} in recv sync'.format(msg['message'])))

            if msg['message'] == 'error':
                raise RemoteError(msg['value'])

            return msg

        finally:
            self.cleanup()

    async def recv(self):
        """
        Receive a message from the child
        """
        try:
            while True:
                await asyncio.get_event_loop().run_in_executor(None, self.pipe.poll, None)
                msg = self.pipe.recv()

                if msg['message'] == 'send':
                    if self.recv_callback:
                        self.recv_callback(msg)
                    continue

                break

            if msg['message'] == 'error':
                raise RemoteError(msg['value'])
            
            return msg

        finally:
            if not self.keep_alive:
                self.cleanup()

    def error(self, message):
        """
        Send error to chil
        """
        msg = {
            'message': 'error',
            'value': message
        }
        self.send(msg)

    def send(self, obj):
        """
        Send a message to the child
        """
        self.pipe.send(obj)

    def request(self, function, *args):
        """
        Send a request to the child
        """
        msg = {
            'message': 'request',
            'function': function,
            'args': args,
            'keepalive': self.keep_alive
        }
        self.pipe.send(msg)


class ProcessPool:
    """
    Handles multiprocessing
    """    

    def __init__(self, min_workers, max_workers):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.pool = []  # type: List[Worker]
        self.busy_event = threading.Event()
        self.lock_pool = threading.Lock()
        self.exit = False

    def add_worker(self):
        """
        Add a new worker to pool
        """
        worker = Worker()
        worker.start()
        self.pool.append(worker)
        return worker  

    def start(self):
        """
        Start process factory
        """
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        core.application.Application.log('prcwrker', 'I', core.language.label(
            'Starting {0} / {1} worker processes'.format(self.min_workers, self.max_workers)))
        
        self.exit = False
        self.busy_event.clear()

        with self.lock_pool:
            for i in range(0, self.min_workers):
                self.add_worker()

    def stop(self):
        """
        Stop process factory
        """
        self.exit = True

        with self.lock_pool:
            while self.pool:
                for worker in self.pool:
                    if worker.pipe_pair is not None:
                        worker.pipe_pair[0].close()
                        worker.pipe_pair[1].close()
                        worker.pipe_pair = None

                    if not worker.process.is_alive():
                        self.pool.remove(worker)
                        break

        self.busy_event.set()                

    def notify_reload(self, modulename):
        """
        Notify workers to reload a specific module
        """
        for worker in self.pool:
            worker.pipe.send({'message': 'reload', 'value': modulename})

    def trygetworker(self):
        """
        Try get a worker, the first available or a new one if is possible
        """
        result = None

        with self.lock_pool:
            for worker in self.pool:
                if not worker.busy:
                    if not worker.process.is_alive():
                        core.application.Application.log('prcwrker', 'W', core.language.label(
                            'Process \'{0}\' is not responding, adding a new process to pool'.format(
                                worker.process.pid)))
                        self.pool.remove(worker)
                        result = self.add_worker()

                    else:
                        result = worker

                    result.busy = True
                    break

        if (not result) and (len(self.pool) < self.max_workers):
            core.application.Application.log('prcwrker', 'I', core.language.label(
                'Adding a new process to pool {0}'.format(len(self.pool) + 1)))

            with self.lock_pool:
                result = self.add_worker()
                result.busy = True

        return result

    async def getworker(self):
        """
        Get a worker, the first available or a new one if is possible
        """
        result = None

        while not self.exit:
            result = self.trygetworker()
            if result:
                break

            core.application.Application.log('prcwrker', 'W', core.language.label('Process pool is full {0}'.format(len(self.pool))))
            await asyncio.get_event_loop().run_in_executor(None, self.busy_event.wait)
            self.busy_event.clear()

        return result


class Task:
    @staticmethod
    def _worker(workerid, unitname, method, runas, *args):
        """
        Worker main function
        """
        core.session.Session.type = 'batch'
        core.session.Session.authenticated = True
        if runas:
            core.session.Session.user_id = runas
        core.session.Session.start()

        try:
            proxy = Proxy(unitname)
            proxy.create()
            return proxy.invoke(method, workerid, *args)

        finally:
            core.session.Session.stop()

    @staticmethod
    def kill(workerid):
        """
        Kill worker
        """
        for worker in core.application.Application.process_pool.pool:
            if worker.id == workerid.lower():
                worker.kill()

    @staticmethod
    def getresult(workerid):
        """
        Get result or error
        """
        for worker in core.application.Application.process_pool.pool:
            if worker.id == workerid.lower():
                return worker.recv_sync()

        return None

    @staticmethod
    def run(unitname, method, runas, *args):
        """
        Run task async
        """
        worker = core.application.Application.process_pool.trygetworker()
        if not worker:
            return None

        worker.request(Task._worker, worker.id, unitname, method, runas, *args)
        return worker.id
