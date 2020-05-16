import os
import datetime
import importlib
import inspect
import sys
from typing import Dict
from babel.core import Locale
from babel.messages.pofile import write_po
from babel.messages.extract import extract_from_file
from babel.messages.catalog import Catalog
from babel.dates import UTC
from core.application import Application
from core.app import App
from core.object.unit import Unit
from core.object.option import Option
from core.utility.system import System
from core.object import attributes
import core.language

_objs = ('option', 'table', 'codeunit', 'report', 'page', 'query')

class Merger:
    """
    This class generate symbol and proxy classes for multiple unit inherited each other
    """
    def __init__(self):
        self._symbols = {}
        self._types = {}
        self._merged = {}
        self._bufimport = {}
        self._bufbody = {}

    def add_types(self, typ: Dict[str, str]):
        """
        Add type to merger
        """
        for cla in typ:
            self._types[cla] = typ[cla]

    def add_symbols(self, sym):
        """
        Add symbols to merger
        """
        for cla in sym:
            if not cla in self._symbols:
                self._symbols[cla] = []

            for mro in sym[cla]:
                if not mro in self._symbols[cla]:
                    self._symbols[cla].append(mro)

    def _merge(self):
        """
        Merge symbols by MRO
        """
        todel = []   
        self._merged = dict(self._symbols)

        swap = True
        while swap:
            swap = False

            for cla in self._merged:
                for mro in self._merged[cla][:]:
                    if mro in self._merged:
                        if self._merged[mro]:
                            self._merged[cla].remove(mro)

                        for mro2 in self._merged[mro][:]:
                            if not mro2 in self._merged[cla]:
                                self._merged[cla].append(mro2)
                            self._merged[mro].remove(mro2)
                            swap = True

                        if not self._merged[mro]:
                            if not mro in todel:
                                todel.append(mro)

        for mro in todel:
            del self._merged[mro]

    def _generate_proxy(self, phase, typ, nam, mros):
        """
        Generate class proxy
        """
        init = ''
        body = ''
        base = ''
        imports = []
        fullmro = []
        members = []

        for mro in mros:
            i = mro.rfind('.')
            modname = mro[:i]
            if not modname in imports:
                imports.append(modname)            
            claname = mro[i+1:]

            try:
                mod = importlib.import_module(modname)
                cla = getattr(mod, claname)
                for b in inspect.getmro(cla):
                    if b.__module__.startswith('core.'):
                        if base == '':
                            base = b.__module__ + '.' + b.__qualname__
                            if not b.__module__ in imports:
                                imports.append(b.__module__)            
                            break

                    if not b.__module__.startswith('app.'):
                        continue

                    if b not in fullmro:
                        fullmro.append(b)

            except:
                Application.logexception('genproxy')
                continue

        isoption = (base == 'core.object.option.Option')

        for mro in fullmro:
            # instance members
            for m in mro.__dict__:
                if m.startswith('_') or (m in members):
                    continue

                attr = getattr(mro, m)
                attr = inspect.unwrap(attr)

                if callable(mro.__dict__[m]):
                    members.append(m)                    

                    body += '    def ' + m + '(' + ', '.join(attr.__code__.co_varnames) + '):\n'
                    body += '        pass\n'
                elif isoption:
                    qn = mro.__module__ + '.' + mro.__qualname__
                    i = qn.rfind('.')
                    qn = qn[0:i]
                    capt = mro.caption(attr)
                    capt = capt.replace('\'', '\\\'')

                    body += '    ' + m + ' = ' + str(attr) + ', \'' + capt + '\', \'' + qn + '\'\n'

            if (phase != 2) or isoption:
                continue

            try:
                obj = mro()

                for m in obj.__dict__:
                    if m.startswith('_') or (m in members):
                        continue

                    attr = getattr(obj, m)
                    members.append(m)    

                    qn = type(attr).__qualname__
                    p = qn.find('__new__')
                    if p > 0:
                        qn = qn[0:p-1]    

                    init += '        self.' + m + ' = None  # type: ' + type(attr).__module__ + '.' + qn + '\n'

                    if not type(attr).__module__ in imports:
                        imports.append(type(attr).__module__)  

            except:
                Application.logexception('genproxy')
                continue  
       
        # split local imports from core imports
        locmod = []
        for i in imports:
            if i.startswith('app.') and (not i.startswith('app.option')):
                locmod.append(i)
            else:
                if i not in self._bufimport[typ]:
                    self._bufimport[typ].append(i)         

        # write body
        buf = []
        buf.append('class ' + nam + '(' + base + '):\n')

        if not isoption:
            buf.append('    def __new__(cls, *args, **kwargs):\n')
            for i in locmod:
                buf.append('        import ' + i + '\n')
            buf.append('        class proxy(' + ', '.join(mros) + '):\n')
            buf.append('            pass\n')
            buf.append('        return proxy(*args, **kwargs)\n')

        if init > '':
            buf.append('    def __init__(self):\n')
            buf.append(init)

        if body > '':
            buf.append(body)  

        buf.append('\n')   
        self._bufbody[typ] += buf 

    def generate_symbols(self):
        """
        Generate symbols in two pass, first static members and properties, next
        intance members and properties
        """
        core.language._suspend_translation = True

        self._merge()        
        self._generate_symbols(1)

        for obj in _objs:   
            modulename = 'app.' + obj
            if modulename in sys.modules:
                importlib.reload(sys.modules[modulename])

        self._generate_symbols(2)
        core.language._suspend_translation = False

    def _generate_symbols(self, phase):
        """
        Generate symbols
        """
        self._bufimport = {}
        self._bufbody = {}        
        for obj in _objs:
            self._bufimport[obj] = []
            self._bufbody[obj] = []

        for cla in self._merged:
            if not cla in self._types:
                continue

            typ = self._types[cla].lower()
            if not typ in _objs:
                continue

            i = cla.rfind('.') + 1
            nam = cla[i:]

            if self._merged[cla]:
                mros = self._merged[cla]
            else:
                mros = [cla] 

            self._generate_proxy(phase, typ, nam, mros)
                    
        for obj in _objs:
            fn = Application.base_path + 'app/' + obj + '.py'
            f = open(fn, "w")

            if self._bufimport[obj]:
                for mod in self._bufimport[obj]:
                    f.write('import ' + mod + '\n')
                f.write('\n\n')

            if self._bufbody[obj]:
                for line in self._bufbody[obj]:
                    f.write(line)
                    
            f.close()
        
        fn = Application.base_path + 'app/__init__.py'
        f = open(fn, "w")
        f.write('# auto generated file, do not edit\n')
        f.close()

    @staticmethod
    def assert_symfiles():
        """
        Create empty app files to assert compilation
        """
        for obj in _objs:
            fn = Application.base_path + 'app/' + obj + '.py'
            f = open(fn, "w")
            f.write('# auto generated file, do not edit\n')
            f.close()
    
class Compiler:
    """
    This class extract all method defined by an app and handles its translations
    """
    def __init__(self, app: App):
        self._catalog = None
        self.symbols = {}
        self.types = {}
        self.app = app

    def find_symbols(self):
        """
        Extract symbols and types defined by an app
        """
        self.symbols = {}
        self.types = {}

        Merger.assert_symfiles()

        mods = self.get_modules()
        for modname in mods:
            try:
                mod = importlib.import_module(modname)
                for name, obj in inspect.getmembers(mod):
                    if (not inspect.isclass(obj)) or (obj.__module__ != modname):
                        continue

                    for mro in inspect.getmro(obj):
                        if issubclass(mro, Unit) or issubclass(mro, Option):
                            self._add_object(obj)
                            break
            except:
                Application.logexception('findsymb')

    def _add_object(self, obj):
        """
        Add a single object to symbols
        """
        bas = obj.__module__ + '.' + obj.__qualname__
        if not bas.startswith('app.'):
            return

        self.symbols[bas] = []

        basefound = False
        mro = inspect.getmro(obj)[1:]        
        for cla in mro:
            fn = cla.__module__ + '.' + cla.__qualname__

            if not basefound:
                for o in _objs:
                    if fn.startswith('core.object.' + o + '.'):
                        self.types[bas] = cla.__qualname__
                        basefound = True
            
            if fn.startswith('app.') and (fn != bas):
                if not fn in self.symbols:
                    self.symbols[fn] = []

                self.symbols[fn].append(bas)                
                
    def get_modules(self):
        """
        Get all module defined by the app
        """
        res = {}

        for root, dirs, files in os.walk(self.app.base_path):
            if not root.endswith('/'):
                root += '/'

            for f in files:
                if f.endswith(".py") and (not f.startswith('__')):
                    ct = root + f
                    modname = System.get_modulename(ct)
                    res[modname] = ct

        return res

    def generate_textcatalog(self):
        """
        Extract text from the app
        """
        tn = self.app.base_path + "translation"

        if not os.path.exists(tn):
            os.mkdir(tn)

        self._catalog = Catalog()

        mods = self.get_modules()
        for modname in mods:
            self._extract_texts(mods[modname], modname)

        self._write_catalog(tn + "/global.pot")

    def _extract_texts(self, fn, ctx):
        """
        Extract text from the app
        """        
        for t in extract_from_file('python', fn, keywords={'label': None}):
            self._catalog.add(t[1], context=ctx)    

    def _write_catalog(self, fn):
        """
        Write text catalog
        """        
        self._catalog.locale = Locale.parse('en_US')
        self._catalog.project = self.app.display_name
        self._catalog.creation_date = datetime.datetime.now(UTC)
        self._catalog.revision_date = datetime.datetime.now(UTC)
        self._catalog.version = self.app.version
        self._catalog.last_translator = self.app.author
        self._catalog.language_team = self.app.author

        f = open(fn, "bw")
        write_po(f, self._catalog)
        f.close()       
