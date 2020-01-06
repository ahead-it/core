from typing import List
import pyodbc
import core.database.server
import core.object.option
import core.object.table
import core.session
import core.application
from core.language import label
from core.field.field import Field, FieldType


class SqlServer(core.database.server.Server):
    """
    Defines a generic server class for database
    """
    def __init__(self):
        super().__init__()
        self._conn: pyodbc.Connection = None

    def connect(self):
        dsn = 'DRIVER={ODBC Driver 17 for SQL Server};'
        dsn += 'SERVER=' + self.host + ';'
        dsn += 'DATABASE=' + self.db_name +';'
        if self.login > '':
            dsn += 'UID=' + self.login + ';PWD=' + self.password + ';'
        else:
            dsn += 'Trusted_Connection=yes;'
        dsn += 'APP=Core ' + core.application.Application.instance['display_name']

        self._conn = pyodbc.connect(dsn, autocommit=False)

    def disconnect(self):
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def get_connectionid(self):
        return self.query('SELECT @@SPID AS [spid]')[0]['spid']

    def _execute(self, sql, parameters: list = None):
        self._statement_begin(sql, parameters)

        try:
            if not parameters:
                cur = self._conn.execute(sql)
            else:
                cur = self._conn.execute(sql, parameters)
        finally:        
            self._statement_end()

        return cur

    def execute(self, sql, parameters: list = None):
        cur = self._execute(sql, parameters)
        return cur.rowcount

    def query(self, sql, parameters: list = None):
        cur = self._execute(sql, parameters)

        res = []
        while True:
            row = cur.fetchone()
            if not row:
                break

            line = {}
            i = 0
            for col in cur.description:
                colname = col[0]
                line[colname] = row[i]
                i += 1
            res.append(line)

        return res

    def _list_fields(self, fields: List[Field], prefix=''):
        res = ''
        comma = False
        for field in fields:
            if comma:
                res += ', '
            comma = True
            res += prefix + '[' + field.sqlname + ']'
        return res

    def _get_fieldtype(self, field: Field):
        res = ''
        if field.type == FieldType.CODE:
            res += 'nvarchar(' + str(field.length) + ') NOT NULL'

        elif field.type in [FieldType.INTEGER]:
            res += 'int'
            if field.autoincrement:
                res += ' IDENTITY(1,1)'
            res += ' NOT NULL'

        elif field.type in [FieldType.OPTION]:
            res += 'int NOT NULL'

        else:
            raise Exception(label('Unknown field type \'{0}\''.format(FieldType.getcaption(field.type))))

        return res
                
    def _process_table(self, table: core.object.table.Table):
        sql = 'SELECT TOP 1 NULL FROM sysobjects WHERE (xtype = ?) AND (name = ?)'
        if self.query(sql, ['U', table._sqlname]):
            sql = 'SELECT c.is_identity, c.max_length, t.name AS typename, c.precision, c.scale, '
            sql += 'c.name, c.is_nullable FROM sys.objects o, sys.columns c, sys.types t '
            sql += 'WHERE (o.name = ?) AND (o.type = ?) AND (c.object_id = o.object_id) AND '
            sql += '(c.system_type_id = t.system_type_id) AND (c.user_type_id = t.user_type_id)'

            tab = self.query(sql, [table._sqlname, 'U'])

            todelete = []
            toadd = []
            tochange = []

            for field in table._fields:
                ok = False
                for row in tab:
                    if row['name'] == field.sqlname:
                        newdef = self._get_fieldtype(field)
                        curdef = row['typename']
                        if row['typename'] == 'nvarchar':
                            curdef += '(' + str(int(row['max_length'] / 2)) + ')'
                        if row['is_identity'] == 1:
                            curdef += ' IDENTITY(1,1)'
                        if row['is_nullable'] == 0:
                            curdef += ' NOT NULL'

                        if newdef != curdef:
                            tochange.append(field)

                        ok = True
                        break
                
                if not ok:
                    toadd.append(field)

            for row in tab:
                if row['name'] == 'timestamp':
                    continue

                ok = False
                for field in table._fields:
                    if row['name'] == field.sqlname:
                        ok = True
                        break
            
                if not ok:
                    todelete.append(row)

            for field in toadd:
                sql = 'ALTER TABLE [' + table._sqlname + '] ADD '
                sql += '[' + field.sqlname + '] ' + self._get_fieldtype(field) 
                sql += ' CONSTRAINT [' + field.sqlname + '$DEF] DEFAULT '
                if field.type in [FieldType.CODE]:
                    sql += '\'\''
                elif field.type in [FieldType.INTEGER, FieldType.OPTION]:
                    sql += '0'
                self.execute(sql)

                sql = 'ALTER TABLE [' + table._sqlname + '] '
                sql += 'DROP CONSTRAINT [' + field.sqlname + '$DEF]'
                self.execute(sql)

            for row in todelete:
                sql = 'ALTER TABLE [' + table._sqlname + '] '
                sql += 'DROP COLUMN [' + row['name'] + ']'
                self.execute(sql)

            for field in tochange:
                sql = 'ALTER TABLE [' + table._sqlname + '] '
                sql += 'ALTER COLUMN [' + field.sqlname + '] '
                sql += self._get_fieldtype(field)
                self.execute(sql)

        else:
            sql = 'CREATE TABLE [' + table._sqlname + '] ('
            for field in table._fields:
                sql += '[' + field.sqlname + '] ' + self._get_fieldtype(field) + ', '
            sql += '[timestamp] timestamp'
            sql += ')'
            self.execute(sql)

    def _process_primarykey(self, table: core.object.table.Table):
        sql = 'SELECT c.name FROM sys.objects o, sys.indexes i, sys.index_columns x, sys.columns c '
        sql += 'WHERE (o.name = ?) AND (o.type = ?) AND (o.object_id = i.object_id) AND (i.name = ?) AND '
        sql += '(x.object_id = o.object_id) AND (x.index_id = i.index_id) AND (c.object_id = o.object_id) AND '
        sql += '(c.column_id = x.column_id) ORDER BY x.key_ordinal'

        tab = self.query(sql, [table._sqlname, 'U', table._sqlname + '$PK'])
        curpk = ''
        for row in tab:
            curpk += row['name'] + ', '

        newpk = ''
        for fld in table._primarykey:
            newpk += fld.sqlname + ', '

        if curpk == newpk:
            return

        if curpk > '':
            sql = 'ALTER TABLE [' + table._sqlname + '] '
            sql += 'DROP CONSTRAINT [' + table._sqlname + '$PK]'
            self.execute(sql)

        if newpk > '':
            sql = 'ALTER TABLE [' + table._sqlname + '] '
            sql += 'ADD CONSTRAINT [' + table._sqlname + '$PK] '
            sql += 'PRIMARY KEY ('
            sql += self._list_fields(table._primarykey)
            sql += ')'
            self.execute(sql)

    def table_compile(self, table: core.object.table.Table):
        if not table._primarykey:
            raise Exception(label('Table \'{0}\' has not primary key'.format(table._caption)))

        self._process_table(table)

        self._process_primarykey(table)

    def from_sqlvalue(self, field: Field, value):
        res = None
        if field.type in [FieldType.CODE, FieldType.INTEGER]:
            res = value

        elif field.type == FieldType.OPTION:
            res = core.object.option.Option.getoptions()[value]

        else:
            raise Exception(label('Unknown field type \'{0}\''.format(FieldType.getcaption(field.type))))

        return res

    def to_sqlvalue(self, field: Field, value):
        res = None
        if field.type in [FieldType.CODE, FieldType.INTEGER]:
            res = value

        elif field.type == FieldType.OPTION:
            res = core.object.option.Option.getvalue(value)

        else:
            raise Exception(label('Unknown field type \'{0}\''.format(FieldType.getcaption(field.type))))

        return res

    def _set_rowversion(self, table: core.object.table.Table):
        table._rowversion = self.query('SELECT @@DBTS [dbts]')[0]['dbts']
            
    def table_insert(self, table: core.object.table.Table):
        pars = []
        places = []

        identity_field = None
        identity_insert = False
        fields = []
        for field in table._fields:
            if field.type in [FieldType.INTEGER]:
                if field.autoincrement:
                    identity_field = field
                    if field.value == 0:
                        continue
                    else:
                        identity_insert = True

            fields.append(field)
            places.append('?')
            pars.append(self.to_sqlvalue(field, field.value))

        sql = 'INSERT INTO [' + table._sqlname + '] ('
        sql += self._list_fields(fields)
        sql += ') VALUES ('
        sql += ', '.join(places)
        sql += ')'

        if identity_insert:
            self.execute('SET IDENTITY_INSERT [' + table._sqlname + '] ON')

        self.execute(sql, pars)
        self._set_rowversion(table)

        if identity_insert:
            self.execute('SET IDENTITY_INSERT [' + table._sqlname + '] OFF')
        elif identity_field is not None:
            identity_field.value = self.query('SELECT @@IDENTITY AS [id]')[0]['id']

    def table_modify(self, table: core.object.table.Table):
        pars = []

        fields = []
        for field in table._fields:
            if field in table._primarykey:
                continue
            if field.value == field.xvalue:
                continue
            fields.append(field)

        if not fields:
            return

        sql = 'UPDATE [' + table._sqlname + '] SET '

        comma = False
        for field in fields:
            if comma:
                sql += ', '
            comma = True
            sql += '[' + field.sqlname + '] = ?'
            pars.append(self.to_sqlvalue(field, field.value))

        sql += ' WHERE '
        sql += self._get_wherepk(table, pars)

        n = self.execute(sql, pars)
        if n != 1:
            table._error_concurrency()
        self._set_rowversion(table)

    def table_delete(self, table: core.object.table.Table):
        pars = []
        sql = 'DELETE FROM [' + table._sqlname + '] WHERE '
        sql += self._get_wherepk(table, pars)

        n = self.execute(sql, pars)
        if n != 1:
            table._error_concurrency()

    def _get_wherepk(self, table: core.object.table.Table, pars, with_timestamp=True):
        sql = ''

        comma = False
        for field in table._primarykey:
            if comma:
                sql += ' AND '
            comma = True
            sql += '([' + field.sqlname + '] = ?)'
            pars.append(self.to_sqlvalue(field, field.value))

        if with_timestamp:
            sql += ' AND ([timestamp] <= ?)'
            pars.append(table._rowversion)

        return sql

    def _table_findset(self, table: core.object.table.Table, size, nextset, ascending, pk):
        pars = []
        sql = 'SELECT TOP ' + str(size) + ' '

        for field in table._fields:
            sql += '[' + field.sqlname + '], '

        sql += '[timestamp] FROM [' + table._sqlname + ']'

        where = []
        if pk:
            i = 0
            for field in table._primarykey:
                where.append('([' + field.sqlname + '] = ?)')
                pars.append(self.to_sqlvalue(field, pk[i]))
                i += 1
                
        elif nextset:
            k = len(table._currentkey)
            l = k
            wn = []
            for i in range(0, k):
                ws = []
                for j in range(0, l):
                    field = table._currentkey[j]
                    op = ('>' if ascending else '<') if j == (l - 1) else '='
                    ws.append('([' + field.sqlname + '] ' + op + ' ?)')
                    pars.append(self.to_sqlvalue(field, field.value))

                wn.append('(' + ' AND '.join(ws) + ')')
                l -= 1

            where.append('(' + ' OR '.join(wn) + ')')

        if where:
            sql += ' WHERE ' + ' AND '.join(where)

        if not pk:
            sql += ' ORDER BY '
            comma = False
            for field in table._currentkey:
                if comma:
                    sql += ', '
                comma = True
                sql += '[' + field.sqlname + ']'
                if not ascending:
                    sql += ' DESC'

        return self.query(sql, pars)

    def table_get(self, table: core.object.table.Table, pk):
        return self._table_findset(table, 1, False, False, pk)

    def table_findset(self, table: core.object.table.Table):
        return self._table_findset(table, self.dataset_size, False, table._ascending, None)

    def table_nextset(self, table: core.object.table.Table):
        return self._table_findset(table, self.dataset_size, True, table._ascending, None)

    def table_findfirst(self, table: core.object.table.Table):
        return self._table_findset(table, 1, False, table._ascending, None)

    def table_findlast(self, table: core.object.table.Table):
        return self._table_findset(table, 1, False, not (table._ascending ^ False), None)

    def table_loadrow(self, table: core.object.table.Table, row: dict):
        for field in table._fields:
            field.value = self.from_sqlvalue(field, row[field.sqlname])
        
        table._rowversion = row['timestamp']