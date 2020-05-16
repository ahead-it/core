import importlib
import uuid
from core.object.option import Option
from core.language import label
import core.session


class UnitType(Option):
    """
    Defines the types of Unit
    """
    NONE = 0, ''
    TABLE = 1, label('Table')
    CODEUNIT = 2, label('Codeunit')
    REPORT = 3, label('Report')
    PAGE = 4, label('Page')
    QUERY = 5, label('Query')


class Unit:
    """
    Defines an Unit
    Multiple units defines an app; each unit is identified by a UUID
    """
    def __init__(self):
        self._type = UnitType.NONE
        self._name = ""
        self._caption = ""
        self._id = str(uuid.uuid4())
        
    def _init(self):
        """
        Method to be overriden in child classes
        """

    def _init_check(self):
        """
        Assert default fields
        """
        if not self._name:
            qn = self.__class__.__qualname__
            if '.' in qn:
                qn = qn[:qn.find('.')]
            self._name = self.__module__ + '.' + qn
                    
        if not self._caption:
            self._caption = self._name

    def __reduce__(self):
        """
        Implement pickle for proxied objects
        """
        clsname = self.__class__.__qualname__
        p = clsname.find('__new__')
        if p > 0:
            clsname = clsname[0:p-1]

        state = {
            'modulename': self.__class__.__module__,
            'classname': clsname
        }

        members = [self.__class__.__dict__, self.__dict__] 
        keys = ['static', 'instance']
        for i in range(0, 2):
            state[keys[i]] = {}
            for m in members[i]:
                if m.startswith('__'):
                    continue

                attr = getattr(self, m)

                if callable(attr):
                    continue
                
                state[keys[i]][m] = attr

        return Unit._restore, (state, )

    @staticmethod
    def _restore(args):
        """
        Restore a pickle unit
        """
        mod = importlib.import_module(args['modulename'])
        cla = getattr(mod, args['classname'])
        obj = cla()
        for k in args['static']:
            setattr(cla, k, args['static'][k])
        for k in args['instance']:
            setattr(obj, k, args['instance'][k])    
        return obj

    def _register(self):
        """
        Register itself in session state
        """
        core.session.Session.objects[self._id] = self

    def _unregister(self):
        """
        Unregister itself from session state
        """
        if self._id in core.session.Session.objects:
            del core.session.Session.objects[self._id]


                