from datetime import date
from core.utility.convert import Convert
from core.field.field import Field, FieldType
from core.utility.system import error
from core.language import label


class FieldDate(Field):
    """
    Field of type DATE
    """    
    def __init__(self, name, caption):
        super().__init__()
        self.type = FieldType.DATE
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)
        self.value = None
        self.initvalue = None
        self.xvalue = None

    def checkvalue(self, value):
        if (value is not None) and (not isinstance(value, date)):
            error(label('Value \'{0}\' is not valid for \'{1}\''.format(value, self.caption)))
            
        return value
        