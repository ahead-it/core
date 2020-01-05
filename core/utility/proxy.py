import importlib
from core.language import label


class InvalidUnitException(Exception):
    def __init__(self, unitname):
        super().__init__(label('Invalid unit \'{0}\''.format(unitname)))

class Proxy:
    def __init__(self, unitname):
        parts = unitname.split('.')
        if (len(parts) != 3) or \
            (parts[0] != 'app') or \
            (parts[1] not in ['codeunit', 'page', 'query', 'report', 'table']):
            raise InvalidUnitException(unitname)

        mod = importlib.import_module(parts[0] + '.' + parts[1])
        if not hasattr(mod, parts[2]):
            raise InvalidUnitException(unitname)

        self.object_class = getattr(mod, parts[2])
        self.object = None
        self.unitname = parts[0] + '.' + parts[1]
        self.classname = parts[2]

    def create(self):
        self.object = self.object_class()

    def is_public(self, method):
        mod = importlib.import_module('app.map')
        funs = getattr(mod, 'functions')
        mn = self.unitname + '/' + self.classname + '.' + method
        if mn not in funs:
            return False
        if 'public' not in funs[mn]:
            return False
        return True

    def invoke(self, method, **kwargs):
        method = getattr(self.object, method)
        return method(**kwargs)
