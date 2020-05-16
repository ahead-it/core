from datetime import datetime, timezone
import sys
import traceback
import core.application
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
       
