import core.object.page
from core.control.control import Control


class Search(Control):
    """
    Implements search 
    """    
    
    def search(self, what):
        """
        Handles search by the user
        """
        return self._page._pageinvoke('_' + self._codename + '_search', what)