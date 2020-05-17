from core.utility.convert import Convert
from core.field.field import Field, FieldType
from core.language import label


class Boolean(Field):
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
        self._testvalue = False
        self._hasformat = True

    def checkvalue(self, value):
        if isinstance(value, int):
            if value == 1:
                return True
            else:
                return False
        elif isinstance(value, bool):
            return value
        else:
            raise Exception('Value \'{0}\' is not valid for \'{1}\''.format(value, self.caption))

    def format(self, value):
        if value:
            return label('Yes')
        else:
            return label('No')

    def evaluate(self, strval):
        if strval.lower() in ['1', 'true', label('true').lower(), 'yes', label('yes').lower()]:
            return True
        else:
            return False
