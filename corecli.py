import sys
import argparse
import os
import signal
from pylint import lint
import core
import importlib
from core import *
from core.compiler import Compiler, Merger
from core.webserver import WebServer


def generate_texts(appname):
    Application.initialize()
    if not appname in Application.apps:
        print('Application \'{0}\' not found'.format(appname))
        return

    cmp = Compiler(Application.apps[appname])
    cmp.generate_textcatalog()
    print('Text catalog for \'{0}\' has been generated.'.format(appname))

def generate_symbols():
    Application.initialize()
    m = Merger()

    for app in Application.apps:
        if app == 'core':
            continue
        
        c = Compiler(Application.apps[app])
        c.find_symbols()
        m.add_symbols(c.symbols)
        m.add_types(c.types)

    m.generate_symbols()        
    print('Symbols has been generated.')

def check_code(path):
    for root, dirs, files in os.walk(path):
        if not root.endswith('/'):
            root += '/'

        for f in files:
            if f.endswith(".py"):
                lint.Run(['--errors-only', root + f], do_exit=False)

    print('Source code check done.')

def sync_schema(inst, mode):
    Application.initialize()
    Application.load_instance(inst)
    Session.connect()
    if Application.synchronize_schema():
        print('Schema synchronization done.')    
    else:
        print('Schema synchronization done with errors.')    

def signal_exit(sign, frame):
    Application.stop_servers()

def start_webserver(inst):
    Application.initialize()
    Application.load_instance(inst)
    
    signal.signal(signal.SIGINT, signal_exit)   
    Application.start_servers()

def install_service(inst):
    Application.initialize()
    Application.load_instance(inst)

    cla = Application.base_path + 'core.winservice.WindowsService'

    win32serviceutil.InstallService(cla, Application.instance['service_name'], Application.instance['service_display'], exeArgs=inst)  
    print('Windows service installed.') 

def uninstall_service(inst):
    Application.initialize()
    Application.load_instance(inst)

    win32serviceutil.RemoveService(Application.instance['service_name'])
    print('Windows service uninstalled.') 

if __name__ == '__main__':
    print(r'''
          _                    _    _____               
    /\   | |                  | |  / ____|              
   /  \  | |__   ___  __ _  __| | | |     ___  _ __ ___ 
  / /\ \ | '_ \ / _ \/ _` |/ _` | | |    / _ \| '__/ _ \
 / ____ \| | | |  __/ (_| | (_| | | |___| (_) | | |  __/
/_/    \_\_| |_|\___|\__,_|\__,_|  \_____\___/|_|  \___|

Ahead Core (v {0})
Powered by Python {1}
Copyright ahead.it 2019-2020
'''.format(core.__appinfo().version, sys.version))

    parser = argparse.ArgumentParser()
    parser.add_argument('--text', help='generate text catalogs', metavar='APPNAME')
    parser.add_argument('--check', help='check source code', metavar='PATH')
    parser.add_argument('--sym', help='generate symbols', action='store_true')
    parser.add_argument('--schema', help='synchronize database schema', choices=['check', 'force'])
    parser.add_argument('--instance', help='instance name')
    parser.add_argument('--log', help="show log on console", choices=['E', 'W', 'I', 'D'], nargs='+')
    parser.add_argument('--start', help='start web server', action='store_true')
    parser.add_argument('--run', help='run codeunit method with specified arguments', metavar='CODEUNIT', nargs='+')
    
    if sys.platform == 'win32':
        import win32serviceutil
        parser.add_argument('--install', help='install service for ths specified instance', metavar='INSTANCE')
        parser.add_argument('--uninstall', help='uninstall service', metavar='INSTANCE')

    args = parser.parse_args()
    
    if not args.log:
        args.log = ['E', 'W', 'I']

    Application._cli_loglevel = args.log

    if args.text:
        generate_texts(args.text)

    elif args.check:
        check_code(args.check)

    elif args.sym:
        generate_symbols()

    elif args.schema and args.instance:
        sync_schema(args.instance, args.schema)

    elif args.start and args.instance:
        start_webserver(args.instance)

    elif args.install:
        install_service(args.install)

    elif args.uninstall:
        uninstall_service(args.uninstall)
        
    else:
        parser.print_help()
