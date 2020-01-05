from datetime import datetime
import core.object.table
import core.field.field
import core.session
import core.application


class Server():
    """
    Defines a generic server class for database
    """
    def __init__(self):
        self.host = ''
        self.login = ''
        self.password = ''
        self.db_name = ''
        self.dataset_size = 0
        self._stmtstart = None
        self._stmtsql = None
        self._stmtpars = None

    def connect(self):
        """
        Connect to database
        """

    def disconnect(self):
        """
        Disconnect from database
        """

    def get_connectionid(self):
        """
        Returns connection id
        """

    def begin_transaction(self):
        """
        Starts a new transaction
        """
    
    def commit(self):
        """
        Commit current transaction
        """

    def rollback(self):
        """
        Rollback current transaction
        """

    def execute(self, sql, parameters: list = None):
        """
        Execute a command and returns affected rows
        """

    def query(self, sql, parameters: list = None):
        """
        Execute a query and returns all rows within a list of dict, key = field name, value = field value
        """

    def table_compile(self, table: core.object.table.Table):
        """
        Compile a table and its dependencies on database
        """        

    def table_insert(self, table: core.object.table.Table):
        """
        Insert a record in the database
        """

    def table_modify(self, table: core.object.table.Table):
        """
        Modify a record in the database
        """

    def table_delete(self, table: core.object.table.Table):
        """
        Delete a record in the database
        """        

    def table_findset(self, table: core.object.table.Table):
        """
        Select dataset from the database
        """

    def table_nextset(self, table: core.object.table.Table):
        """
        Select next dataset from the database (pagination)
        """

    def from_sqlvalue(self, field: core.field.field.Field, value):
        """
        Convert sql value to core value
        """

    def to_sqlvalue(self, field: core.field.field.Field, value):
        """
        Convert core value to sql value
        """

    def table_loadrow(self, table: core.object.table.Table, row: dict):
        """
        Load a datasetrow into table
        """

    def _statement_begin(self, sql, parameters):
        """
        Debug logging start parameters
        """
        if not core.application.Application.instance['db_debug']:
            return

        self._stmtstart = datetime.now()
        self._stmtsql = sql
        self._stmtpars = parameters

    def _statement_end(self):
        """
        Debug logging final
        """
        if not core.application.Application.instance['db_debug']:
            return

        duration = datetime.now() - self._stmtstart
        msg = 'execute ' + str(duration) + ' sql ' + self._stmtsql + ';'
        if self._stmtpars:
            msg += ' parameters'
            for p in self._stmtpars:
                msg += ' ' + str(p)

        core.application.Application.log('database', 'D', msg)    