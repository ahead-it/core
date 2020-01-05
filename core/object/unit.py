import uuid
from core.object.option import Option
from core.language import label


class UnitType(Option):
    """
    Defines the types of Unit
    """
    NONE = 0, ''
    TABLE = 1, label("Table")
    CODEUNIT = 2, label("Codeunit")
    REPORT = 3, label("Report")
    PAGE = 4, label("Page")
    QUERY = 5, label("Query")


class Unit:
    """
    Defines an Unit
    Multiple units defines an app; each unit is identified by a UUID
    """
    def __init__(self):
        self._type = UnitType.NONE
        self._name = ""
        self._caption = ""
        self._id = str(uuid.uuid4())
        
    def _init(self):
        """
        Method to be overriden in child classes
        """

    def _init_check(self):
        """
        Assert default fields
        """
        if not self._name:
            qn = self.__class__.__qualname__
            self._name = self.__module__ + '.' + qn[:qn.find('.')]
        
        if not self._caption:
            self._caption = self._name