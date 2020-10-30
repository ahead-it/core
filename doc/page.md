# Page
Pages are object that allows user to interact with Core. Pages are available only through websocket and user interface must be implemented by client.

```python
from core import *


class Welcome(Page):
    def _init(self):
        self._name = 'Welcome'
        self._caption = label('Welcome Page')

        if appctr := control.AppCenter(self):
            if actarea := control.ActionArea(appctr):
                if actcust := control.Action(actarea, label('Custom')):
                    if acterrs := control.Action(actcust, label('Error Pages'), 'fa-exclamation-triangle'):
                        self.error1 = control.Action(acterrs, label('Error 1'))
             
    def _error1_click(self):
        if Client.confirm('Continue?'):
            Client.message('Continue YES')        
        else:
            Client.message('BREAK')                
```

A page is made by multiple controls. Each control can contains other controls and so on.

When a control is added as member of the page, it's possible to define its specific method.

## Display 
There are three display mode:

* `run` the page is shown as popup or a window (default)
* `runtask` the page is shown as main content of the client
* `runmodal` the page is shown as popup or a window in modal way
(code is suspended until the close)

## Triggers
Following triggers are raised:

* `_onopen` before the page is shown
* `_onqueryclose` before the page is closed (return False to cancel)
* `_onclose` after the page is closed
* `_onafterinitrec` after the new record is initialized
* `_onaftergetdata` after the record is fetched from database

## Magic properties
* `_parent` if the page is shown as subpage contains the parent object

## Magic methods
* `_ctlinvoke(controlid, method, args)` invoke specified method in the control identified by ID passing arguments
* `_getdata(offset, limit, sorting, filters)` returns data limited to specified rows, with sorting and filters applied
* `_selectrows(rows)` select rows in the dataset (empty array for new rows)
* `_delete()` delete selected rows
* `_close(mandatory)` closes gracefully or not the page
* `_setrecord(rec)` change the record of the page with new one

## Controls
Core defines several widgets that are rendered by the client in the proper way (web, mobile client, desktop client...).

Each control exposes one or more methods that can be subscribed in the page as `_codename_method(params)`.

* [Control List](controls.md)