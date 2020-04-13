import core.object.page
from core.control.control import Control


class Action(Control):
    """
    Implements action
    """   

    def __init__(self, parent, caption, icon=None):
        super().__init__(parent)

        self.caption = caption
        self.icon = icon
        self.description = None

    def _onrender(self, obj):
        obj['caption'] = self.caption
        if self.icon:
            obj['icon'] = self.icon
        if self.description: 
            obj['description'] = self.description

    def click(self):
        """
        Handles action click
        """
        return self._page._pageinvoke('_' + self._codename + '_click')


class ActionArea(Control):
    """
    Implements area containing actions
    """    


class ActionGroup(Control):
    """
    Implements group of actions
    """    
    def __init__(self, parent, caption):
        super().__init__(parent)

        self.caption = caption

    def _onrender(self, obj):
        obj['caption'] = self.caption


class ActionList(Control):
    """
    Implements area containing actions in list view
    """    
