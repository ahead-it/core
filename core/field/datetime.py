from datetime import datetime
from core.utility.convert import Convert
from core.field.field import Field, FieldType
from core.utility.system import error
from core.language import label
import core.session

class DateTime(Field):
    """
    Field of type DATETIME
    """    
    def __init__(self, name, caption):
        super().__init__()
        self.type = FieldType.DATETIME
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)
        self.value = None
        self.initvalue = None
        self.xvalue = None
        self._testvalue = None
        self._hasformat = True

    def checkvalue(self, value):
        if (value is not None) and (not isinstance(value, datetime)):
            error(label('Value \'{0}\' is not valid for \'{1}\''.format(value, self.caption)))
            
        return value

    def serialize(self, value):
        if value is None:
            return None
        else:
            if value.tzinfo is None:
                value = value.astimezone(core.session.Session.timezone)
            return value.strftime('%Y-%m-%d %H:%M:%S.%f%z')

    def deserialize(self, value):
        if value is None:
            return None
        else:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f%z')

    def format(self, value):
        if value is None:
            return ''
        else:
            return value.strftime('%d/%m/%Y %H:%M:%S')  # FIXME local settings

    def evaluate(self, strval):
        try:
            return Convert.strtodatetime(strval)
        except:
            raise Exception('Value \'{0}\' is not valid for \'{1}\''.format(strval, self.caption))