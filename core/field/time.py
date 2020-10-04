from datetime import time, datetime
from core.utility.convert import Convert
from core.field.field import Field, FieldType
from core.utility.system import error
from core.language import label


class Time(Field):
    """
    Field of type TIME
    """    
    def __init__(self, name, caption):
        super().__init__()
        self.type = FieldType.TIME
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)
        self.value = None
        self.initvalue = None
        self.xvalue = None
        self._testvalue = None
        self._hasformat = True

    def checkvalue(self, value):
        if (value is not None) and (not isinstance(value, time)):
            error(label('Value \'{0}\' is not valid for \'{1}\''.format(value, self.caption)))
            
        return value

    def serialize(self, value):
        if value is None:
            return None
        else:
            return value.strftime('%H:%M:%S')

    def deserialize(self, value):
        if value is None:
            return None
        else:
            return datetime.strptime(value, '%H:%M:%S').time()

    def format(self, value):
        if value is None:
            return ''
        else:
            return value.strftime('%H:%M:%S')   # FIXME local settings

    def evaluate(self, strval):
        try:
            return Convert.strtotime(strval)
        except:
            raise Exception('Value \'{0}\' is not valid for \'{1}\''.format(strval, self.caption))