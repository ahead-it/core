import core.object.page
from core.control.control import Control


class UserCenter(Control):
    """
    Implements user center button
    """    

    def __init__(self, parent):
        super().__init__(parent)
        self.username = ''
    
    def _onrender(self, obj):
        obj['username'] = self.username