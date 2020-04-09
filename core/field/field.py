from typing import List
from core.object.option import Option
from core.language import label


class FieldType(Option):
    """
    Defines the types of field supported by the application
    """
    NONE = 0, ''
    CODE = 1, label('Code')
    INTEGER = 2, label('Integer')
    OPTION = 3, label('Option')
    TEXT = 4, label('Text')
    BIGINTEGER = 5, label('Big Integer')
    DECIMAL = 6, label('Decimal')
    DATE = 7, label('Date')
    DATETIME = 8, label('DateTime')
    BOOLEAN = 9, label('Boolean')


class FieldFilter():
    """
    Filter implementation
    """
    def __init__(self):
        self.level = 0
        self.type = ''
        self.min_value = None
        self.max_value = None
        self.value = None
        self.values = []


class Field():
    """
    Base field implementation
    """
    def __init__(self):
        self._codename = ''
        self._parent = None
        self._relations = []
        self.name = ''
        self.caption = ''
        self.sqlname = ''
        self.type = FieldType.NONE
        self.value = None
        self.initvalue = None
        self.xvalue = None
        self.filters = [] # type: List[FieldFilter]

    def __setattr__(self, key, value):
        handled = False
        if (key in ['value', 'initvalue', 'xvalue']) and hasattr(self, key):
            value = self.checkvalue(value)

        if not handled:
            super().__setattr__(key, value)

    def __add__(self, other):
        return self.value + self.checkvalue(other)

    def __radd__(self, other):
        return self.value + self.checkvalue(other)
        
    def __sub__(self, other):
        return self.value - self.checkvalue(other)

    def __rsub__(self, other):
        return self.value - self.checkvalue(other)

    def __eq__(self, other):
        return self.value == other 

    def __ne__(self, other):
        return self.value != other             

    def __lt__(self, other):
        return self.value < other             

    def __gt__(self, other):
        return self.value > other             

    def __le__(self, other):
        return self.value <= other             

    def __ge__(self, other):
        return self.value >= other             

    def init(self):
        """
        Reset the field value to initial value
        """
        self.value = self.initvalue
        self.xvalue = self.initvalue

    def checkvalue(self, value):
        """
        Check or adjust the value according to field type, returns adjusted value
        """
        return value
        
    def validate(self, value):
        """
        Assign value an trigger on validate method
        """
        self.value = value
        m = '_' + self._codename + '_onvalidate'
        if self._parent and hasattr(self._parent, m):
            a = getattr(self._parent, m)
            a()
            
    def related(self, to, field=None, when=None, filters=None):
        """
        Add a relation to other table
        
        to -- target table (class)
        field -- field to return (string)
        when -- conditions if relation is true (lambda returns tuple)
        filters -- filters applied to target (lamba called with table object returns tuple)
        """

        if field is None:
            tab = to()
            if not tab._primarykey:
                tab._error_noprimarykey()
            field = tab._primarykey[0]
            if field._codename == '':
                raise Exception('Field \'{0}\' in \'{1}\' has not codename'.format(field.caption, tab._caption))
            field = field._codename

        self._relations.append({
            "to": to,
            "field": field,
            "when": when,
            "filters": filters
        })

    def _getfilterlevel(self):
        """
        Return current filter level of parent table
        """
        if (self._parent is not None) and hasattr(self._parent, '_filterlevel'):
            return self._parent._filterlevel
        else:
            return 0

    def setfilter(self, expression, *values):
        """
        Add an expression filter
        """
        flt = FieldFilter()
        flt.type = 'expr'
        flt.level = self._getfilterlevel()
        flt.values = values
        self.filters.append(flt)

    def setrange(self, min=None, max=None):
        """
        Add or remove a simple filter to the field
        """
        if (min is None) and (max is None):
            fd = []
            for f in self.filters:
                if f.level == self._getfilterlevel:
                    fd.append(f)
            for f in fd:
                self.filters.remove(f)

        elif max is None:
            flt = FieldFilter()
            flt.type = 'equal'
            flt.level = self._getfilterlevel()
            flt.value = min
            self.filters.append(flt)

        else:
            flt = FieldFilter()
            flt.type = 'range'
            flt.level = self._getfilterlevel()
            flt.min_value = min
            flt.max_value = max
            self.filters.append(flt)
