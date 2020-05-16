import core.object.page
import core.field.field
from core.object.option import Option
from core.language import label
from core.control.control import Control


class FieldType:
    """
    Defines the types of page field supported by the application
    """
    DEFAULT = 'default'
    PASSWORD = 'password'


class Field(Control):
    """
    Implements the field
    """    
    def __init__(self, parent, field):
        super().__init__(parent)
        self.field = field # type: core.field.field.Field
        self.type = FieldType.DEFAULT
        self.caption = field.caption
        self.enabled = True
        self.visble = True

    def _onrender(self, obj):
        obj['caption'] = self.caption
        obj['codename'] = self.field._codename
        obj['controltype'] = FieldType.name(self.type)
        obj['datatype'] = core.field.field.FieldType.name(self.field.type)
        obj['enabled'] = self.enabled
        obj['visible'] = self.visible
        
        if self.field._relations:
            obj['hasrelations'] = True

    def getrelated(self, value=''):
        """
        Get relations
        """
        rel = self.field._getrelation()

        dataset = []
        schema = []
        if rel:
            tab = rel['to']()

            schema = self._page._getschema(tab)

            if tab.findset():
                while tab.read():
                    dataset.append(self._page._getdatarow(tab))

        return {
            'schema': schema,
            'dataset': dataset
        }

    def validate(self, value, parsevalue=True):
        """
        Handle UI validation
        """
        if parsevalue:
            value = self.field.evaluate(value)
        
        self.field.validate(value)

        if self._page.rec is not None:
            if self._page.rec._rowversion is None:
                self._page.rec.insert(True)

                self._page._dataset.append(self._page._getdatarow(self._page.rec))
                self._page._currentrow = len(self._page._dataset) - 1

            else:
                self._page.rec.modify(True)

        return self._page._getdatarow(self._page.rec)