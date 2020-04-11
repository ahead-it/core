from datetime import date, datetime, time, timedelta

from core.application import Application
from core.app import App, AppInfo
from core.session import Session
from core.language import label

from core.object.unit import Unit, UnitType
from core.object.option import Option
from core.object.codeunit import Codeunit
from core.field.field import FieldType
from core import field
from core.object.table import Table
from core.object.page import Page
from core import control

from core.utility.convert import Convert
from core.utility.system import System, error, commit
from core.utility.client import Client

from core.object.attributes import PublicMethod

def __appinfo():
    app = AppInfo()
    app.display_name = 'Core'
    app.version = '1.0.20005.0'
    app.author = 'ahead.it'
    return app
    