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

