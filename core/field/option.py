from core.utility.convert import Convert
from core.field.field import Field, FieldType
from core.object.option import Option
from core.utility.system import error
from core.language import label


class FieldOption(Field):
    """
    Field of type OPTION
    """    
    def __init__(self, name, caption, optclass: Option):
        super().__init__()
        self.type = FieldType.OPTION
        self.option_class = optclass
        self.name = name
        self.caption = caption
        self.sqlname = Convert.to_sqlname(name)

        opts = optclass.getoptions()
        if not opts:
            error(label('Field \'{0}\' has no options defined'.format(name)))

        for opt in opts:
            self.value = opts[opt]
            self.initvalue = self.value
            self.xvalue = self.value
            break

    def checkvalue(self, value):
        pass

    