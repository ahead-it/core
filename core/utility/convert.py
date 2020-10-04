from datetime import datetime, timezone, date, time
from decimal import Decimal
import sys
import traceback
import hashlib
import core.application
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.padding import PKCS7
import base64
from core.language import label


class RemoteError(Exception):
    """
    Defines an error raised in child process. In 'fmt_exception' the remote exception well formatted 
    with traceback.
    """
    def __init__(self, value):
        super().__init__(value['message'])
        self.fmt_exception = value


class Convert:
    """
    Contains useful function for formatting and converting
    """
    @staticmethod
    def to_sqlname(name):
        """
        Convert a name in SQL compliant name
        Allowed chars: alphabetic, numbers, parenthesis, dash and space
        """
        sqlname = ''
        for c in name:
            if (c >= 'A') and (c <= 'Z'):
                sqlname += c
            elif (c >= 'a') and (c <= 'z'):
                sqlname += c
            elif (c >= '0') and (c <= '9'):
                sqlname += c
            elif c in ['(', ')', '-', ' ']:
                sqlname += c
            else:
                sqlname += '_'

        return sqlname

    @staticmethod
    def formatexception(skip_trace=0):
        """
        Returns a dict of the last exception
        """
        exc = sys.exc_info()

        if isinstance(exc[1], RemoteError):
            return exc[1].fmt_exception

        traces = []
        frames = traceback.extract_tb(exc[2])
        if skip_trace > 0:
            frames = frames[skip_trace:]
        for frame in frames:
            fn = frame.filename
            fn = fn.replace('\\', '/')
            if (core.application.Application.base_path > '') and fn.startswith(core.application.Application.base_path):
                l = len(core.application.Application.base_path)
                fn = fn[l:]
            else:
                i = fn.rfind('/')
                fn = fn[i+1:]

            traces.append('in ' + fn + ' line ' + str(frame.lineno) + ' \'' + frame.line + '\'')

        return {
            'class': exc[0].__qualname__,
            'message': str(exc[1]),
            'trace': traces
        }

    @staticmethod
    def strtodecimal(strval):
        """
        Converts a string to Decimal type according to local settings
        """
        strval = strval.strip()
        if not strval:
            return Decimal('0')

        # FIXME local settings
        if ('.' in strval) and (',' in strval):
            strval = strval.replace('.', '')

        strval = strval.replace(',', '.')
        return Decimal(strval)

    @staticmethod
    def strtodate(strval):
        """
        Converts a string to Date type according to local settings
        """
        strval = strval.strip()
        if not strval:
            return None

        strval = strval.replace('/', '')
        strval = strval.replace('-', '')
        strval = strval.replace('.', '')

        # FIXME localsettins
        if len(strval) == 2:
            return date(datetime.now().year, datetime.now().month, int(strval))
        elif len(strval) == 4:
            return date(datetime.now().year, int(strval[2:4]), int(strval[0:2]))
        elif len(strval) == 6:
            return datetime.strptime(strval, '%d%m%y').date()
        elif len(strval) == 8:
            return datetime.strptime(strval, '%d%m%Y').date()
        else:
            raise ValueError()

    @staticmethod
    def strtotime(strval):
        """
        Converts a string to Time
        """
        strval = strval.strip()
        if not strval:
            return None

        strval = strval.replace('.', '')
        strval = strval.replace(':', '')

        if len(strval) == 2:
            return time(int(strval), 0, 0)
        elif len(strval) == 4:
            return time(int(strval[0:2]), int(strval[2:4]), 0)
        elif len(strval) == 6:
            return datetime.strptime(strval, '%H%M%S').date()
        else:
            raise ValueError()

    @staticmethod
    def strtodatetime(strval):
        """
        Converts a string to Date / Time
        """
        strval = strval.strip()
        if not strval:
            return None

        parts = strval.split(' ', 1)
        if len(parts) == 1:
            return datetime.combine(Convert.strtodate(parts[0]), time(0, 0, 0))
        else:
            return datetime.combine(Convert.strtodate(parts[0]), Convert.strtotime(parts[1]))

    @staticmethod
    def encryptstr(value, key):
        """
        Encrypt a string AES256-CBC-NOIV with SHA256 KEY-UTF8 value PKCS7 padded
        """
        key = hashlib.sha256(key.encode('utf8')).digest()
        cipher = Cipher(AES(key), CBC(bytearray(16)))
        encryptor = cipher.encryptor()
        padder = PKCS7(128).padder()
        data = padder.update(value.encode('utf8')) + padder.finalize()
        ct = encryptor.update(data) + encryptor.finalize()
        return base64.b64encode(ct).decode('utf8')

    @staticmethod
    def decryptstr(value, key):
        """
        Decrypt a string AES256-CBC-NOIV with SHA256 KEY-UTF8 value PKCS7 padded
        """
        data = base64.b64decode(value.encode('utf8'))
        key = hashlib.sha256(key.encode('utf8')).digest()
        cipher = Cipher(AES(key), CBC(bytearray(16)))
        decryptor = cipher.decryptor()
        dt = decryptor.update(data) + decryptor.finalize()
        unpadder = PKCS7(128).unpadder()
        txt = unpadder.update(dt) + unpadder.finalize()
        return txt.decode('utf8')
