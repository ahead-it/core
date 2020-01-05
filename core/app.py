from core.utility.system import System
import core.application


class AppInfo:
    """
    App defines an application built on Core
    Multiple Apps defines a complete application; apps can extends each others
    Must be implemented in __init__ of app package and returned by __appinfo() function
    """
    def __init__(self):
        self.name = System.get_caller_appname()
        self.version = ''
        self.author = ''
        self.display_name = self.name

        if self.name == 'core':
            self.base_path = core.application.Application.base_path + 'core/'
        else:
            self.base_path = core.application.Application.base_path + self.name.replace('.', '/') + '/'


class AppMeta(type):
    def __getattribute__(self, name):
        appname = System.get_caller_appname()
        if appname in core.application.Application.apps:
            return object.__getattribute__(core.application.Application.apps[appname], name)
        else:
            return object.__getattribute__(self, name)


class App(metaclass=AppMeta):
    name = ''
    version = ''
    author = ''
    display_name = ''
    base_path = ''