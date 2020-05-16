import core.object.page
from core.control.control import Control


class Repeater(Control):
    """
    Implements the repeater
    """    
    
    def __init__(self, parent, caption=''):
        super().__init__(parent)
        self.caption = caption
        self._page._islist = True

    def _onrender(self, obj):
        obj['caption'] = self.caption