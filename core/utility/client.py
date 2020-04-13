import core.session
import core.process
from core.language import label


class ClientNotSupportedException(Exception):
    """
    Method invalid for this kind of client
    """
    def __init__(self):
        super().__init__(label('Client \'{0}\' not supported'.format(core.session.Session.type)))


class Client():
    """
    Contains utility specific for the client
    """

    @staticmethod
    def send(message):
        """
        Send a message to client 
        """        
        if core.session.Session.type not in ['web', 'socket']:
            raise ClientNotSupportedException()

        core.process.Control.send(message)

    @staticmethod
    def sendrecv(message):
        """
        Send a message to client and wait for response
        """        
        if core.session.Session.type not in ['socket']:
            raise ClientNotSupportedException()

        return core.process.Control.sendrecv(message)

    @staticmethod
    def save_auth_token(expireat):
        """
        Tells client to save authentication token
        """
        msg = {
            'action': 'saveauthtoken',
            'token': core.session.Session.auth_token,
            'expireat': expireat
        }

        Client.send(msg)

    @staticmethod
    def destroy_auth_token():
        """
        Tells client to destroy authentication token
        """
        msg = {
            'action': 'delauthtoken'
        }

        Client.send(msg)

    @staticmethod
    def message(message, title=None):
        msg = {
            'action': 'message',
            'message': message,
            'title': title
        }

        Client.send(msg)

    @staticmethod
    def confirm(message, default=False, title=None):
        msg = {
            'action': 'confirm',
            'message': message,
            'default': default,
            'title': title
        }

        return Client.sendrecv(msg)        
