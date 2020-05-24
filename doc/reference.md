# Core Language Reference

## Creating an app
In the `app` folder simply create a new subfolder with the
name of your app. Define a `__init__.py` file with the 
app information, example:

```python
from core import AppInfo


def __appinfo():
    app = AppInfo()
    app.display_name = 'My app'
    app.version = '1.0.19001.0'
    app.author = 'My Dream Team'
    return app
```

For the version use this convention `X.Y.Z.R`:
* `X` Major (for major changes)
* `Y` Minor (for minor changes)
* `Z` Build number (two digit of year followed by incremental 
build number)
* `R` Revision number (incremental number whithin the same build)

Python files are searched in all subfolder of app but suggested
structure is separating objects by types:
* `codeunit` 
* `table`
* `page`
* `query`
* `report`

## Default imports
For Core usage simply add at the top of the files:
```python
from core import *
from app import table, codeunit
```

## Option
Options are special enumerations that defines tuples as
class members with the first item as integer value, the second
item as caption (so translated).

```python
class SalesHeaderType(Option):
    QUOTE = 0, label('Quote')
    ORDER = 1, label('Order')
    INVOICE = 2, label('Invoice')
    RETURNORDER = 3, label('Return order')
    CREDITMEMO = 4, label('Credit memo')
    BLANKETORDER = 5, label('Blanket order')
```

## Unit
All objects derives from `Unit` class and must declare a name and a caption in 
the `_init` method:
```python
from core import *


class MathManagement(Codeunit):
    def _init(self):
        self._name = 'Math Management'
        self._caption = label('Math management')
```
Name could include spaces and must be human readable. Name
convention defines the first letter of each word in uppercase.
Caption is mostly equal to name but convention defines only
the first letter of the string in uppercase (such as text
usage in a normal phrase).

Each `Unit` can contains static or instance method or 
properties. 

## Codeunit
Codeunits are the most simple Core object type and contains
functions for other objects.

Example:
```python
from core import *


class MathManagement(Codeunit):
    def sum(self, a, b):
        return a + b
```

## Table
[Table reference](table.md)

## Page
[Page reference](page.md)

## Unit Extension
Each unit (codeunit, table, page...) can be extended. Core compiler creates proxy object
merging multiple units in a single usable class.

For example, define a codeunit `app/one/codeunit/mathmanagement.py`

```python
from core import *


class MathManagement(Codeunit):
    def sum(self, a, b):
        return a + b
```

Define the codeunit extension `app/two/codeunit/mathmanagement.py`
with a class that inherits the previous one:

```python
from core import *
import app.one.codeunit.mathmanagement

class MathManagement(app.one.codeunit.mathmanagement.Codeunit):
    def mul(self, a, b):
        return a * b
```

Run the symbol creation and then simply use the merged object:

```python
from core import *
from app import codeunit

class MyCodeunit(Codeunit):
    def mymethod(self, a, b):
        mm = MathManagement()
        return mm.sum(a, b) / mm.mul(a, b)

```

## Access control
### Public method
Public methods are served without authentication and are
identified by `@PublicMethod` decorator.
```python
from core import *

@PublicMethod
class MathManagement(Codeunit):
    def sum(self, a, b):
        return a + b
```