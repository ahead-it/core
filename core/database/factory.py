import core.database.server
import core.database.sqlserver
from core.language import label


class ServerFactory:
    @staticmethod
    def CreateServer(instance) -> core.database.server.Server:
        if instance['db_type'] == 'sqlserver':
            res = core.database.sqlserver.SqlServer()
        else:
            raise Exception(label('Unsupported database type \'{0}\''.format(instance['db_type'])))

        res.host = instance['db_host']
        res.login = instance['db_login']
        res.password = instance['db_password']
        res.db_name = instance['db_name']
        res.dataset_size = instance['dataset_size']
        return res