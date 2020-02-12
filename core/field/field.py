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
        
    def convertvalue(self, value):
        """
        Convert value in the right type
        """
        return value

    def validate(self, value):
        """
        Assign value an trigger on validate method
        """
        self.value = value
        m = '_onvalidate_' + self._codename
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
