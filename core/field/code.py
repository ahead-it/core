from core.utility.convert import Convert
from core.field.field import Field, FieldType
from core.utility.system import error
from core.language import label


class FieldCode(Field):
    """
    Field of type CODE
    """    
    def __init__(self, name, caption, length):
        super().__init__()
        self.type = FieldType().CODE
        self.length = length
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)
        self.value = ''
        self.initvalue = ''
        self.xvalue = ''

    def checkvalue(self, value):
        value = value.strip()
        value = value.upper()
        if len(value) > self.length:
            error(label('Value of \'{0}\' cannot be longer than {1}'.format(self.name, self.length)))
        return value
        