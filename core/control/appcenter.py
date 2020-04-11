import core.object.page
from core.control.control import Control


class AppCenter(Control):
    """
    Implements the main control that owns menu, actions, search and pages
    """    
    def search(self, what):
        """
        Handles search by the user
        """
        return self._page._pageinvoke('_' + self._codename + '_search', **{'what': what})
        
        