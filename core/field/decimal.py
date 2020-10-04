import decimal
from core.utility.convert import Convert
from core.field.field import Field, FieldType


class Decimal(Field):
    """
    Field of type DECIMAL
    """    
    def __init__(self, name, caption):
        super().__init__()
        self.type = FieldType.DECIMAL
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)
        self.value = decimal.Decimal(0)
        self.initvalue = self.value
        self.xvalue = self.value
        self._testvalue = self.value
        self._hasformat = True

    def checkvalue(self, value):
        if isinstance(value, float):
            return decimal.Decimal(str(value))
        else:
            return decimal.Decimal(value)        

    def serialize(self, value):
        return str(value)

    def deserialize(self, value):
        return decimal.Decimal(value)

    def format(self, value):
        return str(value).replace('.', ',')  # FIXME local settings

    def evaluate(self, strval):
        try:
            return Convert.strtodecimal(strval)
        except:
            raise Exception('Value \'{0}\' is not valid for \'{1}\''.format(strval, self.caption))
