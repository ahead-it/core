import inspect
import core.application
import core.session


class System():
    """
    Contains utility specific to Core system
    """

    @staticmethod
    def get_modulename(path):
        """
        Get the name of the module starting from file path related to Core base path
        Example:
            BASE PATH       /core/path
            FILE PATH       /core/path/app/myapp/myfile.py
            MODULE NAME     app.myapp.myfile
        """
        if not hasattr(core, 'application'):
            return ''
        if core.application.Application.base_path == '':
            return ''
        fn = path.replace('\\', '/')
        fn = fn.replace('/', '.')

        l = len(core.application.Application.base_path)
        fn = fn[l:]

        if fn.endswith('.py'):
            return fn[:-3]
        elif fn.endswith('.pyc'):
            return fn[:-4]
        else:
            return fn

    @staticmethod
    def get_appname(modname):
        """
        Get the name of the app starting from module name
        Example:
            MODULE NAME     app.myapp.myfile
            APP NAME        app.myapp
        """
        n = modname.find('.')
        if n < 0:
            return ''
        seg1 = modname[:n]
        if seg1 == "core":
            return seg1
        n = modname.find('.', n + 1)
        if n < 0:
            return ''
        return modname[:n]

    @staticmethod
    def get_caller_class(stack=2):
        """
        Get caller class, none if outside class
        """
        frame = inspect.stack()[stack]
        if 'self' in frame[0].f_locals:
            return frame[0].f_locals['self'].__class__
        else:
            return None

    @staticmethod
    def get_caller_filename(stack=2):
        """
        Get caller filename
        """
        frame = inspect.stack()[stack]
        module = inspect.getmodule(frame[0])
        return module.__file__
       
    @staticmethod
    def get_caller_modulename(stack=2):
        """
        Get the Core module name of the caller
        """
        frame = inspect.stack()[stack]
        module = inspect.getmodule(frame[0])
        return System.get_modulename(module.__file__)

    @staticmethod
    def get_caller_appname():
        """
        Get the App name of the caller
        """
        modname = System.get_caller_modulename(3)
        return System.get_appname(modname)

def getnone():
    """
    Returns none (parser type hint fix)
    """
    none = None
    return none

def error(message=''):
    """
    Raise an exception with provided message
    """
    raise Exception(message)

def commit():
    """
    Commit to the database
    """
    if core.session.Session.database:
        core.session.Session.database.commit()

