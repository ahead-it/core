from typing import List, Dict
from core.object.unit import Unit
from core.object.unit import UnitType
from core.control.control import Control
from core.utility.client import Client
from core.utility.system import getnone
import core.session
import core.object.table


class Page(Unit):
    """
    Defines a page for user interaction
    """
    def __init__(self):
        super().__init__()
        self._type = UnitType.PAGE
        self._controls = []  # type: List[Control]
        self._allcontrols = {} # type: Dict[str, Control]
        self._dataset = []
        self._currentrow = None

        self.rec = getnone() # type: core.object.table.Table

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
        self._onload()
        self._register()
        obj = self._render()
        obj['action'] = 'page'
        Client.send(obj)

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

        dataset = []
        if self.rec is not None:
            for f in self.rec._fields:
                itm = {
                    'caption': f.caption,
                    'codename': f._codename,
                    'type': f.__class__.__name__
                }
                dataset.append(itm)
        page['dataset'] = dataset

        return page

    def _getdata(self, limit=1, sorting=None, filters=None):
        """
        Returns data
        """
        self._dataset = []
        if self.rec is not None:
            if self.rec.findset():
                while self.rec.read() and (limit > 0):
                    line = []
                    for f in self.rec._fields:
                        line.append(f.value)
                    self._dataset.append(line)
                    limit -= 1

        return self._dataset

    def _selectrow(self, row):
        """
        Change current row
        """ 
        if self._currentrow != row:
            self._currentrow = row

            if self.rec is not None:
                pk = []
                i = 0;
                for f in self.rec._fields:
                    if f in self.rec._primarykey:
                        pk.append(self._dataset[self._currentrow][i])
                    i += 1
                
                self.rec.get(*pk)

    def _ctlinvoke(self, controlid, method, *args, **kwargs):
        """
        Invoke method of a control
        """
        ctl = self._allcontrols[controlid]
        fun = getattr(ctl, method)
        return fun(*args, **kwargs)
    
    def _pageinvoke(self, method, *args, **kwargs):
        """
        Invoke method of page
        """
        if hasattr(self, method):
            fun = getattr(self, method)
            return fun(*args, **kwargs)

    def _onload(self):
        """
        Event before show
        """            