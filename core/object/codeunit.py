from core.object.unit import Unit
from core.object.unit import UnitType


class Codeunit(Unit):
    """
    Defines a unit with code only
    """
    def __init__(self):
        super().__init__()
        self._type = UnitType().CODEUNIT
        self._init()
        self._init_check()
        
    