# Table
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
## Fields
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

## Selecting and modifying records
To insert a new record:
```python
cust = Customer()
cust.no = '6274'
cust.validate(name, 'My Customer')
cust.insert(True)
```
* `validate` calls validation trigger of field
* `insert` insert the record in the database calling table trigger

To get a record by primary key:
```python
cust = Customer()
if not cust.get('6274'):
    cust.error_notfound()
```
* `get` accepts primary key values as arguments
* `error_notfound` is a special error that raises a standard "not found" exception

To get the first record:
```python
cust = Customer()
if cust.findfirst()
    print(cust.name.value)
```
* `findfirst` select the first record in the table by current filters and sorting

To get the last record:
```python
cust = Customer()
if cust.findlast()
    print(cust.name.value)
```
* `findlast` select the first record in the table by current filters and sorting

To iterate through records:
```python
cust = Customer()
if cust.findset():
    while cust.read():
        print(cust.name.value)
```
* `findset` select the first available set of records in the table by current filters and sorting
* `read` goes on inside the dataset

To verify if table is empty or not:
```python
cust = Customer()
if cust.isempty():
    print(label('No customer found'))
```
* `isempty` returns true if table is empty

## Sorting
FIXME

## Filters
FIXME

## Triggers
Following triggers are raised:
* `_oninsert` before a record is inserted in the database
* `_onmodify` before a record is modified 
* `_ondelete` before a record is deleted
* `_onrename` before a record is renamed (change of the primary
key value)
* `_[fieldname]_onvalidate` before the validation of specified
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

    def _postcode_onvalidate(self):
        postmgmt = codeunit.PostCodeManagement()
        postmgmt.check(self.postcode.value)
```

# Fields
## FieldOption
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
