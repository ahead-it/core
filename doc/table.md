# Table
Table are high level objects that wraps physical table on a database. Table contains fields and must define a primary key.

```python
from core import *


class Customer(Table):
    def _init(self):
        self._name = 'Customer'
        self._caption = label('Customer')
        
        self.no = field.Code('No.', label('No.'), 20)
        self.name = field.Text('Name', label('Name'), 50)

        self._setprimarykey(self.no)
```
## Fields
These field types are defined:
* `Code` string value, without leading and trailing spaces,
always in uppercase
* `Text` string value
* `Integer` integer value
* `BigInteger` big integer value
* `Option` value related to Option class
* `Date` value representing a date
* `Time` value representing a time
* `DateTime` value representing a date/time
* `Boolean` true or false value
* `Decimal` fixed decimal value

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
Tables are sorted by default by their primary keys.

To change sorting:
```python
cust = Customer()
cust.setcurrentkey(cust.name)
cust.ascending(false)
if cust.findfirst():
    print(label('Last customer is \'{0}\''.format(cust.name.value)))
```
* `setcurrentkey` accepts one or more field to sort (primary key is always added at the end of the sorting)
* `ascending` set orders up-bottom, bottom-up

## Filters
Table start without filters, `reset` remove all filters and set
default sorting key.

To filter for a specific value or range:
```python
cust = Customer()
cust.name.setrange('John')
if not cust.isempty():
    print(label('John exists'))
```
* `setrange` accepts three different calling
  * without parameters, removes any filter from the field
  * with a single parameter search for the value (equal comparison)
  * with two parameters search between the values (min/max)

To filter for a custom expression:
```python
cust = Customer()
cust.name.setfiler('John|*ike*|{0}', 'Bill')
if cust.findfirst():
    print(label('Customer \'{0}\' found'.format(cust.name.value)))
```
* `setfilter` accepts various parameter
  * a string expression with `|` logical OR operator, `&` logical AND operator, parenthesis, `*` wildcard LIKE operator, `<>=` equal, greater and lower operator, `..` range operator (`A..Z` between, `..Z` lower or equal than, `A..` greater or equal than)
  * a placeholder for a specific value passed as parameter `{0}`, `{1}` and so on

Filters can be set as various level with `setfilterlevel` function.

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
        self.postcode = field.Code('Post Code', label('Post code'), 10)
        ...
        
    def _oninsert(self):
        self.createdatetme = datetime.now()

    def _postcode_onvalidate(self):
        postmgmt = codeunit.PostCodeManagement()
        postmgmt.check(self.postcode.value)
```

# Fields
## Option
Here's the syntax to define a `field.Option`:

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
        self.documenttype = field.Option('Document Type', label('Document type'), SalesHeaderType)
        ...
```
