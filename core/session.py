import threading
import locale
import uuid
import os
import socket
import core.application
import core.database.server
import core.database.factory


class Session():
    """
    Define a session in the application server
    Each session is identified by an unqueidentifier; can be only a session for each process/thread
    Types of session:
        cli         running from console
        web         called from web (GET/POST, ex. webservice)
        socket      live connected through websocket
        batch       running batch from application server
    """    
    process_id = 0
    language_code = ''
    id = ''
    type = '' 
    hostname = ''
    database = None # type: core.database.server.Server
    db_id = None
    user_id = ''
    connected = False
    authenticated = False

    @staticmethod
    def initialize():
        Session.process_id = os.getpid()
        Session.language_code = locale.getdefaultlocale()[0]
        Session.id = str(uuid.uuid4())
        Session.type = 'cli' 
        Session.hostname = socket.gethostname()
        Session.database: core.database.server.Server = None
        Session.db_id = None
        Session.user_id = ''
        Session.connected = False
        Session.authenticated = False
        
    @staticmethod
    def connect():
        """
        Connect to instance and create db server
        """
        if Session.connected:
            return

        if 'db_type' not in core.application.Application.instance:
            return

        Session.database = core.database.factory.ServerFactory.CreateServer(core.application.Application.instance)
        Session.database.connect()      
        Session.connected = True  
        Session.db_id = Session.database.get_connectionid()
