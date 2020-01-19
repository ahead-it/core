"""
Contains internationalization function
"""
import os
from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po
import core.session
import core.utility.system


_catalogs = dict()

def gettext(text, modname, localecode):
    """
    Search for a translation of text in loaded catalogs, for the context of modname and 
    for specified localecode.
    Locale is searched first in full way (ex. en-US), next in generic way (ex. en)
    """    
    if not localecode in _catalogs:
        localecode = localecode[0:2]
        if not localecode in _catalogs:
            return text

    msg = _catalogs[localecode].get(text, modname)
    if msg and msg.string:
        text = msg.string

    return text

def label(text):
    """
    Search for a translation of text in loaded catalogs in the current context 
    in current language code
    """    
    return gettext(text, core.utility.system.System.get_caller_modulename(), core.session.Session.language_code)

def mergecatalog(filename):
    """
    Try to load a translation catalog
    """
    language = os.path.basename(filename)[0:-3]
    if not language in _catalogs:
        _catalogs[language] = Catalog()

    try:
        f = open(filename, "br")
        c = read_po(f)
        f.close()
        for m in c:
            _catalogs[language].add(m.id, string=m.string, context=m.context)

    except:
        core.application.Application.logexception('loadlang')

def loadtranslations():
    """
    For each app, for each language load all texts
    """
    for app in core.application.Application.apps:
        dn = core.application.Application.apps[app].base_path + '/translation/'
        if os.path.exists(dn) and os.path.isdir(dn):
            for tt in os.listdir(dn):
                if tt.endswith(".po"):
                    mergecatalog(dn + tt)



