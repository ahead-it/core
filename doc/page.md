# Page
Pages are object that allows user to interact with Core. Pages are available only through websocket and user interface must be implemented by client.

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
## Fields
