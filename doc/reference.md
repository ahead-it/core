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
    app.enabled = True
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
Table are high level objects that wraps physical table on a database. Table contains fields and must define a primary key.

```python
from core import *


class Customer(Table):
    def _init(self):
        self._name = 'Customer'
        self._caption = label('Customer')
        
        self.no = FieldCode('No.', label('No.'), 20)
        self.name = FieldText('Name', label('Name'), 50)

        self._setprimarykey(self.no)
```
### Fields
These field types are defined:
* `FieldCode` string value, without leading and trailing spaces,
always in uppercase
* `FieldText` string value
* `FieldInteger` integer value
* `FieldBigInteger` big integer value
* `FieldOption` value related to Option class
* `FieldDate` value representing a date
* `FieldTime` value representing a time
* `FieldDateTime` value representing a date/time
* `FieldBoolean` true or false value
* `FieldDecimal` fixed decimal value

### Triggers
Following triggers are raised:
* `_oninsert` before a record is inserted in the database
* `_onmodify` before a record is modified 
* `_ondelete` before a record is deleted
* `_onrename` before a record is renamed (change of the primary
key value)
* `_onvalidate_[fieldname]` before the validation of specified
field

Example:
```python
class Customer(Table):
    def _init(self):
        ...
        self.postcode = FieldCode('Post Code', label('Post code'), 10)
        ...
        
    def _oninsert(self):
        self.createdatetme = datetime.now()

    def _onvalidate_postcode(self):
        postmgmt = codeunit.PostCodeManagement()
        postmgmt.check(self.postcode.value)
```

## Fields
### FieldOption
Here's the syntax to define a FieldOption:

```python
class SalesHeaderType(Option):
    QUOTE = 0, label('Quote')
    ORDER = 1, label('Order')
    INVOICE = 2, label('Invoice')
    RETURNORDER = 3, label('Return order')
    CREDITMEMO = 4, label('Credit memo')
    BLANKETORDER = 5, label('Blanket order')

class SalesHeader(Table):
    def _init(self):
        ...
        self.documenttype = FieldOption('Document Type', label('Document type'), SalesHeaderType)
        ...
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