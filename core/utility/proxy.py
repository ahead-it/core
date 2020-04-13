import importlib
import hashlib
import inspect
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.language import label
import core.utility.system
import core.application
import core.object.unit
import core.object.codeunit
import core.object.table
import core.session


_allowed_types = ['codeunit', 'page', 'query', 'report', 'table']


class InvalidUnitException(Exception):
    """
    Invalid unit was called
    """
    def __init__(self, unitname):
        super().__init__(label('Invalid unit \'{0}\''.format(unitname)))


class ReloaderHandler(FileSystemEventHandler):
    """
    Handles reloading of modified files
    """
    def __init__(self):
        super().__init__()
        self.hashes = {}

    def on_created(self, event):
        self.reload(event.src_path)

    def on_modified(self, event):
        self.reload(event.src_path)

    def on_moved(self, event):
        self.reload(event.dest_path)

    def reload(self, path):
        if not path.endswith('.py'):
            return

        try:
            modname = core.utility.system.System.get_modulename(path)
        
            f = open(path, 'rb')
            content = f.read()
            f.close()

            if not content:
                return

            sha = hashlib.sha1()
            sha.update(content)
            hash = sha.hexdigest()

            if modname in self.hashes:
                if self.hashes[modname] == hash:
                    return

            self.hashes[modname] = hash
            
            core.application.Application.log('reloader', 'I', 'Reloading module \'{0}\''.format(modname))
            core.application.Application.process_pool.notify_reload(modname)

        except:
            core.application.Application.logexception('reloader')


class Reloader():
    _observer = None

    @staticmethod
    def start():
        """
        Start reloader module
        """
        if core.application.Application.base_path == '':
            return

        if core.application.Application.process_pool is None:
            return

        Reloader._observer = Observer()
        Reloader._observer.schedule(ReloaderHandler(), core.application.Application.base_path + 'app', recursive=True)
        Reloader._observer.start()
    
    @staticmethod
    def stop():
        """
        Stop the reloader module
        """
        if Reloader._observer is not None:
            Reloader._observer.stop()
            Reloader._observer = None

    @staticmethod
    def reload_module(modulename):
        if not modulename.startswith('app.'):
            return

        if modulename not in sys.modules:
            return
            
        importlib.reload(sys.modules[modulename])


class Proxy:
    """
    Dynamically load and handles unit
    """
    def __init__(self, unitname=None, obj=None):
        if unitname is not None:
            parts = unitname.split('.')
            if (len(parts) != 3) or \
                (parts[0] != 'app') or \
                (parts[1] not in _allowed_types):
                raise InvalidUnitException(unitname)

            mod = importlib.import_module(parts[0] + '.' + parts[1])
            if not hasattr(mod, parts[2]):
                raise InvalidUnitException(unitname)

            self.object_class = getattr(mod, parts[2])
            if not issubclass(self.object_class, core.object.unit.Unit):
                raise InvalidUnitException(unitname)

            self.unitname = parts[0] + '.' + parts[1]
            self.classname = parts[2]

        else:
            self.unitname = ''
            self.classname = ''

        self.object = obj # type: core.object.unit.Unit        

    def create(self):
        """
        Create the object
        """
        self.object = self.object_class()
        return self.object

    def is_public(self, method):
        """
        Returns True if object is decorated with @PublicMethod
        """
        if '_ispublic' in method.__dict__:
            return method.__dict__['_ispublic']
        else:
            return False

    def invoke(self, methodname, *args, **kwargs):
        """
        Invoke a method in the object
        """
        if not hasattr(self.object, methodname):
            raise Exception('Method \'{0}\' does not exists in \'{1}\''.format(methodname, self.classname))

        method = getattr(self.object, methodname)

        if (not core.session.Session.authenticated) and (not self.is_public(method)):
            raise Exception('Unauthorized access to method \'{0}\' in \'{1}\''.format(methodname, self.classname))
        
        return method(*args, **kwargs)

    @staticmethod
    def get_units(unittype=''):
        """
        Get all units available in symbols
        """
        if (unittype > '') and (unittype not in _allowed_types):
            raise Exception(label('Invalid unit type \'{0}\''.format(unittype)))

        if unittype > '':
            types = [unittype, ]
        else:
            types = _allowed_types

        res = []

        for t in types:
            mod = importlib.import_module('app.' + t)
            for name, obj in inspect.getmembers(mod):
                if not inspect.isclass(obj):
                    continue
                if not issubclass(obj, core.object.unit.Unit):
                    continue
                if (unittype == 'table') and (not issubclass(obj, core.object.table.Table)):
                    continue

                res.append(obj)
        
        return res
        
    @staticmethod
    def su_create(unitname):
        """
        Try create an object for administrative purpose
        """
        try:
            parts = unitname.split('.')
            mod = importlib.import_module(parts[0] + '.' + parts[1])
            cla = getattr(mod, parts[2])
            if issubclass(cla, core.object.unit.Unit):
                return cla()
        except:
            pass

    @staticmethod
    def su_invoke(obj, methodname, *args, **kwargs):
        """
        Try create an object method for administrative purpose
        """
        try:
            if isinstance(obj, str):
                obj = Proxy.su_create(obj)
            method = getattr(obj, methodname)
            return method(*args, **kwargs)
        except:
            pass
