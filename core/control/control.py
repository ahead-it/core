import uuid
from typing import List
import core.object.page


class Control:
    """
    Implements a generic user control
    """    
    def __init__(self, parent):
        self._parent = parent
        self._page = None  # type: core.object.page.Page
        self._codename = ''        
        self.id = str(uuid.uuid4())
        self.visible = True
        self._controls = []  # type: List[Control]

        if issubclass(type(parent), core.object.page.Page):
            self._page = parent  # type: core.object.page.Page
            self._parent._controls.append(self)

        elif issubclass(type(parent), Control):
            self._page = parent._page  # type: core.object.page.Page
            self._parent._controls.append(self)

        if self._page is not None:
            self._page._allcontrols[self.id] = self

    def move_first(self):
        """
        Move this control as first in the parent
        """
        self._parent._controls.remove(self)
        self._parent._controls.insert(0, self)
        
    def render(self):
        """
        Render itself
        """
        if not self.visible:
            return None

        ctl = {
            'id': self.id,
            'type': self.__class__.__name__,
            'controls': []
        }

        for c in self._controls:
            ctl['controls'].append(c.render())

        self._onrender(ctl)

        return ctl

    def _onrender(self, obj):
        """
        Render event to be inherited
        """ 