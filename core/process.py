import multiprocessing
import multiprocessing.connection
import threading
import asyncio
import sys
from typing import List, Callable
import core.application
import core.language
import core.session
from core.utility.convert import Convert
from core.utility.proxy import Reloader


class Control:
    """
    Wrapper around pipe to exchange values between child process and parent process.
    This class should be used by *child process*.
    """
    def __init__(self, pipe: multiprocessing.Pipe):
        self.pipe = pipe

    def send(self, obj):
        """
        Send an object to parent 
        """
        msg = {
            'message': 'control',
            'value': obj
        }
        self.pipe.send(msg)

    def recv(self):
        """
        Receive an object from parent
        """        
        obj = self.pipe.recv()
        return obj['value']


class ControlProxy:
    """
    Wrapper around pipe to control parent from child process.
    'receive_callback' is called into parent when a message is received from child.
    """
    def __init__(self, receive_callback: Callable[[any], None]):
        self.pipe = None # type: multiprocessing.Pipe
        self.receive_callback = receive_callback # type: Callable[[any], None]

    def send(self, obj):
        """
        Send an object to child
        """
        msg = {
            'message': 'control',
            'value': obj
        }
        self.pipe.send(msg)


class RemoteError(Exception):
    """
    Defines an error raised in child process. In 'fmt_exception' the remote exception well formatted 
    with traceback.
    """
    def __init__(self, value):
        super().__init__(value['message'])
        self.fmt_exception = value

        
def worker_loop(args):
    """
    Process worker loop
    """

    try:
        core.application.Application.initialize()
        core.application.Application._cli_loglevel = args['cli_loglevel']
        core.application.Application._log_lock = args['log_lock']
        
        core.application.Application.load_instance(args['instname'])

        pipe = args['pipe']
        control = Control(pipe)

        core.session.Session.connect()

        core.application.Application.log('prcwrker', 'I', core.language.label('Process ready to work'))

        while True:
            obj = pipe.recv()
            
            try:
                if obj['message'] == 'request':
                    try:
                        core.session.Session.initialize()
                        
                        msg = {
                            'message': 'response',
                            'value': obj['function'](control, *obj['args']),
                            'success': True
                        }
                        pipe.send(msg)
                    except:
                        core.application.Application.logexception('prcwrker')

                        try:
                            msg = {
                                'message': 'response',
                                'value': Convert.formatexception(1),
                                'success': False
                            }
                            pipe.send(msg)
                        except:
                            pass

                elif obj['message'] == 'reload':
                    Reloader.reload_module(obj['value'])

                else:
                    raise Exception(core.language.label('Unknown message \'{0}\''.format(obj)))

            except:
                core.application.Application.logexception('prcwrker')

    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
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

        self.process = multiprocessing.Process(target=worker_loop, args=(args, ))
        self.pipe_pair = pipe_pair
        self.pipe = self.pipe_pair[0]
        self.busy = False
        self.control = None # type: ControlProxy

    def start(self):
        """
        Start the worker process
        """
        self.process.start()

    async def receive(self):
        """
        Receive a message from the child. If message is of the 'control' type is dispatched to
        the control callback. If 'response' message is not success a RemoteError is raised.
        """
        while True:
            await asyncio.get_event_loop().run_in_executor(None, self.pipe.poll, None)
            msg = self.pipe.recv()

            if msg['message'] == 'control':
                if self.control is not None:
                    self.control.receive_callback(msg['value'])
                continue

            break
        
        return msg


class ProcessPool:
    """
    Handles multiprocessing
    """    

    def __init__(self, max_workers):
        self.max_workers = max_workers
        self.pool = [] # type: List[Worker]
        self.manager = multiprocessing.Manager()
        self.busy_event = threading.Event()

    def add_worker(self):
        """
        Add a new worker to pool
        """
        worker = Worker()
        worker.start()
        self.pool.append(worker)    

    def start(self):
        """
        Start process factory
        """
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        core.application.Application.log('prcwrker', 'I', core.language.label(
            'Starting {0} worker processes'.format(self.max_workers)))
        
        for i in range(0, self.max_workers):
            self.add_worker()

    def stop(self):
        """
        Stop process factory
        """
        while self.pool:
            for worker in self.pool:
                if worker.pipe_pair is not None:
                    worker.pipe_pair[0].close()
                    worker.pipe_pair[1].close()
                    worker.pipe_pair = None

                if not worker.process.is_alive():
                    self.pool.remove(worker)
                    break  

    def notify_reload(self, modulename):
        """
        Notify workers to reload a specific module
        """
        for worker in self.pool:
            worker.pipe.send({'message': 'reload', 'value': modulename})
              
    async def enqueue_wait(self, control: ControlProxy, function, *args):
        """
        Enqueue a job and wait for result
        """
        worker = await self.enqueue(control, function, *args)
        return await self.receive(worker)

    async def enqueue(self, control: ControlProxy, function, *args) -> Worker:
        """
        Enqueue a job in the first process available. If no one available will hold.
        """        
        while True:
            found = False
            repeat = False
            for worker in self.pool:
                if not worker.busy:
                    if not worker.process.is_alive():
                        core.application.Application.log('prcwrker', 'W', core.language.label(
                            'Process \'{0}\' is not responding, adding a new process to pool'.format(worker.process.pid)))
                        self.pool.remove(worker)
                        self.add_worker()
                        repeat = True
                        break

                    msg = {
                        'message': 'request',
                        'function': function,
                        'args': args
                    }
                    worker.busy = True
                    worker.pipe.send(msg)
                    worker.control = control
                    if worker.control is not None:
                        worker.control.pipe = worker.pipe
                    found = True
                    break
            
            if repeat:
                continue
            elif found:
                break
            else:
                core.application.Application.log('prcwrker', 'W', core.language.label('Process pool is full'))
                await asyncio.get_event_loop().run_in_executor(None, self.busy_event.wait)
                self.busy_event.clear()

        return worker

    async def receive(self, worker: Worker):
        """
        Wait the result for selected worker
        """
        result = await worker.receive()
        
        worker.control = None
        worker.busy = False
        self.busy_event.set()

        if not result['success']:
            raise RemoteError(result['value'])

        return result['value']
