from core.object.option import Option
from core.language import label


class FieldType(Option):
    """
    Defines the types of field supported by the application
    """
    def _options(self):
        self.NONE = 0, ''
        self.CODE = 1, label('Code')
        self.INTEGER = 2, label('Integer')
        self.OPTION = 3, label('Option')
        self.TEXT = 4, label('Text')


class Field():
    """
    Base field implementation
    """
    def __init__(self):
        self.name = ''
        self.caption = ''
        self.sqlname = ''
        self.type = FieldType().NONE
        self.value = None
        self.initvalue = None
        self.xvalue = None

    def __setattr__(self, key, value):
        handled = False
        if (key in ['value', 'initvalue', 'xvalue']) and hasattr(self, key):
            value = self.checkvalue(value)

        if not handled:
            super().__setattr__(key, value)

    def init(self):
        """
        Reset the field value to initial value
        """
        self.value = self.initvalue
        self.xvalue = self.initvalue

    def checkvalue(self, value):
        """
        Check or adjust the value according to field type, returns adjusted value
        """
        return value
        