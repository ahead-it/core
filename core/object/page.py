from typing import List, Dict
from core.object.unit import Unit
from core.object.unit import UnitType
from core.control.control import Control
from core.control.contentarea import ContentArea
from core.control.actions import ActionArea, Action
from core.utility.client import Client
from core.utility.system import getnone
from core.language import label
from core.utility.system import error
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
        self._selectedrows = [] 
        self._count = None
        self._insertallowed = True
        self._modifyallowed = True
        self._deleteallowed = True
        self._readonly = False
        self._cardPage = None

        self.rec = getnone() # type: core.object.table.Table
        
        self._init()
        self._init_check()
        self._add_defaultactions()

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

    def _add_defaultactions(self):
        """
        Add default action to page
        """
        contArea = None
        for c in self._controls:
            if isinstance(c, ContentArea):
                contArea = c
                break

        if contArea is None:
            return

        actArea = None
        for c in contArea._controls:
            if isinstance(c, ActionArea):
                actArea = c
                break

        if actArea is None:
            actArea = ActionArea(contArea)

        recbtn = Action(actArea, label('Record'), category='record')
        
        if (not self._readonly) and self._insertallowed:
            self._newbtn = Action(actArea, label('New'))

    def __newbtn_click(self):
        """
        New button
        """
        if self._cardPage:
            card = self._cardPage()
            card.rec.init()
            card.run()

    def _getdatarow(self):
        """
        Returns current data row
        """
        line = []
        for f in self.rec._fields:
            line.append(f.serialize(f.value))
        return line
    
    def _delete(self):
        """
        Delete selected rows
        """
        if not self._selectedrows:
            return

        if self.rec is None:
            return

        if not Client.confirm(label('Delete {0} {1}?'.format(len(self._selectedrows), self.rec._caption))):
            return

        for i in self._selectedrows:
            self._getrowbypk(i)
            self.rec.delete(True)

        self._selectedrows = []

    def _getdata(self, offset=0, limit=1, sorting=None, filters=None):
        """
        Returns data
        """
        self._dataset = []

        if self.rec is not None:
            if offset == 0:
                self._count = self.rec.count()

            if self.rec._findset(size=limit, offset=offset):
                while (limit > 0) and self.rec.read():
                    self._dataset.append(self._getdatarow())

                    limit -= 1

        else:
            self._count = 1

        return {
            'dataset': self._dataset,
            'count': self._count
        }

    def _getrowbypk(self, index):
        """
        Locate current record to index with primary key 
        """
        pk = []
        i = 0
        for f in self.rec._fields:
            if f in self.rec._primarykey:
                pk.append(self._dataset[index][i])
            i += 1
        
        self.rec.get(*pk)
        
    def _selectrows(self, rows):
        """
        Change current selection
        """ 
        if self._selectedrows != rows:
            self._selectedrows = rows

            if self.rec is not None:
                if not self._selectedrows:
                    self.rec.init()
                else:
                    self._getrowbypk(self._selectedrows[0])
                    
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