#!/usr/bin/env python
# -*- coding: UTF-8 -*-

###################################################################################
# Macro destinée à l'affichage de textes en couleur et à la segmentation
# de mots en syllabes
#
# voir http://lirecouleur.arkaline.fr
#
# @author Marie-Pierre Brungard
# @version 4.0.0
# @since 2017
#
# GNU General Public Licence (GPL) version 3
#
# LireCouleur is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
# LireCouleur is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# LireCouleur; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
###################################################################################

import uno
import unohelper
import traceback
import sys
import os
import gettext
from gettext import gettext as _
from com.sun.star.awt import (XWindowListener, XActionListener, XMouseListener)
from com.sun.star.task import XJobExecutor
from com.sun.star.task import XJob

from com.sun.star.awt import XKeyHandler
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
from com.sun.star.awt import Rectangle
from com.sun.star.awt.KeyModifier import MOD2
from com.sun.star.awt.Key import LEFT as keyLeft
from com.sun.star.awt.Key import RIGHT as keyRight

try:
    # nécessaire pour Python 3
    from functools import reduce
except:
    pass
import string
import re
from lirecouleur.lirecouleur import *
from lirecouleur.utils import (Settings, create_uno_service, create_uno_struct)
from lirecouleur.lirecouleurui import (i18n,__lirecouleur_phonemes__,__lirecouleur_noir__,__lirecouleur_bdpq__,
        __lirecouleur_consonne_voyelle__,__lirecouleur_couleur_mots__,__lirecouleur_defaut__,__lirecouleur_espace__,
        __lirecouleur_espace_lignes__,__lirecouleur_extra_large__,__lirecouleur_l_muettes__,__lirecouleur_large__,
        __lirecouleur_liaisons__,__lirecouleur_lignes__,__lirecouleur_phon_muet__,__lirecouleur_phonemes_complexes__,
        __lirecouleur_phrase__,__lirecouleur_separe_mots__,__lirecouleur_suppr_decos__,__lirecouleur_suppr_syllabes__,
        __lirecouleur_syllabes__,__arret_dynsylldys__,__new_lirecouleur_document__,getLirecouleurDirectory,
        getLirecouleurDictionary,__lirecouleur_dynsylldys__, importStylesLireCouleur)

######################################################################################
# Gestionnaire d'événement de la boite de dialogue
######################################################################################
class MyActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer, checkListPhonemes, fieldCoul, fieldEsp, checkPoint,
                    selectTyp1Syll, selectTyp2Syll, selectLoc, fieldTemp):
        self.controlContainer = controlContainer
        self.checkListPhonemes = checkListPhonemes
        self.fieldCoul = fieldCoul
        self.fieldEsp = fieldEsp
        self.checkPoint = checkPoint
        self.selectTyp1Syll = selectTyp1Syll
        self.selectTyp2Syll = selectTyp2Syll
        self.selectLocale = selectLoc
        self.fieldTemp = fieldTemp

    def actionPerformed(self, actionEvent):
        global __style_phon_perso__
        
        settings = Settings()

        selectphonemes = settings.get('__selection_phonemes__')
        nbcouleurs = settings.get('__alternate__')
        nbespaces = settings.get('__subspaces__')
        tempFilename = settings.get('__template__')

        selectphonemes['a'] = self.checkListPhonemes['checkA'].State
        selectphonemes['e'] = selectphonemes['e_comp'] = self.checkListPhonemes['checkE'].State
        selectphonemes['e^'] = selectphonemes['e^_comp'] = self.checkListPhonemes['checkEt'].State
        selectphonemes['q'] = self.checkListPhonemes['checkQ'].State
        selectphonemes['u'] = self.checkListPhonemes['checkU'].State
        selectphonemes['i'] = self.checkListPhonemes['checkI'].State
        selectphonemes['y'] = self.checkListPhonemes['checkY'].State
        selectphonemes['o'] = selectphonemes['o_comp'] = selectphonemes['o_ouvert'] = self.checkListPhonemes['checkO'].State

        selectphonemes['x'] = selectphonemes['x^'] = self.checkListPhonemes['checkEu'].State
        selectphonemes['a~'] = self.checkListPhonemes['checkAn'].State
        selectphonemes['e~'] = selectphonemes['x~'] = self.checkListPhonemes['checkIn'].State
        selectphonemes['o~'] = self.checkListPhonemes['checkOn'].State
        selectphonemes['w'] = selectphonemes['wa'] = selectphonemes['w5'] = self.checkListPhonemes['checkW'].State
        selectphonemes['j'] = self.checkListPhonemes['checkJ'].State

        selectphonemes['n'] = self.checkListPhonemes['checkN'].State
        selectphonemes['g~'] = self.checkListPhonemes['checkNg'].State
        selectphonemes['n~'] = self.checkListPhonemes['checkGn'].State

        selectphonemes['l'] = self.checkListPhonemes['checkL'].State
        selectphonemes['m'] = self.checkListPhonemes['checkM'].State
        selectphonemes['r'] = self.checkListPhonemes['checkR'].State

        selectphonemes['v'] = self.checkListPhonemes['checkV'].State
        selectphonemes['z'] = selectphonemes['z_s'] = self.checkListPhonemes['checkZ'].State
        selectphonemes['z^'] = selectphonemes['z^_g'] = self.checkListPhonemes['checkGe'].State

        selectphonemes['f'] = selectphonemes['f_ph'] = self.checkListPhonemes['checkF'].State
        selectphonemes['s'] = selectphonemes['s_c'] = selectphonemes['s_t'] = self.checkListPhonemes['checkS'].State
        selectphonemes['s^'] = self.checkListPhonemes['checkCh'].State

        selectphonemes['p'] = self.checkListPhonemes['checkP'].State
        selectphonemes['t'] = self.checkListPhonemes['checkT'].State
        selectphonemes['k'] = selectphonemes['k_qu'] = self.checkListPhonemes['checkK'].State

        selectphonemes['b'] = self.checkListPhonemes['checkB'].State
        selectphonemes['d'] = self.checkListPhonemes['checkD'].State
        selectphonemes['g'] = selectphonemes['g_u'] = self.checkListPhonemes['checkG'].State

        selectphonemes['ks'] = self.checkListPhonemes['checkKS'].State
        selectphonemes['gz'] = self.checkListPhonemes['checkGZ'].State

        selectphonemes['#'] = selectphonemes['q_caduc'] = self.checkListPhonemes['checkH'].State

        nbcouleurs = self.fieldCoul.getValue()
        nbespaces = self.fieldEsp.getValue()
        tempFilename = self.fieldTemp.getText()

        settings.setValue('__selection_phonemes__', selectphonemes)
        settings.setValue('__alternate__', int(nbcouleurs))
        settings.setValue('__subspaces__', int(nbespaces))
        settings.setValue('__point__', self.checkPoint.getState())

        settings.setValue('__syllo__', (self.selectTyp1Syll.getSelectedItemPos(), self.selectTyp2Syll.getSelectedItemPos()))
        settings.setValue('__template__', tempFilename)
        settings.setValue('__locale__', self.selectLocale.getSelectedItem())

        self.controlContainer.endExecute()

class MySetActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer, checkListPhonemes):
        self.controlContainer = controlContainer
        self.checkListPhonemes = checkListPhonemes

    def actionPerformed(self, actionEvent):
        listPhonemes = ['checkA', 'checkE', 'checkEt', 'checkQ', 'checkI',
                        'checkU', 'checkY', 'checkO', 'checkEu',
                        'checkAn', 'checkIn', 'checkOn', 'checkW',
                        'checkJ', 'checkN', 'checkNg', 'checkGn', 'checkB', 'checkD', 'checkG',
                        'checkL', 'checkM', 'checkR', 'checkV', 'checkZ', 'checkGe',
                        'checkF', 'checkS', 'checkCh', 'checkP', 'checkT', 'checkK',
                        'checkKS','checkGZ', 'checkH']
        for phon in listPhonemes:
            self.checkListPhonemes[phon].State = 1

class MyUnsetActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer, checkListPhonemes):
        self.controlContainer = controlContainer
        self.checkListPhonemes = checkListPhonemes

    def actionPerformed(self, actionEvent):
        listPhonemes = ['checkA', 'checkE', 'checkEt', 'checkQ', 'checkI',
                        'checkU', 'checkY', 'checkO', 'checkEu',
                        'checkAn', 'checkIn', 'checkOn', 'checkW',
                        'checkJ', 'checkN', 'checkNg', 'checkGn', 'checkB', 'checkD', 'checkG',
                        'checkL', 'checkM', 'checkR', 'checkV', 'checkZ', 'checkGe',
                        'checkF', 'checkS', 'checkCh', 'checkP', 'checkT', 'checkK',
                        'checkKS','checkGZ', 'checkH']
        for phon in listPhonemes:
            self.checkListPhonemes[phon].State = 0

class TemplateActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer, fieldTemp, xContext):
        self.controlContainer = controlContainer
        self.fieldTemp = fieldTemp
        self.xContext = xContext

    def actionPerformed(self, actionEvent):
        # Get the service manager
        smgr = self.xContext.ServiceManager

        # create the dialog model and set the properties
        oFilePicker = smgr.createInstanceWithContext("com.sun.star.ui.dialogs.FilePicker", self.xContext)
        #oFilePicker.DisplayDirectory = getUserDir()
        oFilePicker.appendFilter("Documents", "*.odt")
        oFilePicker.appendFilter("OTT", "*.ott")
        oFilePicker.CurrentFilter = "Documents"

        if oFilePicker.execute():
            sFiles = oFilePicker.getFiles()
            sFileURL = sFiles[0]
            self.fieldTemp.setText(sFileURL)

######################################################################################
# Création d'une checkbox (pour 1 phonème) dans la boite de dialogue
######################################################################################
def createCheckBox(dialogModel, px, py, name, index, label, etat, w=58):
    checkBP = dialogModel.createInstance("com.sun.star.awt.UnoControlCheckBoxModel")
    checkBP.PositionX = px
    checkBP.PositionY = py
    checkBP.Width  = w
    checkBP.Height = 10
    checkBP.Name = name
    checkBP.TabIndex = index
    checkBP.State = etat
    checkBP.Label = label
    dialogModel.insertByName(checkBP.Name, checkBP)

    return checkBP

######################################################################################
# Création d'une checkbox (pour 1 phonème) dans la boite de dialogue
######################################################################################
def createNumericField(dialogModel, px, py, name, index, val, w=20):
    checkNF = dialogModel.createInstance("com.sun.star.awt.UnoControlNumericFieldModel")
    checkNF.PositionX = px
    checkNF.PositionY = py
    checkNF.Width  = w
    checkNF.Height = 10
    checkNF.Name = name
    checkNF.TabIndex = index
    checkNF.Value = val
    checkNF.ValueMin = 2
    checkNF.ValueMax = 10
    checkNF.ValueStep = 1
    checkNF.Spin = True
    checkNF.DecimalAccuracy = 0
    return checkNF

######################################################################################
# Création d'une boite de dialogue pour sélectionner les phonèmes à visualiser
######################################################################################
class GestionnaireConfiguration(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __gestionnaire_config_dialog__(desktop.getCurrentComponent(), self.ctx)

def gestionnaire_config_dialog( args=None ):
    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    __gestionnaire_config_dialog__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __gestionnaire_config_dialog__(xDocument, xContext):
    __arret_dynsylldys__(xDocument)

    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    import array
    
    # récupération des infos de configuration
    settings = Settings()

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # read the already selected phonemes in the .lirecouleur file
    selectphonemes = settings.get('__selection_phonemes__')

    # lecture de la période d'alternance de lignes
    nbcouleurs = settings.get('__alternate__')

    # lecture du nombre d'espaces entre mots
    nbespaces = settings.get('__subspaces__')

    # lecture pour savoir s'il faut mettre un point sous les lettres muettes
    selectpoint = settings.get('__point__')

    # lecture pour savoir comment il faut afficher les syllabes
    selectsyllo = settings.get('__syllo__')

    # lecture pour savoir  dans le fichier .lirecouleur
    select_locale = settings.get('__locale__')

    # lecture de la période d'alternance de lignes
    tempFileName = settings.get('__template__')

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 100
    dialogModel.PositionY = 50
    dialogModel.Width = 180
    dialogModel.Height = 284
    dialogModel.Title = _("Configuration LireCouleur")
    
    # créer le label titre
    labelTitre = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelTitre.PositionX = 10
    labelTitre.PositionY = 2
    labelTitre.Width  = 130
    labelTitre.Height = 12
    labelTitre.Name = "labelTitre"
    labelTitre.TabIndex = 1
    labelTitre.Label = _(u("Cocher les phonèmes à mettre en évidence"))

    # créer les checkboxes des phonèmes
    i = 2
    checkA = createCheckBox(dialogModel, 10, 30, "checkA", i, u('[~a] ta'), selectphonemes['a'])
    i += 1
    checkQ = createCheckBox(dialogModel, 10, 40, "checkQ", i, u('[~e] le'), selectphonemes['q'])
    i += 1
    checkI = createCheckBox(dialogModel, 10, 50, "checkI", i, u('[~i] il'), selectphonemes['i'])
    i += 1
    checkY = createCheckBox(dialogModel, 10, 60, "checkY", i, u('[~y] tu'), selectphonemes['y'])
    i += 1

    checkU = createCheckBox(dialogModel, 70, 30, "checkU", i, u('[~u] fou'), selectphonemes['u'])
    i += 1
    checkE = createCheckBox(dialogModel, 70, 40, "checkE", i, u('[~é] né'), selectphonemes['e'])
    i += 1
    checkO = createCheckBox(dialogModel, 70, 50, "checkO", i, u('[~o] mot'), selectphonemes['o'])
    i += 1
    checkEt = createCheckBox(dialogModel, 70, 60, "checkEt", i, u('[~è] sel'), selectphonemes['e^'])
    i += 1
    checkAn = createCheckBox(dialogModel, 70, 70, "checkAn", i, u('[~an] grand'), selectphonemes['a~'])
    i += 1

    checkOn = createCheckBox(dialogModel, 130, 30, "checkOn", i, u('[~on] son'), selectphonemes['o~'])
    i += 1
    checkEu = createCheckBox(dialogModel, 130, 40, "checkEu", i, u('[~x] feu'), selectphonemes['x'])
    i += 1
    checkIn = createCheckBox(dialogModel, 130, 50, "checkIn", i, u('[~in] fin'), selectphonemes['e~'])
    i += 1
    checkW = createCheckBox(dialogModel, 130, 60, "checkW", i, u('[~w] noix'), selectphonemes['w'])
    i += 1
    checkJ = createCheckBox(dialogModel, 130, 70, "checkJ", i, u('[~j] fille'), selectphonemes['j'])
    i += 1

    checkNg = createCheckBox(dialogModel, 10, 75, "checkNg", i, u('[~ng] parking'), selectphonemes['g~'])
    i += 1
    checkGn = createCheckBox(dialogModel, 10, 85, "checkGn", i, u('[~gn] ligne'), selectphonemes['n~'])
    i += 1

    checkH = createCheckBox(dialogModel, 70, 85, "checkH", i, u('[#] lettres muettes, e caduc'), selectphonemes['#'], 88)
    i += 1

    checkR = createCheckBox(dialogModel, 130, 95, "checkR", i, u('[~r] rat'), selectphonemes['r'])
    i += 1
    checkL = createCheckBox(dialogModel, 10, 105, "checkL", i, u('[~l] ville'), selectphonemes['l'])
    i += 1
    checkM = createCheckBox(dialogModel, 70, 105, "checkM", i, u('[~m] mami'), selectphonemes['m'])
    i += 1
    checkN = createCheckBox(dialogModel, 130, 105, "checkN", i, u('[~n] âne'), selectphonemes['n'])
    i += 1

    checkV = createCheckBox(dialogModel, 10, 115, "checkV", i, u('[~v] vélo'), selectphonemes['v'])
    i += 1
    checkZ = createCheckBox(dialogModel, 70, 115, "checkZ", i, u('[~z] zoo'), selectphonemes['z'])
    i += 1
    checkGe = createCheckBox(dialogModel, 130, 115, "checkGe", i, u('[~ge] jupe'), selectphonemes['z^'])
    i += 1

    checkF = createCheckBox(dialogModel, 10, 125, "checkF", i, u('[~f] effacer'), selectphonemes['f'])
    i += 1
    checkS = createCheckBox(dialogModel, 70, 125, "checkS", i, u('[~s] scie'), selectphonemes['s'])
    i += 1
    checkCh = createCheckBox(dialogModel, 130, 125, "checkCh", i, u('[c~h] chat'), selectphonemes['s^'])
    i += 1

    checkP = createCheckBox(dialogModel, 10, 135, "checkP", i, u('[~p] papa'), selectphonemes['p'])
    i += 1
    checkT = createCheckBox(dialogModel, 70, 135, "checkT", i, u('[~t] tortue'), selectphonemes['t'])
    i += 1
    checkK = createCheckBox(dialogModel, 130, 135, "checkK", i, u('[~k] coq'), selectphonemes['k'])
    i += 1

    checkB = createCheckBox(dialogModel, 10, 145, "checkB", i, u('[~b] bébé'), selectphonemes['b'])
    i += 1
    checkD = createCheckBox(dialogModel, 70, 145, "checkD", i, u('[~d] dindon'), selectphonemes['d'])
    i += 1
    checkG = createCheckBox(dialogModel, 130, 145, "checkG", i, u('[~g] gare'), selectphonemes['g'])
    i += 1

    checkKS = createCheckBox(dialogModel, 70, 155, "checkKS", i, u('[ks] ksi'), selectphonemes['ks'])
    i += 1
    checkGZ = createCheckBox(dialogModel, 130, 155, "checkGZ", i, u('[gz] exact'), selectphonemes['gz'])
    i += 1

    labelListLocale = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelListLocale.PositionX = 10
    labelListLocale.PositionY = checkKS.PositionY+checkKS.Height+2
    labelListLocale.Width  = 50
    labelListLocale.Height = checkKS.Height
    labelListLocale.Name = "labelListLocale"
    labelListLocale.TabIndex = 1
    labelListLocale.Label = "Configuration : "

    listLocale = dialogModel.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listLocale.PositionX = labelListLocale.PositionX+labelListLocale.Width
    listLocale.PositionY = labelListLocale.PositionY
    listLocale.Width  = 50
    listLocale.Height  = checkKS.Height
    listLocale.Name = "listLocale"
    listLocale.TabIndex = 1
    listLocale.Dropdown = True
    listLocale.MultiSelection = False
    listLocale.StringItemList = ("fr", "fr_CA", )
    if select_locale in listLocale.StringItemList:
        listLocale.SelectedItems = (listLocale.StringItemList.index(select_locale),)
    else:
        listLocale.SelectedItems = (0,)

    checkListPhonemes = {'checkA':None, 'checkE':None, 'checkEt':None, 'checkQ':None, 'checkI':None,
                        'checkU':None, 'checkY':None, 'checkO':None, 'checkEu':None,
                        'checkAn':None, 'checkIn':None, 'checkOn':None, 'checkW':None,
                        'checkJ':None, 'checkCh':None, 'checkN':None, 'checkNg':None, 'checkGn':None,
                        'checkL':None, 'checkM':None, 'checkR':None,
                        'checkV':None, 'checkZ':None, 'checkGe':None,
                        'checkF':None, 'checkS':None, 'checkCh':None,
                        'checkP':None, 'checkT':None, 'checkK':None,
                        'checkB':None, 'checkD':None, 'checkG':None,
                        'checkKS':None, 'checkGZ':None, 'checkH':None}

    # create the button model and set the properties
    buttonModel = dialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")

    buttonModel.PositionX = 65
    buttonModel.Width = 50
    buttonModel.Height = 14
    buttonModel.PositionY  = dialogModel.Height-buttonModel.Height-2
    buttonModel.Name = "myButtonName"
    buttonModel.TabIndex = 0
    buttonModel.Label = _(u("Valider"))

    # create the button model and set the properties
    setAllModel = dialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
    setAllModel.PositionX = 25
    setAllModel.PositionY  = 12
    setAllModel.Width = 60
    setAllModel.Height = 14
    setAllModel.Name = "setAllButtonName"
    setAllModel.TabIndex = 0
    setAllModel.Label = _(u("Tout sélectionner"))

    unsetAllModel = dialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
    unsetAllModel.PositionX = 87
    unsetAllModel.PositionY  = 12
    unsetAllModel.Width = 60
    unsetAllModel.Height = 14
    unsetAllModel.Name = "unsetAllButtonName"
    unsetAllModel.TabIndex = 0
    unsetAllModel.Label = _(u("Tout désélectionner"))

    sep1 = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedLineModel")
    sep1.PositionX = 2
    sep1.PositionY = listLocale.PositionY+listLocale.Height+2
    sep1.Width  = dialogModel.Width - 4
    sep1.Height  = 5
    sep1.Name = "sep1"
    sep1.TabIndex = 1

    labelCoul = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelCoul.PositionX = 10
    labelCoul.PositionY = sep1.PositionY+sep1.Height+2
    labelCoul.Width  = 145
    labelCoul.Height = 12
    labelCoul.Name = "labelCoul"
    labelCoul.TabIndex = 1
    labelCoul.Label = _(u("Période d'alternance des couleurs (lignes, syllabes) :"))
    fieldCoul = createNumericField(dialogModel, labelCoul.PositionX+labelCoul.Width, labelCoul.PositionY, "fieldCoul", 0, nbcouleurs)

    labelEsp = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelEsp.PositionX = 10
    labelEsp.PositionY = fieldCoul.PositionY+fieldCoul.Height
    labelEsp.Width  = 105
    labelEsp.Height = 12
    labelEsp.Name = "labelEsp"
    labelEsp.TabIndex = 1
    labelEsp.Label = _(u("Nombre d'espaces entre deux mots :"))
    fieldEsp = createNumericField(dialogModel, labelEsp.PositionX+labelEsp.Width, labelEsp.PositionY, "fieldEsp", 0, nbespaces)

    sep2 = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedLineModel")
    sep2.PositionX = sep1.PositionX
    sep2.PositionY = labelEsp.PositionY+labelEsp.Height
    sep2.Width  = sep1.Width
    sep2.Height  = sep1.Height
    sep2.Name = "sep2"
    sep2.TabIndex = 1

    checkPoint = createCheckBox(dialogModel, 10, sep2.PositionY+sep2.Height, "checkPoint", 0,
                    _(u("Placer des symboles sous certains sons")), selectpoint, dialogModel.Width-10)

    labelRadio = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelRadio.PositionX = 10
    labelRadio.PositionY = checkPoint.PositionY+checkPoint.Height+2
    labelRadio.Width  = dialogModel.Width-100-12
    labelRadio.Height = 10
    labelRadio.Name = "labelRadio"
    labelRadio.TabIndex = 1
    labelRadio.Label = _(u("Souligner les syllabes"))

    listTyp1Syll = dialogModel.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listTyp1Syll.PositionX = labelRadio.PositionX+labelRadio.Width
    listTyp1Syll.PositionY = labelRadio.PositionY-2
    listTyp1Syll.Width  = 50
    listTyp1Syll.Height  = 12
    listTyp1Syll.Name = "listTyp1Syll"
    listTyp1Syll.TabIndex = 1
    listTyp1Syll.Dropdown = True
    listTyp1Syll.MultiSelection = False
    listTyp1Syll.StringItemList = ("LireCouleur", "standard", )
    if selectsyllo[0] in [0, 1]:
        listTyp1Syll.SelectedItems = (selectsyllo[0],)
    else:
        listTyp1Syll.SelectedItems = (0,)

    listTyp2Syll = dialogModel.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listTyp2Syll.PositionX = listTyp1Syll.PositionX+listTyp1Syll.Width
    listTyp2Syll.PositionY = listTyp1Syll.PositionY
    listTyp2Syll.Width  = 50
    listTyp2Syll.Height  = listTyp1Syll.Height
    listTyp2Syll.Name = "listTyp2Syll"
    listTyp2Syll.TabIndex = 1
    listTyp2Syll.Dropdown = True
    listTyp2Syll.MultiSelection = False
    listTyp2Syll.StringItemList = ( _(u("écrites")), _(u("orales")) )
    if selectsyllo[1] in [0, 1]:
        listTyp2Syll.SelectedItems = (selectsyllo[1],)
    else:
        listTyp2Syll.SelectedItems = (0,)

    sep3 = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedLineModel")
    sep3.PositionX = sep1.PositionX
    sep3.PositionY = labelRadio.PositionY+labelRadio.Height+2
    sep3.Width  = sep1.Width
    sep3.Height  = sep1.Height
    sep3.Name = "sep3"
    sep3.TabIndex = 1

    labelTemp = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelTemp.PositionX = 10
    labelTemp.PositionY = sep3.PositionY+sep3.Height
    labelTemp.Width  = dialogModel.Width-12
    labelTemp.Height = 10
    labelTemp.Name = "labelTemp"
    labelTemp.TabIndex = 1
    labelTemp.Label = _(u("Nom du fichier modèle :"))

    fieldTemp = dialogModel.createInstance("com.sun.star.awt.UnoControlEditModel")
    fieldTemp.PositionX = 10
    fieldTemp.PositionY  = labelTemp.PositionY+labelTemp.Height
    fieldTemp.Width = dialogModel.Width-42
    fieldTemp.Height = 14
    fieldTemp.Name = "fieldTemp"
    fieldTemp.TabIndex = 0

    buttTemp = dialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
    buttTemp.PositionX = fieldTemp.PositionX+fieldTemp.Width+2
    buttTemp.PositionY  = fieldTemp.PositionY
    buttTemp.Width = dialogModel.Width-buttTemp.PositionX-2
    buttTemp.Height = fieldTemp.Height
    buttTemp.Name = "buttTemp"
    buttTemp.TabIndex = 0
    buttTemp.Label = "..."

    # insert the control models into the dialog model
    dialogModel.insertByName("setAllButtonName", setAllModel)
    dialogModel.insertByName("unsetAllButtonName", unsetAllModel)
    dialogModel.insertByName("myButtonName", buttonModel)
    dialogModel.insertByName("labelTitre", labelTitre)

    dialogModel.insertByName("labelCoul", labelCoul)
    dialogModel.insertByName("fieldCoul", fieldCoul)

    dialogModel.insertByName("labelEsp", labelEsp)
    dialogModel.insertByName("fieldEsp", fieldEsp)

    dialogModel.insertByName("sep1", sep1)
    dialogModel.insertByName("sep2", sep2)
    dialogModel.insertByName("sep3", sep3)

    dialogModel.insertByName(labelListLocale.Name, labelListLocale)
    dialogModel.insertByName(listLocale.Name, listLocale)

    dialogModel.insertByName("labelTemp", labelTemp)
    dialogModel.insertByName("fieldTemp", fieldTemp)
    dialogModel.insertByName("buttTemp", buttTemp)

    dialogModel.insertByName(labelRadio.Name, labelRadio)
    dialogModel.insertByName(listTyp1Syll.Name, listTyp1Syll)
    dialogModel.insertByName(listTyp2Syll.Name, listTyp2Syll)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    # add the action listener
    for k in checkListPhonemes:
        checkListPhonemes[k] = controlContainer.getControl(k)
    controlContainer.getControl("myButtonName").addActionListener(MyActionListener(controlContainer, checkListPhonemes,
                                controlContainer.getControl("fieldCoul"),
                                controlContainer.getControl("fieldEsp"),
                                controlContainer.getControl("checkPoint"),
                                controlContainer.getControl(listTyp1Syll.Name),
                                controlContainer.getControl(listTyp2Syll.Name),
                                controlContainer.getControl(listLocale.Name),
                                controlContainer.getControl("fieldTemp")))
    controlContainer.getControl("setAllButtonName").addActionListener(MySetActionListener(controlContainer, checkListPhonemes))
    controlContainer.getControl("unsetAllButtonName").addActionListener(MyUnsetActionListener(controlContainer, checkListPhonemes))
    controlContainer.getControl("buttTemp").addActionListener(TemplateActionListener(controlContainer, controlContainer.getControl("fieldTemp"), xContext))

    if len(tempFileName) > 0:
        controlContainer.getControl("fieldTemp").setText(tempFileName)

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

######################################################################################
# Création d'une boite de dialogue pour gérer le dictionnaire des décodages spéciaux
######################################################################################
def checkMethodParameter(interface_name, method_name, param_index, param_type):
    """ Check the method has specific type parameter at the specific position. """
    cr = create_uno_service("com.sun.star.reflection.CoreReflection")
    try:
        idl = cr.forName(interface_name)
        m = idl.getMethod(method_name)
        if m:
            info = m.getParameterInfos()[param_index]
            return info.aType.getName() == param_type
    except:
        pass
    return False

def MsgBox(parent, toolkit=None, message="message", title="", message_type="errorbox", buttons=BUTTONS_OK):
    """ Show message in message box. """
    if toolkit is None:
        toolkit = parent.getToolkit()
    older_imple = checkMethodParameter(
        "com.sun.star.awt.XMessageBoxFactory",
        "createMessageBox", 1, "com.sun.star.awt.Rectangle")

    if older_imple:
        msgboxdial = toolkit.createMessageBox(parent, Rectangle(), message_type, buttons, title, message)
    else:
        msgboxdial = toolkit.createMessageBox(parent, message_type, buttons, title, message)
    n = msgboxdial.execute()
    msgboxdial.dispose()
    return n

class DictListActionListener(unohelper.Base, XActionListener):
    """Gestionnaire d'événement : double-clic sur un élément de la liste du dico de décodage"""
    def __init__(self, listdict, field1, field2, field3):
        self.listdict = listdict
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3

    def actionPerformed(self, actionEvent):
        key = self.listdict.getSelectedItem()
        self.field1.setText(key)
        entry = getLCDictEntry(key)
        self.field2.setText(entry[0])
        self.field3.setText(entry[1])

class DictAddActionListener(unohelper.Base, XActionListener):
    """Gestionnaire d'événement : ajout d'une entrée dans le dico de décodage"""
    def __init__(self, listdict, field1, field2, field3, parent, toolkit=None):
        self.listdict = listdict
        self.field1 = field1
        self.field2 = field2
        self.field3 = field3
        self.parent = parent
        self.toolkit = toolkit

    def actionPerformed(self, actionEvent):
        # existe déjà ?
        key = self.field1.getText().strip().lower()
        phon = self.field2.getText().strip()
        syll = self.field3.getText().strip()

        ctrl = ''.join([ph.split('.')[0] for ph in re.split('/', phon)])
        if len(ctrl) > 0 and key != ctrl:
            # les phonèmes ne redonnent pas le mot utilisé comme clé d'index
            ctrl = '/'.join([ph.split('.')[0] for ph in re.split('/', phon)])
            MsgBox(self.parent, self.toolkit, _(u("Phonèmes"))+' : '+key+' <=> '+ctrl+' ... incorrect')
            return

        ctrl = ''.join(syll.split('/'))
        if len(ctrl) > 0 and key != ctrl:
            # les syllabes ne redonnent pas le mot utilisé comme clé d'index
            MsgBox(self.parent, self.toolkit, _(u("Syllabes"))+' : '+key+' <=> '+syll+' ... incorrect')
            return

        deja_la = False
        try:
            deja_la = key in self.listdict.StringItemList
        except:
            pass

        if not deja_la:
            self.listdict.insertItemText(len(self.listdict.StringItemList), key)
        setLCDictEntry(key, phon, syll)

class DictRemActionListener(unohelper.Base, XActionListener):
    """Gestionnaire d'événement : suppression d'une entrée dans le dico de décodage"""
    def __init__(self, controlContainer, listdict):
        self.controlContainer = controlContainer
        self.listdict = listdict
        self.listdictControl = controlContainer.getControl(listdict.Name)

    def actionPerformed(self, actionEvent):
        if self.listdictControl.getSelectedItemPos() >= 0:
            delLCDictEntry(self.listdictControl.getSelectedItem())
            self.listdict.removeItem(self.listdictControl.getSelectedItemPos())

class GestionnaireDictionnaire(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour gérer le dictionnaire des décodages spéciaux."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __gestionnaire_dictionnaire_dialog__(desktop.getCurrentComponent(), self.ctx)

def gestionnaire_dictionnaire_dialog( args=None ):
    """Ouvrir une fenêtre de dialogue pour gérer le dictionnaire des décodages spéciaux."""
    __gestionnaire_dictionnaire_dialog__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __gestionnaire_dictionnaire_dialog__(xDocument, xContext):
    __arret_dynsylldys__(xDocument)

    """Ouvrir une fenêtre de dialogue pour gérer le dictionnaire des décodages spéciaux."""
    # i18n
    i18n()

    # charge le dictionnaire si cela n'est pas encore fait
    loadLCDict(getLirecouleurDictionary())

    # get the service manager
    smgr = xContext.ServiceManager

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 100
    dialogModel.PositionY = 50
    dialogModel.Width = 300
    dialogModel.Height = 150
    dialogModel.Title = _(u("Dictionnaire LireCouleur"))

    buttAdd = dialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
    buttAdd.Width = 20
    buttAdd.Height = 20
    buttAdd.PositionX = dialogModel.Width/2-buttAdd.Width-2
    buttAdd.PositionY  = dialogModel.Height-2-buttAdd.Height
    buttAdd.Name = "buttAdd"
    buttAdd.TabIndex = 0
    buttAdd.Label = "+"

    buttRem = dialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
    buttRem.Width = 20
    buttRem.Height = 20
    buttRem.PositionX = dialogModel.Width/2+2
    buttRem.PositionY  = buttAdd.PositionY
    buttRem.Name = "buttRem"
    buttRem.TabIndex = 0
    buttRem.Label = "-"

    sep = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedLineModel")
    sep.PositionX = 5
    sep.PositionY = buttAdd.PositionY-40
    sep.Width  = dialogModel.Width-2*sep.PositionX
    sep.Height  = 10
    sep.Name = "sep"
    sep.TabIndex = 1

    label1 = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    label1.PositionX = 2
    label1.PositionY = sep.PositionY+sep.Height
    label1.Width  = 70
    label1.Height = 10
    label1.Name = "label1"
    label1.TabIndex = 1
    label1.Label = _(u("Entrée dictionnaire"))

    label2 = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    label2.PositionX = label1.PositionX+label1.Width+2
    label2.PositionY = label1.PositionY
    label2.Width  = 130
    label2.Height = 10
    label2.Name = "label2"
    label2.TabIndex = 1
    label2.Label = _(u("Phonèmes"))

    label3 = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    label3.PositionX = label2.PositionX+label2.Width+2
    label3.PositionY = label1.PositionY
    label3.Width  = dialogModel.Width-2-label3.PositionX
    label3.Height = 10
    label3.Name = "label3"
    label3.TabIndex = 1
    label3.Label = _(u("Syllabes"))

    field1 = dialogModel.createInstance("com.sun.star.awt.UnoControlEditModel")
    field1.PositionX = label1.PositionX
    field1.PositionY  = label1.PositionY+label1.Height
    field1.Width = label1.Width
    field1.Height = 14
    field1.Name = "field1"
    field1.TabIndex = 0

    field2 = dialogModel.createInstance("com.sun.star.awt.UnoControlEditModel")
    field2.PositionX = label2.PositionX
    field2.PositionY  = label2.PositionY+label2.Height
    field2.Width = label2.Width
    field2.Height = 14
    field2.Name = "field2"
    field2.TabIndex = 0

    field3 = dialogModel.createInstance("com.sun.star.awt.UnoControlEditModel")
    field3.PositionX = label3.PositionX
    field3.PositionY  = label3.PositionY+label3.Height
    field3.Width = label3.Width
    field3.Height = 14
    field3.Name = "field3"
    field3.TabIndex = 0

    listdic = dialogModel.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listdic.PositionX = 2
    listdic.PositionY = 2
    listdic.Width  = dialogModel.Width-2-listdic.PositionX
    listdic.Height  = sep.PositionY-listdic.PositionY
    listdic.Name = "listdic"
    listdic.TabIndex = 1
    listdic.Dropdown = False
    listdic.MultiSelection = False
    listdic.StringItemList = tuple(getLCDictKeys())

    dialogModel.insertByName(label1.Name, label1)
    dialogModel.insertByName(label2.Name, label2)
    dialogModel.insertByName(label3.Name, label3)
    dialogModel.insertByName(field1.Name, field1)
    dialogModel.insertByName(field2.Name, field2)
    dialogModel.insertByName(field3.Name, field3)
    dialogModel.insertByName(sep.Name, sep)
    dialogModel.insertByName(buttAdd.Name, buttAdd)
    dialogModel.insertByName(buttRem.Name, buttRem)
    dialogModel.insertByName(listdic.Name, listdic)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel)

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.getControl(listdic.Name).addActionListener(DictListActionListener(
            controlContainer.getControl(listdic.Name),
            controlContainer.getControl(field1.Name),
            controlContainer.getControl(field2.Name),
            controlContainer.getControl(field3.Name)))
    oParentWin = xDocument.getCurrentController().getFrame().getContainerWindow()
    controlContainer.getControl(buttAdd.Name).addActionListener(DictAddActionListener(
            listdic,
            controlContainer.getControl(field1.Name),
            controlContainer.getControl(field2.Name),
            controlContainer.getControl(field3.Name),
            oParentWin,
            toolkit))
    controlContainer.getControl(buttRem.Name).addActionListener(DictRemActionListener(controlContainer, listdic))

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

"""
    Traitement de la validation du style à éditer
"""
class SelectStyleActionListener(unohelper.Base, XMouseListener):
    """Gestionnaire d'événement : double-clic sur un élément de l'arbre des styles"""
    def __init__(self, ctx, document):
        self.ctx = ctx
        self.document = document

    def mouseEntered(self, aEvent): pass
    def mouseExited(self, aEvent): pass
    def mousePressed(self, aEvent):
        try:
            noeud = aEvent.Source.getNodeForLocation(aEvent.X, aEvent.Y)
            if not noeud is None:
                phonstyle = noeud.DataValue
                if not phonstyle is None and aEvent.ClickCount == 2 and aEvent.Buttons == 1:
                    dispatcher = self.ctx.ServiceManager.createInstanceWithContext( 'com.sun.star.frame.DispatchHelper', self.ctx)
                    prop1 = create_uno_struct("com.sun.star.beans.PropertyValue")
                    prop1.Name = 'Param'
                    prop1.Value = phonstyle
                    prop2 = create_uno_struct("com.sun.star.beans.PropertyValue")
                    prop2.Name = 'Family'
                    prop2.Value = 1
                    dispatcher.executeDispatch(self.document.getCurrentController().getFrame(), ".uno:EditStyle", "", 0, (prop1, 
                    prop2,))
        except Exception as e:
            print(("Failed to process Mouse Event: %s" % e))
    def mouseReleased(self, aEvent): pass

######################################################################################
# Création d'une boite de dialogue pour sélectionner les phonèmes à visualiser
######################################################################################
class GestionnaireStyles(unohelper.Base, XJobExecutor, XMouseListener):
    """Ouvrir une fenêtre de dialogue pour éditer les styles."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __gestionnaire_styles_dialog__(desktop.getCurrentComponent(), self.ctx)

def gestionnaire_styles_dialog( args=None ):
    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    __gestionnaire_styles_dialog__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __gestionnaire_styles_dialog__(xDocument, xContext):
    __arret_dynsylldys__(xDocument)

    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    import array

    # i18n
    i18n()

    try:
        # Importer les styles de coloriage de texte
        importStylesLireCouleur(xDocument)
    except:
        pass

    # get the service manager
    smgr = xContext.ServiceManager

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 100
    dialogModel.PositionY = 50
    dialogModel.Width = 150
    dialogModel.Height = 200
    dialogModel.Title = _(u("Edition des styles"))

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel)

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    treeModel = dialogModel.createInstance("com.sun.star.awt.tree.TreeControlModel")
    treeModel.Name = 'treeModel'
    treeModel.PositionX = 0
    treeModel.PositionY = 0
    treeModel.Width = 150
    treeModel.Height = 200
    dialogModel.insertByName(treeModel.Name, treeModel)
    
    mutableTreeDataModel = smgr.createInstanceWithContext("com.sun.star.awt.tree.MutableTreeDataModel", xContext)
    rootNode = mutableTreeDataModel.createNode("Styles LireCouleur", True)
    mutableTreeDataModel.setRoot(rootNode)

    # styles phonèmes
    noeudPhonemes = mutableTreeDataModel.createNode("Phonèmes", True)
    rootNode.appendChild(noeudPhonemes)
    
    lphon_v = {'phon_a': u('[a] ta'), 'phon_e':u('[e] le'), 'phon_i':u('[i] il'), 'phon_u':u('[y] tu'),
    'phon_ou':u('[u] fou'), 'phon_ez':u('[é] né'), 'phon_o_ouvert':u('[o] mot'), 'phon_et':u('[è] sel'),
    'phon_an':u('[an] grand'), 'phon_on':u('[on] son'), 'phon_eu':u('[x] feu'), 'phon_in':u('[in] fin'),
    'phon_un':u('[un] un'), 'phon_muet':u('[#] lettres muettes, e caduc')}
    lphon_c = {'phon_r':u('[r] rat'), 'phon_l':u('[l] ville'),
    'phon_m':u('[m] mami'), 'phon_n':u('[n] âne'), 'phon_v':u('[v] vélo'), 'phon_z':u('[z] zoo'),
    'phon_ge':u('[ge] jupe'), 'phon_f':u('[f] effacer'), 'phon_s':u('[s] scie'), 'phon_ch':u('[ch] chat'),
    'phon_p':u('[p] papa'), 'phon_t':u('[t] tortue'), 'phon_k':u('[k] coq'), 'phon_b':u('[b] bébé'),
    'phon_d':u('[d] dindon'), 'phon_g':u('[g] gare'), 'phon_ks':u('[ks] ksi'), 'phon_gz':u('[gz] exact')}
    lphon_s = {'phon_w':u('[w]'), 'phon_wa':u('[wa] noix'), 'phon_w5':u('[w5] coin'),
    'phon_y':u('[j] fille'), 'phon_ng':u('[ng] parking'), 'phon_gn':u('[gn] ligne')}
    lphon_x = {'phon_voyelle_comp':u('voyelle complexe'), 'phon_consonne_comp':u('consonne complexe')}
    noeudcat = mutableTreeDataModel.createNode("Voyelles", True)
    noeudPhonemes.appendChild(noeudcat)
    for ph in lphon_v:
        noeud = mutableTreeDataModel.createNode(lphon_v[ph], False)
        noeud.DataValue = ph
        noeudcat.appendChild(noeud)
    noeudcat = mutableTreeDataModel.createNode("Consonnes", True)
    noeudPhonemes.appendChild(noeudcat)
    for ph in lphon_c:
        noeud = mutableTreeDataModel.createNode(lphon_c[ph], False)
        noeud.DataValue = ph
        noeudcat.appendChild(noeud)
    noeudcat = mutableTreeDataModel.createNode("Semi-consonnes", True)
    noeudPhonemes.appendChild(noeudcat)
    for ph in lphon_s:
        noeud = mutableTreeDataModel.createNode(lphon_s[ph], False)
        noeud.DataValue = ph
        noeudcat.appendChild(noeud)
    noeudcat = mutableTreeDataModel.createNode("Complexes", True)
    noeudPhonemes.appendChild(noeudcat)
    for ph in lphon_x:
        noeud = mutableTreeDataModel.createNode(lphon_x[ph], False)
        noeud.DataValue = ph
        noeudcat.appendChild(noeud)

    # styles syllabes
    noeudSyllabes = mutableTreeDataModel.createNode("Syllabes", True)
    rootNode.appendChild(noeudSyllabes)
    for i in range(4):
        noeud = mutableTreeDataModel.createNode('syllabe '+str(i+1), False)
        noeud.DataValue = 'syll_dys_'+str(i+1)
        noeudSyllabes.appendChild(noeud)
    
    # styles mots
    noeudMots = mutableTreeDataModel.createNode("Mots", True)
    rootNode.appendChild(noeudMots)
    for i in range(4):
        noeud = mutableTreeDataModel.createNode('mot '+str(i+1), False)
        noeud.DataValue = 'mot_dys_'+str(i+1)
        noeudMots.appendChild(noeud)
    noeud = mutableTreeDataModel.createNode('liaison', False)
    noeud.DataValue = 'liaison'
    noeudMots.appendChild(noeud)

    # styles lettres
    lphon_x = {'lettre_b':'b', 'lettre_d':'d', 'lettre_p':'p', 'lettre_q':'q',
                'Majuscule':'majuscule', 'Ponctuation':'ponctuation'}
    noeudLettres = mutableTreeDataModel.createNode("Lettres", True)
    rootNode.appendChild(noeudLettres)
    for ph in lphon_x:
        noeud = mutableTreeDataModel.createNode(lphon_x[ph], False)
        noeud.DataValue = ph
        noeudLettres.appendChild(noeud)
    
    # styles lignes
    noeudLignes = mutableTreeDataModel.createNode("Lignes", False)
    rootNode.appendChild(noeudLignes)
    for i in range(4):
        noeud = mutableTreeDataModel.createNode('ligne '+str(i+1), False)
        noeud.DataValue = 'altern_ligne_'+str(i+1)
        noeudLignes.appendChild(noeud)

    treeModel.DataModel = mutableTreeDataModel
    treeCtrl = controlContainer.getControl(treeModel.Name)
    treeCtrl.addMouseListener(SelectStyleActionListener(xContext, xDocument))

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

###################################################################################
# Élimine tout style de caractère
###################################################################################
class StyleDefaut(unohelper.Base, XJobExecutor):
    """Applique le style par défaut à la sélection"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_defaut__(desktop.getCurrentComponent())

def lirecouleur_defaut( args=None ):
    """Applique le style par défaut à la sélection"""
    __lirecouleur_defaut__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Recode le texte sélectionné en noir
###################################################################################
class StyleNoir(unohelper.Base, XJobExecutor):
    """Recode le texte sélectionné en noir"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_noir__(desktop.getCurrentComponent())

def lirecouleur_noir( args=None ):
    """Recode le texte sélectionné en noir"""
    __lirecouleur_noir__(XSCRIPTCONTEXT.getDocument())

###################################################################################
# Espace les mots de la sélection en dupliquant les espaces
###################################################################################
class StyleEspace(unohelper.Base, XJobExecutor):
    """Espace les mots de la sélection"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_espace__(desktop.getCurrentComponent())

def lirecouleur_espace( args=None ):
    """Espace les mots de la sélection"""
    __lirecouleur_espace__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les mots de la sélection en dupliquant les espaces
###################################################################################
class StyleSepareMots(unohelper.Base, XJobExecutor):
    """Sépare les mots de la sélection en coloriant les espaces"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_separe_mots__(desktop.getCurrentComponent())

def lirecouleur_separe_mots( args=None ):
    """Sépare les mots de la sélection en coloriant les espaces"""
    __lirecouleur_separe_mots__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les mots de la sélection en dupliquant les espaces
###################################################################################
class StyleCouleurMots(unohelper.Base, XJobExecutor):
    """Colorie les mots en alternant les couleurs (comme syll_dys)"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_couleur_mots__(desktop.getCurrentComponent())

def lirecouleur_couleur_mots( args=None ):
    """Colorie les mots en alternant les couleurs (comme syll_dys)"""
    __lirecouleur_couleur_mots__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les lignes de la sélection
###################################################################################
class StylePara(unohelper.Base, XJobExecutor):
    """Espace les lignes de la sélection"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_espace_lignes__(desktop.getCurrentComponent())

def lirecouleur_espace_lignes( args=None ):
    """Espace les lignes de la sélection"""
    __lirecouleur_espace_lignes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les lignes et les mots de la sélection
###################################################################################
class StyleLarge(unohelper.Base, XJobExecutor):
    """Espace les lignes et les mots de la sélection"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_large__(desktop.getCurrentComponent())

def lirecouleur_large( args=None ):
    """Espace les lignes et les mots de la sélection"""
    __lirecouleur_large__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les lignes de la sélection ainsi que les caractères
###################################################################################
class StyleExtraLarge(unohelper.Base, XJobExecutor):
    """Espace les lignes de la sélection ainsi que les caractères"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_extra_large__(desktop.getCurrentComponent())

def lirecouleur_extra_large( args=None ):
    """Espace les lignes de la sélection ainsi que les caractères"""
    __lirecouleur_extra_large__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Marque les phonèmes sous forme de couleurs en fonction des styles du document
###################################################################################
class StylePhonemes(unohelper.Base, XJobExecutor):
    """Colorie les phonèmes en couleurs arc en ciel"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_phonemes__(desktop.getCurrentComponent())

def lirecouleur_phonemes( args=None ):
    """Colorie les phonèmes en couleurs arc en ciel"""
    __lirecouleur_phonemes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Marque les phonèmes sous forme de couleurs en fonction des styles du document
###################################################################################
class StylePhonemesComplexes(unohelper.Base, XJobExecutor):
    """Colorie les phonèmes complexes"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_phonemes_complexes__(desktop.getCurrentComponent())

def lirecouleur_phonemes_complexes( args=None ):
    """Colorie les phonèmes complexes"""
    __lirecouleur_phonemes_complexes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Marque les syllabes sous forme de ponts.
###################################################################################
class StyleSyllabes(unohelper.Base, XJobExecutor):
    """Mise en évidence des syllabes soulignées"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_syllabes__(desktop.getCurrentComponent(),  "souligne")

def lirecouleur_syllabes( args=None ):
    """Mise en évidence des syllabes soulignées"""
    __lirecouleur_syllabes__(XSCRIPTCONTEXT.getDocument(), 'souligne')

###################################################################################
# Marque les syllabes en alternant les couleurs
###################################################################################
class StyleSyllDys(unohelper.Base, XJobExecutor):
    """Mise en évidence des syllabes -- dyslexiques"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_syllabes__(desktop.getCurrentComponent(), "dys")
        __lirecouleur_dynsylldys__(desktop.getCurrentComponent())

def lirecouleur_sylldys( args=None ):
    """Mise en évidence des syllabes -- dyslexiques"""
    xDocument = XSCRIPTCONTEXT.getDocument()

    __lirecouleur_syllabes__(xDocument, 'dys')
    __lirecouleur_dynsylldys__(xDocument)


###################################################################################
# Supprime les arcs sous les syllabes dans le texte sélectionné.
###################################################################################
class SupprimerSyllabes(unohelper.Base, XJobExecutor):
    """Supprime les formes ajoutées sur la page pour marquer les syllabes"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_suppr_syllabes__(desktop.getCurrentComponent())

def lirecouleur_suppr_syllabes( args=None ):
    """Supprime les cuvettes qui marquent les liaisons"""
    __lirecouleur_suppr_syllabes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Ne marque que les lettres muettes dans le texte sélectionné.
###################################################################################
class StyleLMuettes(unohelper.Base, XJobExecutor):
    """Met uniquement en évidence les lettres muettes"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_l_muettes__(desktop.getCurrentComponent())

def lirecouleur_l_muettes( args=None ):
    """Met uniquement en évidence les lettres muettes"""
    __lirecouleur_l_muettes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Formatte toute la sélection comme phonème muet
###################################################################################
class StylePhonMuet(unohelper.Base, XJobExecutor):
    """Formate la sélection comme phonème muet"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_phon_muet__(desktop.getCurrentComponent())

def lirecouleur_phon_muet( args=None ):
    """Formate la sélection comme phonème muet"""
    __lirecouleur_phon_muet__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Supprime d'éventuelles décorations sous certains sons
###################################################################################
class SupprimerDecos(unohelper.Base, XJobExecutor):
    """Supprime les formes ajoutées sur la page pour marquer certains sons"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_suppr_decos__(desktop.getCurrentComponent())

def lirecouleur_suppr_decos( args=None ):
    """Supprime les formes ajoutées sur al page pour marquer certains sons"""
    __lirecouleur_suppr_decos__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Colorie les majuscules de début de phrase et les point de fin de phrase.
###################################################################################
class StylePhrase(unohelper.Base, XJobExecutor):
    """Marque les majuscules de début de phrase et les points de fin de phrase."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_phrase__(desktop.getCurrentComponent())

def lirecouleur_phrase( args=None ):
    """Marque les majuscules de début de phrase et les points de fin de phrase."""
    __lirecouleur_phrase__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Marque les liaisons dans le texte sélectionné.
###################################################################################
class StyleLiaisons(unohelper.Base, XJobExecutor):
    """Mise en évidence des liaisons"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_liaisons__(desktop.getCurrentComponent())

def lirecouleur_liaisons( args=None ):
    """Mise en évidence des liaisons"""
    __lirecouleur_liaisons__(XSCRIPTCONTEXT.getDocument())

class StyleLiaisonsForcees(unohelper.Base, XJobExecutor):
    """Forcer la mise en évidence des liaisons (mode enseignant)"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_liaisons__(desktop.getCurrentComponent(), forcer=True)

def lirecouleur_liaisons_forcees( args=None ):
    """Mise en évidence des liaisons"""
    __lirecouleur_liaisons__(XSCRIPTCONTEXT.getDocument(), forcer=True)


###################################################################################
# Colorie les lettres b, d, p, q pour éviter des confusions.
###################################################################################
class ConfusionBDPQ(unohelper.Base, XJobExecutor):
    """Colorie les lettre B, D, P, Q pour éviter les confusions"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_bdpq__(desktop.getCurrentComponent())

def lirecouleur_bdpq( args=None ):
    """Colorie les lettres B, D, P, Q pour éviter les confusions"""
    __lirecouleur_bdpq__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Colorie les consonnes et les voyelles.
###################################################################################
class ConsonneVoyelle(unohelper.Base, XJobExecutor):
    """Colorie les consonnes et les voyelles"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_consonne_voyelle__(desktop.getCurrentComponent())

def lirecouleur_consonne_voyelle( args=None ):
    """Colorie les consonnes et les voyelles"""
    __lirecouleur_consonne_voyelle__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Colorie les lignes avec une alternance de couleurs.
###################################################################################
class StyleLignesAlternees(unohelper.Base, XJobExecutor):
    """Alterne les styles pour les lignes du document"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_lignes__(desktop.getCurrentComponent())

def lirecouleur_lignes( args=None ):
    """Alterne les styles pour les lignes du document -- dyslexiques"""
    __lirecouleur_lignes__(XSCRIPTCONTEXT.getDocument())


"""
    Création d'un nouveau document LireCouleur
"""
class NewLireCouleurDocument(unohelper.Base, XJobExecutor):
    """Création d'un nouveau document LireCouleur"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __new_lirecouleur_document__(desktop.getCurrentComponent(), self.ctx)

def new_lirecouleur_document(args=None):
    __new_lirecouleur_document__(XSCRIPTCONTEXT.getDocument(), uno.getComponentContext())


###################################################################################
# Lit le passage courant sous le curseur
###################################################################################
class Lire():
    """Lit la syllabe courante sous le curseur"""
    def __init__(self, xDocument, applic, nb_altern, choix_syllo):
        self.xDocument = xDocument
        self.xController = self.xDocument.getCurrentController()
        self.curseurMot = None
        self.ps = None
        self.isyl = 0
        self.jsyl = 0
        self.nb_altern = nb_altern
        self.choix_syllo = choix_syllo
        self.applic = applic
        
    def debutMot(self, xtr):
        if not self.curseurMot is None:
            # remise en place de la couleur d'arrière plan de la syllabe
            self.curseurMot.setPropertyToDefault('CharBackColor')
            del self.curseurMot
            del self.ps
        
        self.curseurMot = xtr.getText().createTextCursorByRange(xtr)
        self.curseurMot.collapseToStart()
        xtr.gotoEndOfWord(True)
        mot = xtr.getString()

        # suppressions et remplacements de caractères perturbateurs
        mot = nettoyeur_caracteres(mot)

        # traite le paragraphe en phonèmes
        pp = generer_paragraphe_phonemes(mot)

        # recompose les syllabes
        self.ps = generer_paragraphe_syllabes(pp, self.choix_syllo)[0]
        del pp
        
        # surligner la première syllabe
        self.isyl = 0
        psyl = len(self.ps[self.isyl])

        #ncurs = xtr.getText().createTextCursorByRange(xtr)
        self.curseurMot.goRight(psyl, True)
        self.curseurMot.setPropertyValue('CharStyleName', 'altern_ligne_1')
        self.xController.getViewCursor().gotoRange(self.curseurMot, False)
        self.xController.getViewCursor().collapseToEnd()
        if self.applic:
            #in order to patch an openoffice bug
            self.xController.getViewCursor().goLeft(1, False)
        colorier_lettres_muettes(self.xDocument, self.ps[self.isyl], self.curseurMot, 'perso')

    def selection(self):
        # récupération du curseur physique
        xTextViewCursor = self.xController.getViewCursor()
        xtr = xTextViewCursor.getText().createTextCursorByRange(xTextViewCursor)

        if xtr.isEndOfWord():
            if not self.curseurMot is None:
                self.curseurMot.setPropertyToDefault('CharBackColor')
                setStyle(styles_syllabes['dys'][str(self.jsyl%self.nb_altern+1)], self.curseurMot)
                colorier_lettres_muettes(self.xDocument, self.ps[self.isyl], self.curseurMot, 'perso')
                self.jsyl += 1
                del self.curseurMot
                del self.ps
                self.curseurMot = None

            # passage au mot suivant
            xtr.gotoNextWord(False)
            xTextViewCursor.gotoRange(xtr, False)
            
        if xtr.isStartOfWord():
            self.debutMot(xtr)
        else:
            if not self.curseurMot is None:
                # passage à la syllabe suivante
                            
                # remise en place de la couleur d'arrière plan de la syllabe
                self.curseurMot.setPropertyToDefault('CharBackColor')
                setStyle(styles_syllabes['dys'][str(self.jsyl%self.nb_altern+1)], self.curseurMot)
                colorier_lettres_muettes(self.xDocument, self.ps[self.isyl], self.curseurMot, 'perso')
                self.curseurMot.collapseToEnd()

                self.isyl += 1
                self.jsyl += 1
                if self.isyl < len(self.ps):
                    psyl = len(self.ps[self.isyl])

                    # surligner la syllabe courante
                    self.curseurMot.goRight(psyl, True)
                    self.curseurMot.setPropertyValue('CharStyleName', 'altern_ligne_1')
                    xTextViewCursor.gotoRange(self.curseurMot, False)
                    xTextViewCursor.collapseToEnd()
                    if self.applic:
                        #in order to patch an openoffice bug
                        self.xController.getViewCursor().goLeft(1, False)
                    colorier_lettres_muettes(self.xDocument, self.ps[self.isyl], self.curseurMot, 'perso')
                else:
                    xtr.gotoEndOfWord(False)
                    xtr.gotoNextWord(False)
                    del self.curseurMot
                    self.curseurMot = None
                    del self.ps
                    xTextViewCursor.gotoRange(xtr, False)
                    xTextViewCursor.collapseToEnd()
                    if self.applic:
                        #in order to patch an openoffice bug
                        self.xController.getViewCursor().goLeft(1, False)
            else:
                # placement du curseur physique en cours de mot par l'utilisateur : passage au mot suivant
                xtr.gotoNextWord(False)
                xTextViewCursor.gotoRange(xtr, False)
                xTextViewCursor.collapseToEnd()
                if self.applic:
                    #in order to patch an openoffice bug
                    self.xController.getViewCursor().goLeft(1, False)

        del xtr

###################################################################################
# Classe de gestion des déplacements d'une syllabe à l'autre
###################################################################################
class LireCouleurHandler(unohelper.Base, XKeyHandler):
    enabled = True

    def __init__(self, xDocument, applic):
        self.xDocument = xDocument
        self.is_text_doc = self.xDocument.supportsService("com.sun.star.text.TextDocument")
        
        settings = Settings()

        # Importer les styles de coloriage de texte
        importStylesLireCouleur(xDocument)

        # chargement du dictionnaire de décodage
        loadLCDict(getLirecouleurDictionary())

        # récup de la période d'alternance des couleurs
        nb_altern = settings.get('__alternate__')

        # récupération de l'information sur le choix entre syllabes orales ou syllabes écrites
        choix_syllo = settings.get('__syllo__')

        self.lit = Lire(self.xDocument, applic, nb_altern, choix_syllo)

    def keyPressed(self, event):
            if not(LireCouleurHandler.enabled and self.is_text_doc):
                return False
            ##if event.Modifiers == MOD2:
            if event.KeyCode == keyRight:
                # ALT + ->
                ##__deplacement__(self.xDocument, __lectureSuivant__)
                self.lit.selection()
                return True
            return False

    def keyReleased(self, event):
        return False
        
    def enable(self, val=True):
        LireCouleurHandler.enabled = val


###################################################################################
# lists the scripts, that shall be visible inside OOo. Can be omitted.
###################################################################################
g_exportedScripts = lirecouleur_defaut, lirecouleur_espace, lirecouleur_phonemes, lirecouleur_syllabes, \
lirecouleur_sylldys, lirecouleur_l_muettes, gestionnaire_config_dialog, lirecouleur_liaisons, \
lirecouleur_liaisons_forcees, lirecouleur_bdpq, lirecouleur_suppr_syllabes, lirecouleur_lignes, \
lirecouleur_phrase, lirecouleur_suppr_decos, lirecouleur_phon_muet, lirecouleur_phonemes_complexes, \
new_lirecouleur_document, gestionnaire_dictionnaire_dialog, lirecouleur_espace_lignes, lirecouleur_consonne_voyelle, \
lirecouleur_large, lirecouleur_extra_large, lirecouleur_noir, lirecouleur_separe_mots, \
lirecouleur_couleur_mots, gestionnaire_styles_dialog,

# --- faked component, dummy to allow registration with unopkg, no functionality expected
g_ImplementationHelper = unohelper.ImplementationHelper()

g_ImplementationHelper.addImplementation( \
    StyleDefaut,'org.lirecouleur.StyleDefaut', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleNoir,'org.lirecouleur.StyleNoir', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleEspace,'org.lirecouleur.StyleEspace', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StylePhonemes,'org.lirecouleur.StylePhonemes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleSyllabes,'org.lirecouleur.StyleSyllabes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleSyllDys,'org.lirecouleur.StyleSyllDys', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleLMuettes,'org.lirecouleur.StyleLMuettes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleLiaisons,'org.lirecouleur.StyleLiaisons', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleLiaisonsForcees,'org.lirecouleur.StyleLiaisonsForcees', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfusionBDPQ,'org.lirecouleur.ConfusionBDPQ', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConsonneVoyelle,'org.lirecouleur.ConsonneVoyelle', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    GestionnaireConfiguration,'org.lirecouleur.GestionnaireConfiguration', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    SupprimerSyllabes,'org.lirecouleur.SupprimerSyllabes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    SupprimerDecos,'org.lirecouleur.SupprimerDecos', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleLignesAlternees,'org.lirecouleur.StyleLignesAlternees', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StylePhrase,'org.lirecouleur.StylePhrase', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StylePhonMuet,'org.lirecouleur.StylePhonMuet', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StylePhonemesComplexes,'org.lirecouleur.StylePhonemesComplexes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    NewLireCouleurDocument,'org.lirecouleur.NewLireCouleurDocument', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    GestionnaireDictionnaire,'org.lirecouleur.GestionnaireDictionnaire', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    GestionnaireStyles,'org.lirecouleur.GestionnaireStyles', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StylePara,'org.lirecouleur.StylePara', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleLarge,'org.lirecouleur.StyleLarge', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleExtraLarge,'org.lirecouleur.StyleExtraLarge', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleSepareMots,'org.lirecouleur.StyleSepareMots', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleCouleurMots,'org.lirecouleur.StyleCouleurMots', \
    ('com.sun.star.task.Job',))

