import core.object.page
from core.control.control import Control


class SubPage(Control):
    """
    Implements the subpage
    """    
    
    def __init__(self, parent, pagecls, caption=''):
        super().__init__(parent)
        self.caption = caption
        self.subpage = pagecls()

    def _onrender(self, obj):
        obj['subpage'] = self.subpage._render()
        obj['subpage']['caption'] = self.caption

