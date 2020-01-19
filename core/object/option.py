import inspect


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

    def __init__(self):
        self._options()

    def _options(self):
        """
        To be overriden to set options
        """

    def getoptname(self, member):
        """
        Returns name of the member
        """
        m = inspect.getmembers(self)
        for o in m:
            if o[1] == member:
                return o[0]
        return ""

    def getoptions(self):
        """
        Returns dict with all members
        Key is value
        Value is tuple
        """
        result = dict()
        m = inspect.getmembers(self)
        for o in m:
            if (not o[0].startswith("_")) and isinstance(o[1], tuple) and (o[0][0:1] == o[0][0:1].upper()):
                result[o[1][0]] = o[1]

        return result
