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
        self.field = field  # type: core.field.field.Field
        self.type = FieldType.DEFAULT
        self.caption = field.caption
        self.enabled = True
        self.visible = True

    def _onrender(self, obj):
        obj['caption'] = self.caption
        obj['codename'] = self.field._codename
        obj['controltype'] = self.type
        obj['datatype'] = core.field.field.FieldType.name(self.field.type)
        obj['enabled'] = self.enabled
        obj['visible'] = self.visible
        
        if self.field._relations:
            obj['hasrelations'] = True

    def getrelated(self, value='', search=True):
        """
        Get relations
        """
        rel = self.field._getrelation()

        dataset = []
        fdataset = []
        schema = []
        if rel:
            tab = rel['to']()

            schema = self._page._getschema(tab._fields)
            if rel['filters']:
                rel['filters'](tab)

            # FIXME search fields
            value = value.strip()
            if value:
                tab.setfilterlevel(core.field.field.FilterLevels.DROPDOWN, True)
                if not value.endswith('*'):
                    value += '*'

                for f in tab._fields:
                    if f.type in [core.field.field.FieldType.TEXT, core.field.field.FieldType.CODE]:
                        f.setfilter(value)

                tab.setfilterlevel(core.field.field.FilterLevels.PUBLIC)

            if tab.findset():
                while tab.read():
                    dataset.append(self._page._getdatarow(tab._fields))
                    fdataset.append(self._page._getdatarow(tab._fields, True))

        return {
            'schema': schema,
            'dataset': dataset,
            'fdataset': fdataset
        }

    def validate(self, value, parsevalue=True):
        """
        Handle UI validation
        """
        if parsevalue:
            value = self.field.evaluate(value)
        else:
            value = self.field.deserialize(value)
        
        self.field.validate(value)

        if self._page.rec is not None:
            if self._page.rec._rowversion is None:
                self._page.rec.insert(True)
                self._page._onaftergetdata()
                self._page._dataset.append(self._page._getdatarow(self._page._allfields))
                self._page._fdataset.append(self._page._getdatarow(self._page._allfields, True))
                self._page._selectedrows = [len(self._page._dataset) - 1]

                if not self._page._islist:
                    self._page.rec.setpkfilter(*self._page._getrowpk(self._page._selectedrows[0]))

            else:
                self._page.rec.modify(True)

        return {
            'datarow': self._page._getdatarow(self._page._allfields),
            'fdatarow': self._page._getdatarow(self._page._allfields, True)
        }
