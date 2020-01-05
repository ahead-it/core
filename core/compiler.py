import os
import datetime
import importlib
import inspect
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
from typing import Dict


_objs = ('option', 'table', 'codeunit', 'report', 'page', 'query')

class Merger:
    """
    This class generate symbol and proxy classes for multiple unit inherited each other
    """
    def __init__(self):
        self._symbols = {}
        self._merged = {}
        self._types = {}
        self._funcmap = {}
        self._attrmap = {}

    def add_types(self, typ: Dict[str, str]):
        """
        Add type to merger
        KEY     class name        
        """
        for cla in typ:
            self._types[cla] = typ[cla]

    def add_symbols(self, sym):
        for cla in sym:
            if not cla in self._symbols:
                self._symbols[cla] = []

            for mro in sym[cla]:
                if not mro in self._symbols[cla]:
                    self._symbols[cla].append(mro)

    def _merge(self):
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

    def _add_tomap(self, prxname, funcname):
        if funcname not in attributes.map:
            return

        if prxname not in self._funcmap:
            self._funcmap[prxname] = []

        attrs = attributes.map[funcname]
        for a in attrs:
            if a not in self._funcmap[prxname]:
                self._funcmap[prxname].append(a)

            if a not in self._attrmap:
                self._attrmap[a] = []

            if prxname not in self._attrmap[a]:
                self._attrmap[a].append(prxname)

    def _generate_proxy(self, typ, nam, mros, buf, imp):
        stat = ''
        init = ''
        body = ''
        base = ''

        for mro in mros:
            i = mro.rfind('.')
            modname = mro[:i]
            claname = mro[i+1:]

            try:
                mod = importlib.import_module(modname)
                cla = getattr(mod, claname)
                obj = cla()

                if base == '':
                    for b in inspect.getmro(cla):
                        if b.__module__.startswith('core.object.'):
                            base = b.__module__ + '.' + b.__qualname__
                            break
            except:
                Application.logexception('genproxy')
                continue

            # static and class members
            members = [obj.__class__.__dict__, obj.__dict__] 

            for i in range(0, 2):
                for m in members[i]:
                    if m.startswith('_'):
                        continue

                    attr = getattr(obj, m)

                    if callable(attr):
                        isstatic = not inspect.ismethod(attr)
                        attr = inspect.unwrap(attr)
                        if (attr.__module__ == modname) and (i == 0):
                            self._add_tomap('app.' + typ + '/' + nam + '.' + m, modname + '/' + claname + '.' + m)

                            if isstatic:
                                body += '    @staticmethod\n'
                            body += '    def ' + m + '(' + ', '.join(attr.__code__.co_varnames) + '):\n'
                            body += '        pass\n'

                    else:
                        if i == 0:
                            stat += '    ' + m + ' = None # type: ' + type(attr).__module__ + '.' + type(attr).__qualname__ + '\n'
                        else:
                            init += '        self.' + m + ' = None # type: ' + type(attr).__module__ + '.' + type(attr).__qualname__ + '\n'
                        
                        if not type(attr).__module__ in imp:
                            imp.append(type(attr).__module__)  
              
        for mro in mros:
            i = mro.rfind('.')
            mod = mro[:i]
            if not mod in imp:
                imp.append(mod)   

        basemod = base[:base.rfind('.')]
        if not basemod in imp:
            imp.append(basemod)           

        buf.append('class ' + nam + '(' + base + '):\n')
        if stat > '':
            buf.append(stat)

        buf.append('    def __new__(cls):\n')
        buf.append('        class _proxy(' + ', '.join(mros) + '):\n')
        buf.append('            pass\n')
        buf.append('        return _proxy()\n')

        if init > '':
            buf.append('    def __init__(self):\n')
            buf.append(init)

        if body > '':
            buf.append(body)      

        buf.append('\n')    
              
    def generate_symbols(self):
        self._funcmap = {}
        self._attrmap = {}

        imp = {}
        buf = {}
        for obj in _objs:
            buf[obj] = []
            imp[obj] = []
        
        self._merge()

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

            self._generate_proxy(typ, nam, mros, buf[typ], imp[typ])
                    
        for obj in _objs:
            fn = Application.base_path + 'app/' + obj + '.py'
            f = open(fn, "a")

            if imp[obj]:
                for mod in imp[obj]:
                    f.write('import ' + mod + '\n')
                f.write('\n\n')

            if buf[obj]:
                for line in buf[obj]:
                    f.write(line)
                    
            f.close()
        
        fn = Application.base_path + 'app/__init__.py'
        f = open(fn, "w")
        f.write('# auto generated file, do not edit\n')
        f.close()

        fn = Application.base_path + 'app/map.py'
        f = open(fn, "w")
        f.write('# auto generated file, do not edit\n')

        maps = {'functions': self._funcmap, 'attributes': self._attrmap}
        for map in maps:
            f.write(map + ' = {\n')
            i = 0
            for x in maps[map]:
                i += 1
                f.write('    \'' + x + '\': [\n')

                j = 0
                for y in maps[map][x]:
                    j += 1
                    f.write('        \'' + y + '\'')
                    if j < len(maps[map][x]):
                        f.write(',')
                    f.write('\n')

                f.write('    ]')
                if i < len(maps[map]):
                        f.write(',')
                f.write('\n')
                
            f.write('}\n\n')

        f.close()        

    @staticmethod
    def assert_symfiles():
        for obj in _objs:
            fn = Application.base_path + 'app/' + obj + '.py'
            f = open(fn, "w")
            f.write('# auto generated file, do not edit\n')
            f.close()
    
class Compiler:
    def __init__(self, app: App):
        self._catalog = None
        self.symbols = {}
        self.types = {}
        self.app = app

    def find_symbols(self):
        self.symbols = {}
        self.types = {}

        Merger.assert_symfiles()

        mods = self.get_modules()
        for modname in mods:
            try:
                mod = importlib.import_module(modname)
                for name, obj in inspect.getmembers(mod):
                    if inspect.isclass(obj) and (issubclass(obj, Unit) or issubclass(obj, Option))\
                        and (obj.__module__ == modname):
                        self._add_object(obj)
            except:
                Application.logexception('findsymb')

    def _add_object(self, obj):
        bas = obj.__module__ + '.' + obj.__qualname__
        if not bas.startswith('app.'):
            return

        self.symbols[bas] = []

        first = True
        mro = inspect.getmro(obj)[1:]        
        for cla in mro:
            fn = cla.__module__ + '.' + cla.__qualname__

            if first:
                first = False
                if fn.startswith('core.'):
                    self.types[bas] = cla.__qualname__
            
            if fn.startswith('app.') and (fn != bas):
                if not fn in self.symbols:
                    self.symbols[fn] = []

                self.symbols[fn].append(bas)                
                
    def get_modules(self):
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
        tn = self.app.base_path + "translation"

        if not os.path.exists(tn):
            os.mkdir(tn)

        self._catalog = Catalog()

        mods = self.get_modules()
        for modname in mods:
            self._extract_texts(mods[modname], modname)

        self._write_catalog(tn + "/global.pot")

    def _extract_texts(self, fn, ctx):
        for t in extract_from_file('python', fn, keywords={'label': None}):
            self._catalog.add(t[1], context=ctx)    

    def _write_catalog(self, fn):
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
