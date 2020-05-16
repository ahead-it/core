from typing import List, Dict, Callable, Optional
from core.object.unit import Unit
from core.object.unit import UnitType
from core.field import field
from core.control.control import Control
from core.control.contentarea import ContentArea
from core.control.actions import ActionArea, Action
from core.control.icon import Icon
from core.utility.client import Client
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
        self._allcontrols = {}  # type: Dict[str, Control]
        self._dataset = []
        self._selectedrows = [] 
        self._count = None
        self._insertallowed = True
        self._modifyallowed = True
        self._deleteallowed = True
        self._readonly = False
        self._cardPage = None  # type: Callable[[], Page]
            
        self.rec = None  # type: core.object.table.Table

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

    def setcaption(self, newcaption):
        """
        Change the caption at runtime
        """
        msg = {
            'action': 'changectlprop',
            'pageid': self._id,
            'property': 'caption',
            'value': newcaption
        }
        Client.send(msg)

    def update(self):
        """
        Refresh data in the client
        """
        msg = {
            'action': 'refreshpage',
            'pageid': self._id,
        }
        Client.send(msg)

    def _close(self, mandatory=False):
        """
        Client magic method to handle close
        """
        if not mandatory:
            if not self._onqueryclose():
                return False

        self._onclose()
        self._unregister()
        return True

    def close(self):
        """
        Close the page
        """
        if not self._onqueryclose():
            return

        msg = {
            'action': 'closepage',
            'pageid': self._id,
        }
        Client.send(msg)    

        self._onclose()
        self._unregister()

    def _onqueryclose(self):
        """
        Query if the page is closeable
        """
        return True

    def _onclose(self):
        """
        Closing event
        """

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
            dataset = self._getschema(self.rec)

        page['schema'] = dataset

        return page

    def _getschema(self, rec):
        """
        Return record schema
        """
        schema = []
        for f in rec._fields:
            itm = {
                'caption': f.caption,
                'codename': f._codename,
                'type': f.__class__.__name__
            }

            if f.type == field.FieldType.OPTION:
                itm['options'] = []
                opts = f._optclass.options()
                for v in opts:
                    capt = opts[v]
                    if capt:
                        itm['options'].append({
                            'value': v,
                            'caption': capt
                        })

            schema.append(itm)

        return schema

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

        recbtn = Action(actArea, label('Record'), Icon.DATA, category='record')
        recbtn.move_first()

        if (not self._readonly) and self.rec:
            if self._insertallowed:
                self._newbtn = Action(recbtn, label('New'), Icon.NEW)

            if self._modifyallowed:
                self._modbtn = Action(recbtn, label('Modify'), Icon.EDIT)

            if self._deleteallowed:
                self._delbtn = Action(recbtn, label('Delete'), Icon.DELETE)

        self._refbtn = Action(recbtn, label('Refresh'), Icon.REFRESH)

    def _refbtn_click(self):
        """
        Refresh button
        """
        self.update()

    def _newbtn_click(self):
        """
        New button
        """
        if self._cardPage:
            card = self._cardPage()
            card.rec.init()
            card.run()

    def _modbtn_click(self):
        """
        Modify button
        """
        if not self._selectedrows:
            return

        if self._cardPage:
            card = self._cardPage()
            card.rec.setpkfilter(*self._getrowpk(self._selectedrows[0]))
            card.run()   

    def _delbtn_click(self):
        """
        Delete button
        """
        self._delete()         

    def _getdatarow(self, rec):
        """
        Returns current data row
        """
        line = []
        for f in rec._fields:
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
            self.rec.get(*self._getrowpk(i))
            self.rec.delete(True)

        newds = []
        for i in self._dataset:
            if i not in self._selectedrows:
                newds.append(self._dataset[i])

        self._selectedrows = []
        self._dataset = newds

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
                    self._dataset.append(self._getdatarow(self.rec))

                    limit -= 1

        else:
            self._count = 1

        return {
            'dataset': self._dataset,
            'count': self._count
        }

    def _getrowpk(self, index):
        """
        Locate current record to index with primary key 
        """
        pk = []
        i = 0
        for f in self.rec._fields:
            if f in self.rec._primarykey:
                pk.append(self._dataset[index][i])
            i += 1
        
        return pk
        
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
                    self.rec.get(*self._getrowpk(self._selectedrows[0]))
                    
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
        if method.startswith('__'):
            method = method[1:]

        if hasattr(self, method):
            fun = getattr(self, method)
            return fun(*args, **kwargs)

    def _onload(self):
        """
        Event before show
        """            