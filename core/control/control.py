import uuid
from typing import List
import core.object.page


class Control():
    """
    Implements a generic user control
    """    
    def __init__(self, parent):
        self._parent = parent
        self._codename = ''        
        self.id = str(uuid.uuid4())
        self.controls = []  # type: List[Control]

        self._page = None # type: core.object.page.Page
        if issubclass(type(parent), core.object.page.Page):
            self._page = parent
            self._parent._controls.append(self)

        elif issubclass(type(parent), Control):
            self._page = parent.page
            self._parent.controls.append(self)

        if self._page is not None:
            self._page._allcontrols[self.id] = self
        
    def render(self):
        """
        Render itself
        """
        ctl = {
            'id': self.id,
            'type': self.__class__.__name__,
            'controls': []
        }

        for c in self.controls:
            ctl['controls'].append(c.render())

        return ctl

        