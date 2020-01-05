from typing import Dict, List
from core.object.unit import Unit
from core.object.unit import UnitType
from core.field.field import Field
from core.utility.convert import Convert
import core.session


class Table(Unit):
    """
    Define a physical table on the database
    """
    def __init__(self):
        super().__init__()
        self._type = UnitType.TABLE
        self._primarykey = [] # type: List[Field]
        self._indexes = {} # type: Dict[str, List[Field]]        
        self._init()
        self._init_check()
        
        self._currentkey = [] # type: List[Field]
        self._ascending = True

        self._currentrow = -1
        self._dataset = None
        self._rowversion = None
        self._sqlname = Convert.to_sqlname(self._name)

        self._fields = [] # type: List[Field]
        self._fieldnames = [] # type: List[str]
        for m in self.__dict__:
            a = getattr(self, m)
            if issubclass(type(a), Field):
                self._fields.append(a)
                self._fieldnames.append(m)

        self.setcurrentkey()

    def __setattr__(self, key, value):
        handled = False
        if hasattr(self, key):
            a = getattr(self, key)
            if issubclass(type(a), Field):
                a.value = value
                handled = True

        if not handled:
            super().__setattr__(key, value)

    def ascending(self, value: bool):
        """
        Set sorting in ascending or descending mode
        """
        self._ascending = value

    def setcurrentkey(self, *fields):
        """
        Set the current key of the table
        """
        self._currentkey.clear()

        for field in fields:
            self._currentkey.append(field)

        for field in self._primarykey:
            if field not in self._currentkey:
                self._currentkey.append(field)

    def _setprimarykey(self, *fields):
        """
        Set the primary key of the table
        """
        self._primarykey.clear()
        for field in fields:
            self._primarykey.append(field)

    def _addindex(self, name, *fields):
        """
        Define a new index for the table
        """
        self._indexes[name] = []
        for field in fields:
            self._indexes[name].append(field)
        
    def init(self):
        """
        Initialize all fields
        """
        for field in self._fields:
            field.init()

    def _accept_changes(self):
        """
        Set xvalue equal to value after database operation
        """
        for field in self._fields:
            field.xvalue = field.value
    
    def insert(self, run_trigger=False):
        """
        Insert the record
        """
        if run_trigger:
            self._oninsert()

        core.session.Session.database.table_insert(self)
        self._accept_changes()

    def _oninsert(self):
        """
        Event before insertion
        """

    def _raise_emptyerror(self):
        raise Exception('FIXME')

    def findset(self, error_ifempty=True):
        """
        Select a set of rows based on current key and filters
        """
        self._dataset = core.session.Session.database.table_findset(self)
        self._currentrow = -1
        if len(self._dataset) > 0:
            return True
        elif error_ifempty:
            self._raise_emptyerror()
        else:
            return False

    def reset(self):
        """
        Remove filter from the table and reset the key to primary key
        """
        self.setcurrentkey()

    def read(self):
        """
        Read one row from dataset, if none returns false
        """
        self._currentrow += 1
        if self._currentrow >= len(self._dataset):
            self._currentrow = 0
            self._dataset = core.session.Session.database.table_nextset(self)
            if len(self._dataset) == 0:
                return False

        core.session.Session.database.table_loadrow(self, self._dataset[self._currentrow])
        self._accept_changes()
        return True

    def findfirst(self, error_ifempty=True):
        """
        Get first record from table
        """
        self._dataset = core.session.Session.database.table_findfirst(self)
        self._currentrow = -1
        if len(self._dataset) > 0:
            return self.read()
        elif error_ifempty:
            self._raise_emptyerror()
        else:
            return False

    def findlast(self, error_ifempty=True):
        """
        Get first record from table
        """
        self._dataset = core.session.Session.database.table_findlast(self)
        self._currentrow = -1
        if len(self._dataset) > 0:
            return self.read()
        elif error_ifempty:
            self._raise_emptyerror()
        else:
            return False
        
