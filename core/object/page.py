from typing import List, Dict
from core.object.unit import Unit
from core.object.unit import UnitType
from core.control.control import Control
from core.utility.client import Client
import core.session


class Page(Unit):
    """
    Defines a page for user interaction
    """
    def __init__(self):
        super().__init__()
        self._type = UnitType.PAGE
        self._controls = []  # type: List[Control]
        self._allcontrols = {} # type: Dict[str, Control]
        self._init()
        self._init_check()

        for m in self.__dict__:
            a = getattr(self, m)
            if issubclass(type(a), Control):
                a._codename = m

    def run(self):
        """
        Render a page into the client
        """
        self._register()
        obj = Client.sendrcv(self._render())
        print(obj)        

    def _render(self):
        """
        Internal rendering
        """
        page = {
            'id': self._id,
            'name': self._name,
            'caption': self._caption,
            'controls': []
        }

        for c in self._controls:
            page['controls'].append(c.render())

        return page

    def _ctlinvoke(self, controlid, method, **kwargs):
        """
        Invoke method of a control
        """
        ctl = self._allcontrols[controlid]
        fun = getattr(ctl, method)
        return fun(**kwargs)
    
    def _pageinvoke(self, method, **kwargs):
        """
        Invoke method of page
        """
        if hasattr(self, method):
            fun = getattr(self, method)
            return fun(**kwargs)