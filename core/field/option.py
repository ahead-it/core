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

        if not issubclass(optclass, core.object.option.Option):
            error(label('Invalid option class \'{0}\''.format(optclass)))

        opts = optclass.options()
        if not opts:
            error(label('Field \'{0}\' has no options defined'.format(self.caption)))

        for opt in opts:
            self.value = opt
            self.initvalue = self.value
            self.xvalue = self.value
            break

    def checkvalue(self, value):
        if not isinstance(value, int):
           error(label('Value \'{0}\' is not valid for \'{1}\''.format(value, self.caption)))

        return value

    