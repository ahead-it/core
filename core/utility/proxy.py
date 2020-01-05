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
        self._object_class = getattr(mod, parts[2])
        self._object = None

    def create(self):
        self._object = self._object_class()

    def invoke(self, method, **kwargs):
        method = getattr(self._object, method)
        return method(**kwargs)
