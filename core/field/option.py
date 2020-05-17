from core.utility.convert import Convert
from core.field.field import Field, FieldType
from core.utility.system import error
from core.language import label
import core.object.option


class Option(Field):
    """
    Field of type OPTION
    """    
    def __init__(self, name, caption, optclass):
        super().__init__()
        
        self.type = FieldType.OPTION
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(self.name)
        self._testvalue = 0
        self._optclass = optclass
        self._hasformat = True

        if not issubclass(optclass, core.object.option.Option):
            error(label('Invalid option class \'{0}\''.format(optclass)))

        self._options = optclass.options()
        if not self._options:
            error(label('Field \'{0}\' has no options defined'.format(self.caption)))

        for opt in self._options:
            self.value = opt
            self.initvalue = self.value
            self.xvalue = self.value
            break

    def checkvalue(self, value):
        if not isinstance(value, int):
           error(label('Value \'{0}\' is not valid for \'{1}\''.format(value, self.caption)))

        return value

    def format(self, value):
        if (value > 0) and (value < len(self._options)):
            return self._options[value]
        else:
            return 0

    def evaluate(self, strval):
        for opt in self._options:
            if self._options[opt].lower() == strval.lower():
                return opt

        try:
            opt = int(strval)
            if (opt > 0) and (opt < len(self._options)):
                return opt
        except:
            pass

        error(label('Value \'{0}\' is not valid for \'{1}\''.format(strval, self.caption)))