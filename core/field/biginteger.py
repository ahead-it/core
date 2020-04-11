from core.utility.convert import Convert
from core.field.field import Field, FieldType


class BigInteger(Field):
    """
    Field of type BIGINTEGER
    """    
    def __init__(self, name, caption):
        super().__init__()
        self.type = FieldType.BIGINTEGER
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)
        self.value = 0
        self.initvalue = 0
        self.xvalue = 0
        self.autoincrement = False

    def checkvalue(self, value):
        return int(value)
        