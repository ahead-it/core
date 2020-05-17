from core.utility.convert import Convert
from core.field.field import Field, FieldType


class Integer(Field):
    """
    Field of type INTEGER
    """    
    def __init__(self, name, caption):
        super().__init__()
        self.type = FieldType.INTEGER
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)
        self.value = 0
        self.initvalue = 0
        self.xvalue = 0
        self._testvalue = 0
        self.autoincrement = False
        self._hasformat = True
        self.blankzero = False

    def checkvalue(self, value):
        return int(value)

    def format(self, value):
        if self.blankzero and (value == 0):
            return ''
        else:
            return str(value)

    def evaluate(self, strval):
        return int(strval)