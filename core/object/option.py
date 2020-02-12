import core.language
import core.utility.system


class OptionMeta(type):
    """
    Metaclass for option
    """
    def __init__(self, name, bases, dct):
        super().__init__(name, bases, dct)
        self._captions = {}
        self._options = {}
        self._modules = {}

        for k in self.__dict__:
            if k.startswith('_'):
                continue
        
            t = self.__dict__[k]
            if isinstance(t, tuple) and (len(t) >= 2) and isinstance(t[0], int) and isinstance(t[1], str):
                v = t[0]
                self._captions[v] = t[1]
                self._options[v] = k
                if len(t) == 3:
                    self._modules[v] = t[2]
                else:
                    self._modules[v] = core.utility.system.System.get_caller_modulename()
                setattr(self, k, v)
 

class Option(metaclass=OptionMeta):
    """
        Enumeration implementation

        Add options as class membmers
        NAME = VALUE, CAPTION

        ITEM_1 = 0, label('Item 1')
        ITEM_2 = 2, label('Item 2')
        ...

        First tuple item is the index and storage value
        Second item is the caption

        If first (zero) is empty, NAME = NONE, CAPTION = ''
        If CAPTION = '' will not be shown
        If CAPTION = ' ' will be shown
    """

    @classmethod
    def caption(cls, value):
        """
        Return caption of the option
        """
        if value in cls._captions:
            return core.language.label_module(cls._captions[value], cls._modules[value])
        else:
            return ''

    @classmethod
    def name(cls, value):
        """
        Return name of the option
        """        
        if value in cls._options:
            return cls._options[value]
        else:
            return ''

    @classmethod
    def options(cls, return_captions=True):
        """
        Return dictionary of defined options
        """        
        if return_captions:
            return cls._captions
        else:
            return cls._options


    


    