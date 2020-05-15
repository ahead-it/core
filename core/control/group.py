import core.object.page
from core.control.control import Control


class Group(Control):
    """
    Implements the group
    """    
    
    def __init__(self, parent, caption=''):
        super().__init__(parent)
        self.caption = caption

    def _onrender(self, obj):
        obj['caption'] = self.caption
