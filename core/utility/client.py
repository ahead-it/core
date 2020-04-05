import core.session
import core.process
from core.language import label
import uuid


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
        if core.session.Session.type not in ['web', 'socket']:
            raise ClientNotSupportedException()

        msg = {
            'action': 'saveauthtoken',
            'token': core.session.Session.auth_token,
            'days': daysvalid
        }

        core.process.Control.send(msg)

    @staticmethod
    def destroy_auth_token():
        if core.session.Session.type not in ['web', 'socket']:
            raise ClientNotSupportedException()

        msg = {
            'action': 'delauthtoken'
        }

        core.process.Control.send(msg)
