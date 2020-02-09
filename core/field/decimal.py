from decimal import Decimal
from core.utility.convert import Convert
from core.field.field import Field, FieldType


class FieldDecimal(Field):
    """
    Field of type DECIMAL
    """    
    def __init__(self, name, caption):
        super().__init__()
        self.type = FieldType.DECIMAL
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)
        self.value = Decimal(0)
        self.initvalue = self.value
        self.xvalue = self.value

    def checkvalue(self, value):
        return self.convertvalue(value)
    
    def convertvalue(self, value):
        if isinstance(value, float):
            return Decimal(str(value))
        else:
            return Decimal(value)        