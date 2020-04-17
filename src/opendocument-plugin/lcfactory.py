# -*- coding: utf-8 -*-
import unohelper

from com.sun.star.ui import XUIElementFactory

IMPL_NAME = "lire.libre.lirecouleur"
RESOURCE_NAME = "private:resource/toolpanel/lire.libre/lirecouleur"

class lirecouleurFactory(unohelper.Base, XUIElementFactory):
    """ Factory for LireCouleur """
    def __init__(self, ctx):
        self.ctx = ctx

    # XUIElementFactory
    def createUIElement(self, name, args):
        element = None
        if name == RESOURCE_NAME:
            frame = None
            parent = None
            for arg in args:
                if arg.Name == "Frame":
                    frame = arg.Value
                elif arg.Name == "ParentWindow":
                    parent = arg.Value
            if frame and parent:
                try:
                    import lirecouleur.lcpanel
                    element = lirecouleur.lcpanel.lirecouleurModel(self.ctx, frame, parent)
                except:
                    pass
        return element

    # XServiceInfo
    def getImplementationName(self):
        return IMPL_NAME
    def supportsService(self, name):
        return IMPL_NAME == name
    def supportedServiceNames(self):
        return (IMPL_NAME,)


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    lirecouleurFactory, IMPL_NAME, (IMPL_NAME,),)
