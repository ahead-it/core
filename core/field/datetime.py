from datetime import datetime
from core.utility.convert import Convert
from core.field.field import Field, FieldType
from core.utility.system import error
from core.language import label


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

    def checkvalue(self, value):
        if (value is not None) and (not isinstance(value, datetime)):
            error(label('Value \'{0}\' is not valid for \'{1}\''.format(value, self.caption)))
            
        return value
        