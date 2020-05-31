import multiprocessing
import threading
import os
import importlib
import inspect
import time
from datetime import datetime
from typing import Dict
import json
from core.session import Session
from core.app import AppInfo
import core
import core.language
import core.object.table
import core.webserver
from core.utility.convert import Convert
import core.utility.proxy
import core.process


class Application:
    """
    Defines an application server on some host that contains apps
    """
    _cli_loglevel = []
    _log_lock = multiprocessing.Lock()
    _thd_check = None
    _thd_check_exit = False

    VERSION = '1.0.20005.0'

    base_path = ''
    apps = {}  # type: Dict[str, AppInfo]
    all_apps = {}  # type: Dict[str, AppInfo]
    instance = {}  # type: dict
    process_pool = None  # type: core.process.ProcessPool
        
    @staticmethod
    def initialize():
        """
        Initialize the application on local server
        Load all apps; assert minimal working directory
        """
        bp = __file__[:-19]
        bp = bp.replace("\\", "/")
        if not bp.endswith('/'):
            bp += '/'
        Application.base_path = bp
        Application._load_apps()
        core.language.loadtranslations()

        if not os.path.exists(bp + 'var'):
            os.mkdir(bp + 'var')

        if not os.path.exists(bp + 'var/log'):
            os.mkdir(bp + 'var/log')

        Session.initialize()

    @staticmethod
    def _assert_default(opts: dict, key, value):
        if key not in opts:
            opts[key] = value

    @staticmethod
    def load_instance(instname):
        """
        Load specific instance
        """
        try:        
            bp = Application.base_path + 'var/instance/' + instname + '/'
            with open(bp + 'config.json', 'r') as fs:
                config = fs.read()

            opts = json.loads(config)
            opts['name'] = instname
            opts['path'] = bp

            Application._assert_default(opts, 'display_name', instname)
            Application._assert_default(opts, 'db_debug', False)
            Application._assert_default(opts, 'ws_debug', False)
            Application._assert_default(opts, 'dataset_size', 50)
            Application._assert_default(opts, 'webserver_enabled', False)
            Application._assert_default(opts, 'webserver_port', 8080)
            Application._assert_default(opts, 'webserver_secure', False)
            Application._assert_default(opts, 'min_processes', 2)            
            Application._assert_default(opts, 'max_processes', 32)
            Application._assert_default(opts, 'scheduler_enabled', False)

            Application.instance = opts
            Session.instance = instname

        except:
            Application.logexception('loadinst')    

    @staticmethod
    def _load_apps():
        """
        Load all the apps and register in the application
        """
        Application.apps.clear()

        app_list = {}
        app_path = Application.base_path + "app/"
        if os.path.exists(app_path + 'apps.py'):
            mod = importlib.import_module('app.apps')
            app_list = getattr(mod, 'apps')

        # Register all the apps
        for app in os.listdir(app_path):
            dn = app_path + app
            if os.path.isdir(dn) and (not app.startswith("__")):
                try:
                    mod = importlib.import_module("app." + app)
                    nfo = getattr(mod, '__appinfo')()
                    Application.all_apps[nfo.name] = nfo

                    if (nfo.name in app_list) and app_list[nfo.name]:
                        Application.apps[nfo.name] = nfo
                        Application.log('loadapps', 'I', core.language.label('App \'{0}\' version \'{1}\' loaded'.format(
                            nfo.display_name, nfo.version)))

                except:
                    Application.logexception('loadapps')

    @staticmethod
    def log(context, severity, message):
        """
        Log a message in the application or instance log in a specific context
        """
        if len(context) > 8:
            context = context[:8]
        elif len(context) < 8:
            context = context.rjust(8, '-')

        message = message.replace('\r', '')
        message = message.replace('\n', ' ')            
        message = message.replace('\t', ' ')

        if not severity in ['E', 'W', 'I', 'D']:
            severity = 'E'

        line = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        line += ' ' + severity
        line += ' ' + context
        line += ' ' + Session.type
        line += ' ' + str(Session.process_id)
        
        if Session.user_id:
            line += ' ' + Session.user_id
        else:
            line += ' -'

        line += ' ' + message

        Application._log_lock.acquire()
        try:
            if severity in Application._cli_loglevel:
                print(line)

            dn = 'application'
            if Application.instance:
                dn = Application.instance['name']
            fn = Application.base_path + 'var/log/' + dn + '-' + datetime.now().strftime('%Y%m%d') + '.log'
            f = open(fn, "a")
            f.write(line + '\n')
            f.close()    
        except:
            pass   
        finally:
            Application._log_lock.release()

    @staticmethod
    def logexception(context):
        """
        Log the current exception in the application log or instance in a specific context
        Use inside try/catch
        """     
        exc = Convert.formatexception()
        message = exc['class'] + ' ' + exc['message'] + ' ' + exc['trace'][0]
        Application.log(context, 'E', message)

    @staticmethod
    def synchronize_schema():
        """
        Synchronize database schema in the current instance
        """
        res = True
        try:        
            if not Application.instance:
                raise Exception(core.language.label('No instance connected'))

            fn = Application.base_path + 'app/table.py'
            if not os.path.isfile(fn):
                return True

            mod = importlib.import_module('app.table')
            for name, obj in inspect.getmembers(mod):
                if inspect.isclass(obj) and issubclass(obj, core.object.table.Table) and (obj.__module__ == 'app.table'):
                    try:
                        tab = obj()
                        Session.database.table_compile(tab)
                        Session.database.commit()
                    except:
                        Application.logexception('syncschem') 
                        res = False           

        except:
            Application.logexception('syncschem')
            res = False

        return res

    @staticmethod
    def _check_loop():
        try:
            sched = Application.instance['scheduler_enabled']
            if sched:
                core.application.Application.log('chckloop', 'I', core.language.label('Task scheduler enabled'))

            while not Application._thd_check_exit:
                if sched:
                    core.utility.proxy.Proxy.su_invoke('app.codeunit.ScheduledTask', 'dispatch')

                time.sleep(2)

        except:
            Application.logexception('chckloop')

    @staticmethod
    def start_servers():
        """
        Start servers and process pools
        """
        try:
            Session.connect()
            core.utility.proxy.Proxy.su_invoke('app.codeunit.SessionManagement', 'server_start')

            Application.process_pool = core.process.ProcessPool(Application.instance['min_processes'], Application.instance['max_processes'])
            Application.process_pool.start()

            core.utility.proxy.Reloader.start()

            Application._thd_check = threading.Thread(target=Application._check_loop)
            Application._thd_check.start()

            # after this Tornado loop will block execution
            if Application.instance['webserver_enabled']:
                core.webserver.WebServer.start()

        except:
            Application.logexception('strtsrvr')

    @staticmethod
    def stop_servers():
        """
        Stop servers and process pools
        """        
        try:
            core.webserver.WebServer.stop()

            if Application._thd_check:
                Application._thd_check_exit = True
                Application._thd_check.join()

            core.utility.proxy.Reloader.stop()

            if Application.process_pool:
                Application.process_pool.stop()
                Application.process_pool = None
               
        except:
            Application.logexception('strtsrvr')
