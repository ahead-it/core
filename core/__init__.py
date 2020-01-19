from core.application import Application
from core.app import App, AppInfo
from core.session import Session
from core.language import label

from core.object.unit import Unit, UnitType
from core.object.option import Option
from core.object.codeunit import Codeunit
from core.field.field import FieldType
from core.field.code import FieldCode
from core.field.option import FieldOption
from core.field.integer import FieldInteger
from core.object.table import Table

from core.utility.convert import Convert
from core.utility.system import System, error, commit

from core.object.attributes import PublicMethod

def __appinfo():
    app = AppInfo()
    app.display_name = 'Core'
    app.version = '1.0.20003.0'
    app.author = 'ahead.it'
    return app
    