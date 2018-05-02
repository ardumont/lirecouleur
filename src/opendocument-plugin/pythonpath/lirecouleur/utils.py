#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# see http://aoo-extensions.sourceforge.net/en/project/watchingwindow
import uno
import unohelper

from com.sun.star.awt.PosSize import (POSSIZE as PS_POSSIZE)
from builtins import int

CONFIG_NODE = "/lire.libre.lirecouleur/Settings"

"""
    Constantes LireCouleur
"""
class ConstLireCouleur:
    # différentes configurations de marquage des syllabes
    SYLLABES_LC = 0
    SYLLABES_STD = 1
    SYLLABES_ORALES = 1
    SYLLABES_ECRITES = 0

    # prononciation différente entre l'Europe et le Canada
    MESTESSESLESDESCES = {'':'e_comp','fr':'e_comp','fr_CA':'e^_comp'}

def create_uno_struct(cTypeName):
    """Create a UNO struct and return it.
    Similar to the function of the same name in OOo Basic. -- Copied from Danny Brewer library
    """
    sm = uno.getComponentContext().ServiceManager
    oCoreReflection = sm.createInstance( "com.sun.star.reflection.CoreReflection" )
    # Get the IDL class for the type name
    oXIdlClass = oCoreReflection.forName( cTypeName )
    # Create the struct.
    __, oStruct = oXIdlClass.createObject( None )
    return oStruct

def create_uno_service(serviceName, ctx=None):
    if ctx is None:
        ctx = uno.getComponentContext()

    sm = ctx.ServiceManager
    try:
        serv = sm.createInstanceWithContext(serviceName, ctx)
    except:
        serv = sm.createInstance(serviceName)

    return serv

def create_control(ctx, control_type, x, y, width, height, names, values):
    """ create a control. """
    smgr = ctx.getServiceManager()
    
    ctrl = smgr.createInstanceWithContext(
        "com.sun.star.awt." + control_type, ctx)
    ctrl_model = smgr.createInstanceWithContext(
        "com.sun.star.awt." + control_type + "Model", ctx)
    
    if len(names) > 0:
        ctrl_model.setPropertyValues(names, values)
    ctrl.setModel(ctrl_model)
    ctrl.setPosSize(x, y, width, height, PS_POSSIZE)
    return ctrl


def create_container(ctx, parent, names, values, __fit=True):
    """ create control container. """
    cont = create_control(ctx, "UnoControlContainer", 0, 0, 0, 0, names, values)
    cont.createPeer(parent.getToolkit(), parent)
    #if fit:
    #    cont.setPosSize()
    return cont


def create_controls(ctx, container, controls):
    """
    ((TYPE, NAME, x, y, width, height, PROP_NAMES, PROP_VALUES, OPTIONS), ())
    """
    smgr = ctx.getServiceManager()
    for defs in controls:
        c = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControl" + defs[0], ctx)
        cm = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControl" + defs[0] + "Model", ctx)
        cm.setPropertyValues(defs[6], defs[7])
        c.setModel(cm)
        c.setPosSize(defs[2], defs[3], defs[4], defs[5], PS_POSSIZE)
        
        container.addControl(defs[1], c)
        if len(defs) == 9:
            options = defs[8]
            if defs[0] == "Button":
                if "ActionCommand" in options:
                    c.setActionCommand(options["ActionCommand"])
                if "ActionListener" in options:
                    c.addActionListener(options["ActionListener"])
            elif defs[0] == "Combo":
                if "TextListener" in options:
                    c.addTextListener(options["TextListener"])
        
    return container


def get_backgroundcolor(window):
    """ Get background color through accesibility api. """
    try:
        return window.getAccessibleContext().getBackground()
    except:
        pass
    return 0xeeeeee


from com.sun.star.task import XInteractionHandler
 
class DummyHandler(unohelper.Base, XInteractionHandler):
    """ dummy XInteractionHanlder interface for 
        the StringResouceWithLocation """
    def __init__(self): pass
    def handle(self,request): pass


def get_resource(ctx, location, locale, name):
    """ load from resource and returns them as a dictionary. """
    res = {}
    try:
        resolver = ctx.getServiceManager().createInstanceWithContext(
            "com.sun.star.resource.StringResourceWithLocation", ctx)
        resolver.initialize((location, True, locale, name, "", DummyHandler()))
        ids = resolver.getResourceIDs()
        
        for i in ids:
            res[i] = resolver.resolveString(i)
    except Exception as e:
        print(e)
    return res


from com.sun.star.lang import Locale
from com.sun.star.beans import PropertyValue
from com.sun.star.beans.PropertyState import DIRECT_VALUE as PS_DIRECT_VALUE


def get_config_access(ctx, nodepath, updatable=False):
    """ get configuration access. """
    arg = PropertyValue("nodepath", 0, nodepath, PS_DIRECT_VALUE)
    cp = ctx.getServiceManager().createInstanceWithContext(
        "com.sun.star.configuration.ConfigurationProvider", ctx)
    if updatable:
        return cp.createInstanceWithArguments(
        "com.sun.star.configuration.ConfigurationUpdateAccess", (arg,))
    else:
        return cp.createInstanceWithArguments(
        "com.sun.star.configuration.ConfigurationAccess", (arg,))


def get_config_value(ctx, nodepath, name):
    """ get configuration value. """
    cua = get_config_access(ctx, nodepath)
    return cua.getPropertyValue(name)


def get_ui_locale(ctx):
    """ get UI locale as css.lang.Locale struct. """
    loc = get_config_value(ctx, "/org.openoffice.Setup/L10N", "ooLocale")
    if "-" in loc:
        parts = loc.split("-")
        locale = Locale(parts[0], parts[1], "")
    else:
        locale = Locale(loc, "", "")
    return locale


def create_dialog(ctx, url):
    """ create dialog from url. """
    try:
        return ctx.getServiceManager().createInstanceWithContext(
            "com.sun.star.awt.DialogProvider", ctx).createDialog(url)
    except:
        return None


"""
    Load and set configuration values.
"""
class Settings(object):
    """ Load and set configuration values. """
    def __init__(self, ctx=None):
        try:
            self._loaded = False
            self.ctx = ctx
            if self.ctx is None:
                self.ctx = uno.getComponentContext()
        except:
            pass
    
    def configure(self, names, values):
        cua = get_config_access(self.ctx, CONFIG_NODE, True)
        try:
            cua.setPropertyValues(names, values)            
            cua.commitChanges()
        except:
            pass
    
    def getPropertyValue(self, cua, name):
        try:
            return cua.getPropertyValue(name)
        except:
            pass
    
    def _load(self):
        cua = get_config_access(self.ctx, CONFIG_NODE)
        self.FPossibles = self.getPropertyValue(cua, "__fonctions_possibles__").split(':')
        self.TaillIco = self.getPropertyValue(cua, "__taille_icones__")
        self.Fonctions = {}
        for fct in self.FPossibles:
            prop = self.getPropertyValue(cua, fct)
            if not prop is None:
                self.Fonctions[fct] = prop.split(':')
                self.Fonctions[fct][2] = eval(self.Fonctions[fct][2])
        
        prop = self.getPropertyValue(cua, "__selection_phonemes__")
        if not prop is None:
            selphon = [ph.split(':') for ph in prop.split(';')]
            self.SelectionPhonemes = dict([[ph[0], eval(ph[1])] for ph in selphon])
            # considérer que la sélection des phonèmes 'voyelle' s'étend à 'yod'+'voyelle' et à 'wau'+'voyelle'
            for phon in ['a', 'a~', 'e', 'e^', 'e_comp', 'e^_comp', 'o', 'o~', 'i', 'e~', 'x', 'x^', 'u', 'q_caduc']:
                try:
                    self.SelectionPhonemes['j_'+phon] = self.SelectionPhonemes[phon]
                    self.SelectionPhonemes['w_'+phon] = self.SelectionPhonemes[phon]
                except:
                    self.SelectionPhonemes[phon] = self.SelectionPhonemes['j_'+phon] = self.SelectionPhonemes['w_'+phon] = 0
        prop = self.getPropertyValue(cua, "__selection_lettres__")
        if not prop is None:
            selphon = [ph.split(':') for ph in prop.split(';')]
            self.SelectionLettres = dict([[ph[0], eval(ph[1])] for ph in selphon])
        self.Template = self.getPropertyValue(cua, "__template__")
        self.Simple = self.getPropertyValue(cua, "__detection_phonemes__")
        self.Point = self.getPropertyValue(cua, "__point__")
        choix_syllo = self.getPropertyValue(cua, "__syllo__")
        if not isinstance(choix_syllo, int):
            self.Syllo = (ConstLireCouleur.SYLLABES_LC, ConstLireCouleur.SYLLABES_ECRITES)
        else:
            self.Syllo = (choix_syllo%2, int(choix_syllo/10)%2)
        if self.Syllo[1]:
            self.SelectionPhonemes['q_caduc'] = self.SelectionPhonemes['yod_q_caduc'] = self.SelectionPhonemes['#']
        else:
            self.SelectionPhonemes['q_caduc'] = self.SelectionPhonemes['yod_q_caduc'] = self.SelectionPhonemes['q']

        self.Superpose = self.getPropertyValue(cua, "__superpose__")
        self.Alternate = self.getPropertyValue(cua, "__alternate__")
        self.Locale = self.getPropertyValue(cua, "__locale__")
        self.SubSpaces = self.getPropertyValue(cua, "__subspaces__")
        self._loaded = True
    
    def get(self, name):
        """ get specified value. """
        if not self._loaded:
            self._load()
        if name == "__fonctions_possibles__":
            return self.FPossibles
        if name == "__taille_icones__":
            return self.TaillIco
        if name == "__selection_phonemes__":
            return self.SelectionPhonemes
        if name == "__selection_lettres__":
            return self.SelectionLettres
        if name == "__template__":
            return self.Template
        if name == "__point__":
            return self.Point
        if name == "__detection_phonemes__":
            return self.Simple
        if name == "__superpose__":
            return self.Superpose
        if name == "__syllo__":
            return self.Syllo
        if name == "__alternate__":
            return self.Alternate
        if name == "__locale__":
            return self.Locale
        if name == "__subspaces__":
            return self.SubSpaces
        try:
            return self.Fonctions[name]
        except:
            return ""
        return ""

    def setValue(self, name, value):
        """ set specified value. """
        cua = get_config_access(self.ctx, CONFIG_NODE, True)
        
        try:
            if name == "__fonctions_possibles__":
                self.FPossibles = value
                cua.setPropertyValues(("__fonctions_possibles__",), (':'.join(value),))
            elif name == "__taille_icones__":
                self.TaillIco = value
                cua.setPropertyValues(("__taille_icones__",), (value,))
            elif name == "__selection_phonemes__":
                self.SelectionPhonemes = value
                cua.setPropertyValues(("__selection_phonemes__",), (';'.join([ph+':'+str(value[ph]) for ph in value.keys()]),))
            elif name == "__selection_lettres__":
                self.SelectionLettres = value
                cua.setPropertyValues(("__selection_lettres__",), (';'.join([ph+':'+str(value[ph]) for ph in value.keys()]),))
            elif name == "__template__":
                self.Template = value
                cua.setPropertyValues(("__template__",), (value,))
            elif name == "__point__":
                self.Point = value
                cua.setPropertyValues(("__point__",), (value,))
            elif name == "__detection_phonemes__":
                self.Simple = value
                cua.setPropertyValues(("__detection_phonemes__",), (value,))
            elif name == "__syllo__":
                self.Syllo = value
                cua.setPropertyValues(("__syllo__",), (value[1]*10+value[0],))
            elif name == "__superpose__":
                self.Superpose = value
                cua.setPropertyValues(("__superpose__",), (value,))
            elif name == "__alternate__":
                self.Alternate = value
                cua.setPropertyValues(("__alternate__",), (value,))
            elif name == "__locale__":
                self.Locale = value
                cua.setPropertyValues(("__locale__",), (value,))
            elif name == "__subspaces__":
                self.SubSpaces = value
                cua.setPropertyValues(("__subspaces__",), (value,))
            else:
                self.Fonctions[name] = value
                cua.setPropertyValues((self.Fonctions[name],), (value,))

            cua.commitChanges()
        except:
            pass
