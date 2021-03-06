from typing import List, Dict, Callable, Optional
from core.object.unit import Unit
from core.object.unit import UnitType
from core.field import field
from core.control.control import Control
from core.control.contentarea import ContentArea
from core.control.actions import ActionArea, Action, ActionCategory
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
        self._fdataset = []
        self._selectedrows = [] 
        self._count = None
        self._insertallowed = True
        self._modifyallowed = True
        self._deleteallowed = True
        self._readonly = False
        self._islist = False
        self._opennew = False
        self._cardpage = None  # type: Callable[[], Page]
        self._parent = None  # type: core.object.page.Page
        self._applylink = None  # type: Callable[[core.object.table.Table], None]
            
        self.rec = None  # type: core.object.table.Table

        self._init()
        self._init_check()
        self._add_defaultactions()
        self._setrecord(self.rec)

        for m in self.__dict__:
            a = getattr(self, m)
            if issubclass(type(a), Control):
                a._codename = m

    def _setrecord(self, newrec):
        """
        Change record of the page with new one
        """
        self.rec = newrec

        self._allfields = self._fields
        if self.rec:
            self._allfields += self.rec._fields

        for id in self._allcontrols:
            ctl = self._allcontrols[id]
            if (ctl.__class__.__name__ == 'Field') and ctl.field:
                for f in self._allfields:
                    if ctl.field._codename == f._codename:
                        ctl.field = f

    def _getsubpages(self):
        """
        :rtype: list[Page]
        """
        res = []
        for c in self._allcontrols:
            ctl = self._allcontrols[c]
            if ctl.__class__.__name__ == 'SubPage':
                res.append(ctl.subpage)
        return res

    def _run(self):
        """
        Render a page into the client
        """
        self._onload()
        self._register()
        for p in self._getsubpages():
            p._onload()
            p._register()

        obj = self._render()
        obj['action'] = 'page'
        return obj

    def run(self):
        """
        Render a page into the client
        """
        obj = self._run()
        obj['display'] = 'window'
        Client.send(obj)

    def runtask(self):
        """
        Render a page into the client
        """
        obj = self._run()
        obj['display'] = 'content'
        Client.send(obj)

    def runmodal(self):
        """
        Render a page into the client
        """
        obj = self._run()
        obj['display'] = 'modal'
        # FIXME manage return value of modal
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

    def render(self):
        """
        Force client to redraw the page
        """
        msg = {
            'action': 'renderpage',
            'pageid': self._id,
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
            for p in self._getsubpages():
                if not p._onqueryclose():
                    return False

            if not self._onqueryclose():
                return False

        for p in self._getsubpages():
            p._onclose()
            p._unregister()

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
        qn = self.__class__.__qualname__
        qn = qn.split('.')

        page = {
            'id': self._id,
            'name': self._name,
            'classname': qn[0],
            'caption': self._caption,
            'controls': [],
            'readonly': self._readonly or (not self._modifyallowed)
        }

        for c in self._controls:
            page['controls'].append(c.render())

        dataset = []
        if self.rec is not None:
            dataset = self._getschema(self._allfields)

        page['schema'] = dataset

        return page

    def _getschema(self, fields):
        """
        Return record schema
        """
        schema = []

        for f in fields:
            itm = {
                'caption': f.caption,
                'codename': f._codename,
                'type': f.__class__.__name__,
                'hasformat': f._hasformat
            }

            if f.type == field.FieldType.OPTION:
                itm['options'] = []
                for v in f._options:
                    capt = f._options[v]
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
        cont_area = None
        for c in self._controls:
            if isinstance(c, ContentArea):
                cont_area = c
                break

        if cont_area is None:
            return

        act_area = None
        for c in cont_area._controls:
            if isinstance(c, ActionArea):
                act_area = c
                break

        if act_area is None:
            act_area = ActionArea(cont_area)

        recbtn = Action(act_area, label('Record'), Icon.DATA, ActionCategory.RECORD)
        recbtn.move_first()

        if self.rec:
            showins = False
            showmod = False
            showdel = self._deleteallowed and (not self._readonly)

            if self._islist:
                showins = self._insertallowed and (not self._readonly)
                showmod = self._modifyallowed and (not self._readonly)

                if self._cardpage:
                    card = self._cardpage()
                    showins |= card._insertallowed and (not card._readonly)
                    showmod |= card._modifyallowed and (not card._readonly)
                    showdel |= card._deleteallowed and (not card._readonly)

            if showins:
                self._newbtn = Action(recbtn, label('New'), Icon.NEW)

            if showmod:
                self._modbtn = Action(recbtn, label('Modify'), Icon.EDIT)

            if showdel:
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
        if self._cardpage:
            card = self._cardpage()
            card._opennew = True
            if self.rec:
                card._setrecord(self.rec)
                card.rec.init()
            card.run()

    def _modbtn_click(self):
        """
        Modify button
        """
        if not self._selectedrows:
            return

        if self._cardpage:
            card = self._cardpage()
            card.rec.setpkfilter(*self._getrowpk(self._selectedrows[0]))
            card.run()   

    def _delbtn_click(self):
        """
        Delete button
        """
        self._delete()         

    def _getdatarow(self, fields, format=False):
        """
        Returns current data row
        """
        line = []
        for f in fields:
            if format:
                if f._hasformat:
                    line.append(f.format(f.value))
                else:
                    line.append('')
            else:
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
        newfds = []
        for i in range(len(self._dataset)):
            if i not in self._selectedrows:
                newds.append(self._dataset[i])
                newfds.append(self._fdataset[i])

        self._dataset = newds
        self._fdataset = newfds

        msg = {
            'action': 'deleterows',
            'rows': self._selectedrows,
            'pageid': self._id,
        }
        Client.send(msg)

        self._selectedrows = []

    def _getdata(self, offset=0, limit=1, sorting=None, filters=None):
        """
        Returns data
        """
        self._dataset = []
        self._fdataset = []

        if self.rec is not None:
            if self._applylink:
                self._applylink(self.rec)

            if offset == 0:
                if self._islist:
                    self._count = self.rec.count()
                else:
                    self._count = 1

            if self._opennew and (self.rec._rowversion is None):
                self.rec.init()
                self._onafterinitrec()
                self._onaftergetdata()
                self._dataset.append(self._getdatarow(self._allfields))
                self._fdataset.append(self._getdatarow(self._allfields, True))

            else:
                if self.rec._findset(size=limit, offset=offset):
                    while (limit > 0) and self.rec.read():
                        self._onaftergetdata()
                        self._dataset.append(self._getdatarow(self._allfields))
                        self._fdataset.append(self._getdatarow(self._allfields, True))

                        limit -= 1

        else:
            self._onaftergetdata()
            self._dataset.append(self._getdatarow(self._allfields))
            self._fdataset.append(self._getdatarow(self._allfields, True))
            self._count = 1

        return {
            'dataset': self._dataset,
            'fdataset': self._fdataset,
            'count': self._count
        }

    def _getrowpk(self, index):
        """
        Locate current record to index with primary key 
        """
        pk = []
        i = 0
        for f in self._allfields:
            if f in self.rec._primarykey:
                pk.append(f.deserialize(self._dataset[index][i]))
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

    def _onafterinitrec(self):
        """
        Event after init record
        """

    def _onaftergetdata(self):
        """
        Event after get record
        """