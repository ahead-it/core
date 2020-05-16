import threading
import locale
import uuid
import os
import socket
from datetime import timezone
from dateutil import tz
from typing import Dict
import core.application
import core.object.unit
import core.database.server
import core.database.factory
import core.utility.proxy
import core.utility.system

class SessionData():
    """
    Contains in memory session data
    """
    def __init__(self):
        self.timezone = tz.tzlocal()
        self.language_code = locale.getdefaultlocale()[0]
        self.id = str(uuid.uuid4())
        self.type = 'cli' 
        self.user_id = ''
        self.auth_token = ''
        self.address = ''
        self.authenticated = False
        self.objects = {} # type: Dict[str, core.object.unit]


class SessionMeta(type):
    """
    Wraps SessionData for static object Session
    """
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        cls.data = SessionData()

    def __getattribute__(self, attr):
        if attr != 'data':
            if hasattr(self.data, attr):
                return getattr(self.data, attr)

        return super().__getattribute__(attr)
    
    def __setattr__(self, attr, value):
        if attr != 'data':
            if hasattr(self.data, attr):
                setattr(self.data, attr, value)

        super().__setattr__(attr, value)

    def initialize(self):
        """
        Create new container for session data and register itself in application
        """
        self.data = SessionData()


class Session(metaclass=SessionMeta):
    """
    Define a session in the application server
    Each session is identified by an unqueidentifier; can be only a session for each process/thread
    Types of session:
        cli         running from console
        web         called from web (GET/POST, ex. webservice)
        socket      live connected through websocket
        batch       running batch from application server
    """    
    process_id = os.getpid()
    hostname = socket.gethostname()
    database = None  # type: core.database.server.Server
    db_id = None
    connected = False

    timezone = None  # type: timezone
    language_code = ''
    id = ''
    type = '' 
    auth_token = ''
    address = ''
    user_id = ''
    authenticated = False
    objects = {}  # type: Dict[str, core.object.unit]

    @staticmethod
    def start():
        """
        Start session and assert validity of parameters
        """
        try:
            uid = uuid.UUID(Session.auth_token)
            Session.auth_token = str(uid)
        except:
            Session.auth_token = ''

        core.utility.proxy.Proxy.su_invoke('app.codeunit.SessionManagement', 'start')
        core.utility.system.commit()

    @staticmethod
    def stop():
        """
        Stop session
        """
        core.utility.proxy.Proxy.su_invoke('app.codeunit.SessionManagement', 'stop')
        core.utility.system.commit()
        
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
        Session.db_id = Session.database.get_connectionid()
        Session.connected = True  
        
    @staticmethod
    def disconnect():
        """
        Disconnect from db server
        """
        if Session.connected:
            Session.database.disconnect()
            Session.database = None
            Session.db_id = None
            Session.connected = False