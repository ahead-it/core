from core.utility.convert import Convert
from core.field.field import Field, FieldType
from core.language import label


class FieldBoolean(Field):
    """
    Field of type BOOLEAN
    """    
    def __init__(self, name, caption):
        super().__init__()
        self.type = FieldType.BOOLEAN
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)
        self.value = False
        self.initvalue = False
        self.xvalue = False

    def checkvalue(self, value):
        if isinstance(value, str):
            if value.lower() in ['1', 'true', label('true')]:
                return True
            else:
                return False
        elif isinstance(value, int):
            if value == 1:
                return True
            else:
                return False
        elif isinstance(value, bool):
            return value
        else:
            raise Exception('Value \'{0}\' is not valid for \'{1}\''.format(value, self.caption))
        