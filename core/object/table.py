from typing import Dict, List
from core.object.unit import Unit
from core.object.unit import UnitType
from core.field.field import Field
from core.utility.convert import Convert
from core.utility.proxy import Proxy
from core.language import label
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
        self._filterlevel = 0

        self._fields = [] # type: List[Field]
        for m in self.__dict__:
            a = getattr(self, m)
            if issubclass(type(a), Field):
                a._parent = self
                a._codename = m
                self._fields.append(a)

        self.setcurrentkey()

    def __setattr__(self, key, value):
        handled = False

        # user friendly value assignment
        if hasattr(self, key) and (not issubclass(type(value), Field)):
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
        self._rowversion = None
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

    def modify(self, run_trigger=False):
        """
        Modify the record
        """
        if run_trigger:
            self._onmodify()

        core.session.Session.database.table_modify(self)
        self._accept_changes()

    def _onmodify(self):
        """
        Event before modify
        """

    def delete(self, run_trigger=False):
        """
        Delete the record
        """
        if run_trigger:
            self._ondelete()

        core.session.Session.database.table_delete(self)

    def deleteall(self, run_trigger=False):
        """
        Delete all record matching the current filter
        """
        if run_trigger:
            if self.findset():
                while self.read():
                    self.delete(True)

        else:
            core.session.Session.database.table_deleteall(self)

    def _ondelete(self):
        """
        Event before deletion
        """

    def _error_concurrency(self):
        """
        Concurrency error
        """
        raise Exception(label('Another user has modified \'{0}\', restart the activity'.format(self._caption)))

    def _error_noprimarykey(self):
        """
        No primary key error
        """
        raise Exception(label('Table \'{0}\' has not primary key'.format(self._caption)))

    def error_notfound(self):
        """
        Record not found error
        """
        raise Exception('FIXME')

    def findset(self):
        """
        Select a set of rows based on current key and filters
        """
        return self._findset()

    def _findset(self, size=None, offset=None):
        """
        Select a set of rows based on current key and filters (with pagination)
        """
        self._dataset = core.session.Session.database.table_findset(self, size=size, offset=offset)
        self._currentrow = -1
        if len(self._dataset) > 0:
            return True
        else:
            return False

    def reset(self):
        """
        Remove filter from the table and reset the key to primary key
        """
        self.setcurrentkey()
        for f in self._fields:
            f.filters.clear()

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

    def count(self):
        """
        Returns the total number of rows
        """
        return core.session.Session.database.table_count(self)

    def isempty(self):
        """
        Returns true if the table is empty with current filters
        """
        return core.session.Session.database.table_isempty(self)

    def getposition(self):
        """
        Returns the current primary key of the record
        """
        val = []
        for f in self._primarykey:
            val.append(f.value)
        return val

    def get(self, *pk):
        """
        Get record by primary key
        """
        val = []
        i = 0
        for f in self._primarykey:
            if len(pk) > i:
                val.append(pk[i])
            else:
                val.append(f.initvalue)
            i += 1

        self._dataset = core.session.Session.database.table_get(self, val)
        self._currentrow = -1
        if len(self._dataset) > 0:
            return self.read()
        else:
            return False

    def findfirst(self):
        """
        Get first record from table
        """
        self._dataset = core.session.Session.database.table_findfirst(self)
        self._currentrow = -1
        if len(self._dataset) > 0:
            return self.read()
        else:
            return False

    def findlast(self):
        """
        Get first record from table
        """
        self._dataset = core.session.Session.database.table_findlast(self)
        self._currentrow = -1
        if len(self._dataset) > 0:
            return self.read()
        else:
            return False

    def setfilterlevel(self, level):
        """
        Set filter level for new filters added to fields
        """
        self._filterlevel = level
        
    def rename(self, *newkey):
        """
        Change primary key of record raising rename trigger and ajusting related table
        """
        if not self._primarykey:
            self._error_noprimarykey()

        if len(self._primarykey) != len(newkey):
            raise Exception('New primary key mismatch')

        pknames = []
        for f in self._primarykey:
            pknames.append(f._codename)

        tables = Proxy.get_units('table')
        for t in tables:
            tab = t()
            for f in tab._fields:
                for r in f._relations:
                    to = r['to']() 
                    if self.__class__ is not to.__class__:
                        continue
                    
                    if r['field'] not in pknames:
                        continue

                    cf = getattr(self, r['field'])
                    idx = pknames.index(r['field'])

                    print('Change ' + tab._caption + ' field ' + f.caption + ' from ' + cf.value + ' to ' + newkey[idx])

