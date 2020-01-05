import inspect
from core.language import label2
import core.utility.system


class Option:
    """
        Enumeration implementation

        Add members as class tuples
        NAME = VALUE, CAPTION

        ITEM_1 = 0, "Item 1"
        ITEM_2 = 2, "Item 2"
        ...

        First tuple item is the index and storage value
        Second item is the caption

        If first (zero) is empty, NAME = NONE, CAPTION = ''
        If CAPTION = '' will not be shown
        If CAPTION = ' ' will be shown
    """

    @classmethod
    def getname(cls, member):
        """
        Returns name of the member
        """
        m = inspect.getmembers(cls)
        for o in m:
            if o[1] == member:
                return o[0]
        return ""

    @classmethod
    def getcaption(cls, member):
        """
        Returns caption of the member
        """
        modname = core.utility.system.System.get_modulename(inspect.getfile(cls))
        return label2(member[1], modname)

    @classmethod
    def getvalue(cls, member):
        """
        Returns value of the membmer
        """
        return member[0]

    @classmethod
    def getoptions(cls):
        """
        Returns dict with all members
        Key is value
        Value is tuple
        """
        result = dict()
        m = inspect.getmembers(cls)
        for o in m:
            if (not o[0].startswith("_")) and isinstance(o[1], tuple):
                result[o[1][0]] = o[1]

        return result
