#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# this is a modified version of http://aoo-extensions.sourceforge.net/en/project/watchingwindow extension
import unohelper

import threading

from com.sun.star.awt import (XWindowListener, XActionListener, XMouseListener)
from com.sun.star.lang import XServiceInfo
from com.sun.star.ui import XUIElement, XToolPanel

from com.sun.star.awt import ActionEvent

from com.sun.star.awt.PosSize import (X as PS_X, Y as PS_Y, 
    WIDTH as PS_WIDTH, HEIGHT as PS_HEIGHT, SIZE as PS_SIZE, POSSIZE as PS_POSSIZE)

from com.sun.star.ui.UIElementType import TOOLPANEL as UET_TOOLPANEL

from com.sun.star.lang import XComponent
from com.sun.star.beans import PropertyValue
from com.sun.star.beans.PropertyState import DIRECT_VALUE as PS_DIRECT_VALUE

from com.sun.star.awt.MenuItemStyle import CHECKABLE as MIS_CHECKABLE
from com.sun.star.awt.MessageBoxButtons import (
    BUTTONS_OK_CANCEL as MBB_BUTTONS_OK_CANCEL, DEFAULT_BUTTON_CANCEL as MBB_DEFAULT_BUTTON_CANCEL)

EXT_ID = "lire.libre.lirecouleur"

from .utils import (create_control, create_container, create_controls, 
    get_backgroundcolor, get_resource, get_config_access, 
    get_config_value, create_uno_struct, create_uno_service, Settings)
    
from .lirecouleurui import (__lirecouleur_phonemes__,__lirecouleur_noir__,__lirecouleur_confusion_lettres__,
        __lirecouleur_consonne_voyelle__,__lirecouleur_couleur_mots__,__lirecouleur_defaut__,__lirecouleur_espace__,
        __lirecouleur_espace_lignes__,__lirecouleur_extra_large__,__lirecouleur_l_muettes__,__lirecouleur_large__,
        __lirecouleur_liaisons__,__lirecouleur_lignes__,__lirecouleur_phon_muet__,__lirecouleur_graphemes_complexes__,
        __lirecouleur_ponctuation__,__lirecouleur_separe_mots__,__lirecouleur_suppr_decos__,__lirecouleur_suppr_syllabes__,
        __lirecouleur_syllabes__,__new_lirecouleur_document__,__lirecouleur_alterne_phonemes__)

class lirecouleurModel(unohelper.Base, XUIElement, XToolPanel, XComponent):
    """ LireCouleur model. """
    
    def __init__(self, ctx, frame, parent):
        self.ctx = ctx
        self.frame = frame
        self.parent = parent
        
        self.view = None
        self.window = None
        try:
            view = lirecouleurView(ctx, self, frame, parent)
            self.view = view
            self.window = view.container
            
            def _focus_back():
                self.frame.getContainerWindow().setFocus()
            
            threading.Timer(0.3, _focus_back).start()
        except Exception as e:
            print('Exception 1:',e)
    
    # XComponent
    def dispose(self):
        self.ctx = None
        self.frame = None
        self.parent = None
        self.view = None
        self.window = None
    
    def addEventListener(self, ev): pass
    def removeEventListener(self, ev): pass
    
    # XUIElement
    def getRealInterface(self):
        return self
    @property
    def Frame(self):
        return self.frame
    @property
    def ResourceURL(self):
        return RESOURCE_NAME
    @property
    def Type(self):
        return UET_TOOLPANEL
    
    # XToolPanel
    def createAccessible(self, parent):
        return self.window.getAccessibleContext()
    @property
    def Window(self):
        return self.window
    
    def dispatch(self, cmd, args):
        """ dispatch with arguments. """
        helper = self.ctx.getServiceManager().createInstanceWithContext(
            "com.sun.star.frame.DispatchHelper", self.ctx)
        helper.executeDispatch(self.frame, cmd, "_self", 0, args)
    
    def hidden(self):
        self.data_model.enable_update(False)
    def shown(self):
        self.data_model.enable_update(True)

from com.sun.star.util import URL

from com.sun.star.view.SelectionType import SINGLE as ST_SINGLE
from com.sun.star.style.HorizontalAlignment import RIGHT as HA_RIGHT

from com.sun.star.awt.PopupMenuDirection import EXECUTE_DEFAULT as PMD_EXECUTE_DEFAULT
from com.sun.star.awt import Rectangle

from com.sun.star.awt.MouseButton import LEFT as MB_LEFT, RIGHT as MB_RIGHT

from com.sun.star.awt.Key import RETURN as K_RETURN
from com.sun.star.awt.InvalidateStyle import UPDATE as IS_UPDATE, CHILDREN as IS_CHILDREN

class lirecouleurView(unohelper.Base, XWindowListener, XActionListener, XMouseListener):
    """ LireCouleur view. """
    LR_MARGIN = 3
    TB_MARGIN = 3
    BUTTON_SEP = 2
    BUTTON_SZ = 32
    
    def __init__(self, ctx, model, frame, parent):
        self.model = model
        self.parent = parent
        self.controller = frame.getController()
        self.ctx = ctx
        self._context_menu = None
        self.popupMenuSourceLabel = None
        self.container = None
        self.width = 200
        self.height = 500
        
        self.settings = Settings(ctx)
        self.FPossibles = self.settings.get("__fonctions_possibles__")
        self.FChoisies = [self.settings.get(fct)[2] for fct in self.FPossibles]
        self.TaillIco = self.settings.get('__taille_icones__')
        self.BUTTON_SZ = self.TaillIco
        
        try:
            self._create_view()
        except Exception as e:
            print(("Failed to create LireCouleur view: %s" % e))
        parent.addWindowListener(self)
    
    def _create_view(self):
        LR_MARGIN = self.LR_MARGIN
        TB_MARGIN = self.TB_MARGIN
        BUTTON_SEP = self.BUTTON_SEP
        BUTTON_SZ = self.BUTTON_SZ
        WIDTH = self.width
        HEIGHT = self.height

        self.fbuttons = []        
        self.container = create_container(self.ctx, self.parent, ("BackgroundColor",), (get_backgroundcolor(self.parent),))

        # bouton de validation
        posMaxY = HEIGHT-TB_MARGIN-BUTTON_SZ
        self.edbtn = create_uno_service('com.sun.star.awt.UnoControlButton')
        btn_model = create_uno_service('com.sun.star.awt.UnoControlButtonModel')
        btn_model.setPropertyValues( ('Label',), ("Editer",) )
        self.edbtn.setModel(btn_model)
        self.edbtn.setPosSize(LR_MARGIN, posMaxY, 64, 32, PS_POSSIZE)
        self.container.addControl("edit_lcbar", self.edbtn)
        self.edbtn.setActionCommand("edit_lcbar")
        self.edbtn.addActionListener(self)

        self.plusbtn = create_uno_service('com.sun.star.awt.UnoControlButton')
        btn_model = create_uno_service('com.sun.star.awt.UnoControlButtonModel')
        btn_model.setPropertyValues( ('Label',), ("+",) )
        self.plusbtn.setModel(btn_model)
        self.plusbtn.setPosSize(LR_MARGIN+16+BUTTON_SEP, posMaxY, 32, 32, PS_POSSIZE)
        self.container.addControl("plus_lcbar", self.plusbtn)
        self.plusbtn.setActionCommand("plus_lcbar")
        self.plusbtn.addActionListener(self)

        self.moinsbtn = create_uno_service('com.sun.star.awt.UnoControlButton')
        btn_model = create_uno_service('com.sun.star.awt.UnoControlButtonModel')
        btn_model.setPropertyValues( ('Label',), ("-",) )
        self.moinsbtn.setModel(btn_model)
        self.moinsbtn.setPosSize(LR_MARGIN+64+2*BUTTON_SEP+32, posMaxY, 32, 32, PS_POSSIZE)
        self.container.addControl("moins_lcbar", self.moinsbtn)
        self.moinsbtn.setActionCommand("moins_lcbar")
        self.moinsbtn.addActionListener(self)

        # création des boutons pour les fonctions sélectionnées
        posX = LR_MARGIN
        posY = TB_MARGIN
        for fct in self.FPossibles:
            sting = self.settings.get(fct)
            img = sting[0]
            btn = create_uno_service('com.sun.star.awt.UnoControlImageControl')
            btn_model = create_uno_service('com.sun.star.awt.UnoControlImageControlModel')
            btn_model.setPropertyValues( ('ImageURL','ScaleImage','ScaleMode','HelpText','Name'),
                        ("vnd.sun.star.extension://"+EXT_ID+"/images/"+img,True,1,sting[1],fct,) )
            btn.setModel(btn_model)
            btn.setPosSize(posX, posY, BUTTON_SZ, BUTTON_SZ, PS_POSSIZE)
            self.container.addControl(fct, btn)
            self.fbuttons.append(btn)
            btn.addMouseListener(self)
            posX += (BUTTON_SZ+BUTTON_SEP)
            if (posX+BUTTON_SZ) > WIDTH:
                posY += (BUTTON_SZ+BUTTON_SEP)
                posX = LR_MARGIN
        
    def _update_view(self):
        LR_MARGIN = self.LR_MARGIN
        TB_MARGIN = self.TB_MARGIN
        BUTTON_SEP = self.BUTTON_SEP
        BUTTON_SZ = self.BUTTON_SZ
        WIDTH = self.width
        HEIGHT = self.height

        # mie à jour des boutons d'après les fonctions sélectionnées
        ps = self.edbtn.getPosSize()
        posMaxY = HEIGHT-TB_MARGIN-ps.Height
        self.edbtn.setPosSize(LR_MARGIN, posMaxY, ps.Width, ps.Height, PS_POSSIZE)
        self.plusbtn.setPosSize(LR_MARGIN+ps.Width+BUTTON_SEP, posMaxY, 32, 32, PS_POSSIZE)
        ps = self.edbtn.getPosSize()
        self.moinsbtn.setPosSize(LR_MARGIN+ps.Width+2*BUTTON_SEP+32, posMaxY, 32, 32, PS_POSSIZE)

        posX = LR_MARGIN
        posY = TB_MARGIN
        i = 0
        for btn in self.fbuttons:
            ps = btn.getPosSize()
            if self.FChoisies[i]:
                btn.setVisible(True)
                btn.setPosSize(posX, posY, BUTTON_SZ, BUTTON_SZ, PS_POSSIZE)

                posX += (BUTTON_SZ+BUTTON_SEP)
                if (posX+BUTTON_SZ) > self.width:
                    posX = LR_MARGIN
                    posY += (BUTTON_SZ+BUTTON_SEP)
            else:
                btn.setVisible(False)
            i += 1

    # XEventListener
    def disposing(self, ev):
        self.editContainer = None
        self.container = None
        self.model = None
        self._context_menu = None
    
    # XWindowListener
    def windowHidden(self, ev): pass
    def windowShown(self, ev): pass
    def windowMoved(self, ev): pass
    def windowResized(self, ev):
        ps = ev.Source.getPosSize()
        self.width = ps.Width
        self.height = ps.Height
        self._update_view()

    # XMouseListener
    def mouseEntered(self, ev):
        btn_model = ev.Source.Model
        btn_model.setPropertyValues( ('BackgroundColor',), (0xffffff,) )
    def mouseExited(self, ev):
        btn_model = ev.Source.Model
        btn_model.setPropertyValues( ('BackgroundColor',), (get_backgroundcolor(self.parent),) )
    def mousePressed(self, ev):
        if ev.Buttons == MB_LEFT and ev.ClickCount == 1:
            img = ev.Source.Model.ImageURL
            limg = ["vnd.sun.star.extension://"+EXT_ID+"/images/"+self.settings.get(cmd)[0] for cmd in self.FPossibles]
            try:
                cmd = self.FPossibles[limg.index(img)]
                desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
                xDocument = desktop.getCurrentComponent()
                if cmd == 'StylePhonemes':
                    __lirecouleur_phonemes__(xDocument)
                elif cmd == 'StyleNoir':
                    __lirecouleur_noir__(xDocument)
                elif cmd == 'ConfusionLettres':
                    __lirecouleur_confusion_lettres__(xDocument)
                elif cmd == 'ConsonneVoyelle':
                    __lirecouleur_consonne_voyelle__(xDocument)
                elif cmd == 'StyleCouleurMots':
                    __lirecouleur_couleur_mots__(xDocument)
                elif cmd == 'StyleSepareMots':
                    __lirecouleur_separe_mots__(xDocument)
                elif cmd == 'StyleDefaut':
                    __lirecouleur_defaut__(xDocument)
                elif cmd == 'StyleEspace':
                    __lirecouleur_espace__(xDocument)
                elif cmd == 'StylePara':
                    __lirecouleur_espace_lignes__(xDocument)
                elif cmd == 'StyleExtraLarge':
                    __lirecouleur_extra_large__(xDocument)
                elif cmd == 'StyleLMuettes':
                    __lirecouleur_l_muettes__(xDocument)
                elif cmd == 'StyleLarge':
                    __lirecouleur_large__(xDocument)
                elif cmd == 'StyleLiaisons':
                    __lirecouleur_liaisons__(xDocument)
                elif cmd == 'StyleLignesAlternees':
                    __lirecouleur_lignes__(xDocument)
                elif cmd == 'StylePhonMuet':
                    __lirecouleur_phon_muet__(xDocument)
                elif cmd == 'StyleGraphemesComplexes':
                    __lirecouleur_graphemes_complexes__(xDocument)
                elif cmd == 'StylePonctuation':
                    __lirecouleur_ponctuation__(xDocument)
                elif cmd == 'StyleSepareMots':
                    __lirecouleur_separe_mots__(xDocument)
                elif cmd == 'SupprimerDecos':
                    __lirecouleur_suppr_decos__(xDocument)
                elif cmd == 'SupprimerSyllabes':
                    __lirecouleur_suppr_syllabes__(xDocument)
                elif cmd == 'StyleSyllabes':
                    __lirecouleur_syllabes__(xDocument)
                elif cmd == 'StyleSyllDys':
                    __lirecouleur_syllabes__(xDocument, 'dys')
                elif cmd == 'NewLireCouleurDocument':
                    __new_lirecouleur_document__(xDocument, self.ctx)
                elif cmd == 'StylePhonemesAlternes':
                    __lirecouleur_alterne_phonemes__(xDocument)
            except:
                pass

    def mouseReleased(self, ev): pass

    # XActionListener
    def actionPerformed(self, ev):
        cmd = ev.ActionCommand
        if cmd == 'edit_lcbar':
            self.editLCBar()
        elif cmd == 'plus_lcbar':
            if self.BUTTON_SZ < 64:
                # éviter d'avoir des icones trop grosses
                self.BUTTON_SZ += 2
                self.settings.configure(("__taille_icones__",), (self.BUTTON_SZ,))
                self._update_view()
        elif cmd == 'moins_lcbar':
            if self.BUTTON_SZ > 16:
                # éviter d'avoir des icones trop petites
                self.BUTTON_SZ -= 2
                self.settings.configure(("__taille_icones__",), (self.BUTTON_SZ,))
                self._update_view()
        elif cmd == 'valid':
            i = 0
            for checker in self.checkList:
                sting = self.settings.get(self.FPossibles[i])
                self.FChoisies[i] = checker.State
                sting[2] = str(self.FChoisies[i])
                self.settings.configure((self.FPossibles[i],), (':'.join(sting),))
                i += 1
            self.editContainer.endExecute()
            self._update_view()
        
    def editLCBar(self):
        smgr = self.ctx.ServiceManager
        dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", self.ctx)
        
        dialogModel.PositionX = 100
        dialogModel.PositionY = 50
        dialogModel.Width = 180
        dialogModel.Height = 284
        dialogModel.Title = "Choisir les fonctions LireCouleur"

        validBtn = dialogModel.createInstance('com.sun.star.awt.UnoControlButtonModel')
        validBtn.Label = "Valider"
        validBtn.Width = 50
        validBtn.Height = 20
        validBtn.PositionX = (dialogModel.Width-validBtn.Width)/2
        validBtn.PositionY = dialogModel.Height-validBtn.Height-2
        validBtn.Name = "valid"
        dialogModel.insertByName(validBtn.Name, validBtn)
        
        sz_button = 24
        nb_col = int(len(self.FPossibles)*(sz_button+2) / validBtn.PositionY + 1)
        sz_col = dialogModel.Width/nb_col
        posX = self.LR_MARGIN
        posY = self.TB_MARGIN
        self.checkList = []
        i = 0
        for fct in self.FPossibles:
            try:
                img = self.settings.get(fct)[0]
                labelEsp = dialogModel.createInstance("com.sun.star.awt.UnoControlImageControlModel")
                labelEsp.PositionX = posX
                labelEsp.PositionY = posY
                labelEsp.Width  = sz_button
                labelEsp.Height = sz_button
                labelEsp.HelpText = self.settings.get(fct)[1]
                labelEsp.Name = fct+'img'
                labelEsp.ImageURL = "vnd.sun.star.extension://"+EXT_ID+"/images/"+img
                labelEsp.ScaleImage = True
                labelEsp.ScaleMode = 1
                dialogModel.insertByName(labelEsp.Name, labelEsp)

                checkBP = dialogModel.createInstance("com.sun.star.awt.UnoControlCheckBoxModel")
                checkBP.PositionX = posX+sz_button
                checkBP.PositionY = posY
                checkBP.Width  = 10
                checkBP.Height = 10
                checkBP.Name = fct
                checkBP.State = self.FChoisies[i]
                checkBP.Label = ''
                dialogModel.insertByName(checkBP.Name, checkBP)
                self.checkList.append(checkBP)

                posY += (sz_button + 2)
                if (posY+sz_button) > validBtn.PositionY:
                    posX += sz_col
                    posY = self.TB_MARGIN
                    
                i += 1
            except:
                pass

        # create the dialog control and set the model
        controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", self.ctx)
        controlContainer.setModel(dialogModel)
        self.editContainer = controlContainer
        
        validCtrl = controlContainer.getControl("valid")
        validCtrl.setActionCommand(validBtn.Name)
        validCtrl.addActionListener(self)

        # create a peer
        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", self.ctx)

        controlContainer.setVisible(False);
        controlContainer.createPeer(toolkit, None);

        # execute it
        controlContainer.execute()

        # dispose the dialog
        controlContainer.dispose()
