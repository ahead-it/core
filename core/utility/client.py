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
    def save_auth_token(daysvalid):
        """
        Tells client to save authentication token
        """
        if core.session.Session.type not in ['web']:
            raise ClientNotSupportedException()

        msg = {
            'action': 'saveauthtoken',
            'token': core.session.Session.auth_token,
            'days': daysvalid
        }

        core.process.Control.send(msg)

    @staticmethod
    def destroy_auth_token():
        """
        Tells client to destroy authentication token
        """
        if core.session.Session.type not in ['web']:
            raise ClientNotSupportedException()

        msg = {
            'action': 'delauthtoken'
        }

        core.process.Control.send(msg)

    @staticmethod
    def sendrcv(message):
        """
        Send a message to client and wait for response
        """        
        if core.session.Session.type not in ['socket']:
            raise ClientNotSupportedException()

        msg = {
            'action': 'send',
            'message': message
        }

        core.process.Control.send(msg)

        obj = core.process.Control.recv()
        return obj

    @staticmethod
    def message(message, title=None):
        msg = {
            'type': 'message',
            'message': message,
            'title': title
        }

        Client.sendrcv(msg)

    @staticmethod
    def confirm(message, default=False, title=None):
        msg = {
            'type': 'confirm',
            'message': message,
            'default': default,
            'title': title
        }

        res = Client.sendrcv(msg)        
