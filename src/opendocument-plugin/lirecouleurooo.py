#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

###################################################################################
# Macro destinée à l'affichage de textes en couleur et à la segmentation
# de mots en syllabes
#
# voir http://lirecouleur.arkaline.fr
#
# @author Marie-Pierre Brungard
# @version 4.6.2
# @since 2018
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
import random
import re
import os

from com.sun.star.awt import (XActionListener, XMouseListener)
from com.sun.star.task import XJobExecutor
from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
from com.sun.star.awt import Rectangle

from lirecouleur.lirecouleur import (u, getLCDictEntry, setLCDictEntry, delLCDictEntry, loadLCDict, getLCDictKeys)
from lirecouleur.utils import (Settings, create_uno_service, create_uno_struct)
from lirecouleur.lirecouleurui import (i18n,__lirecouleur_phonemes__,__lirecouleur_noir__,__lirecouleur_confusion_lettres__,
        __lirecouleur_consonne_voyelle__,__lirecouleur_couleur_mots__,__lirecouleur_defaut__,__lirecouleur_espace__,
        __lirecouleur_espace_lignes__,__lirecouleur_extra_large__,__lirecouleur_l_muettes__,__lirecouleur_large__,
        __lirecouleur_liaisons__,__lirecouleur_lignes__,__lirecouleur_phon_muet__,__lirecouleur_graphemes_complexes__,
        __lirecouleur_ponctuation__,__lirecouleur_separe_mots__,__lirecouleur_suppr_decos__,__lirecouleur_suppr_syllabes__,
        __lirecouleur_syllabes__,__new_lirecouleur_document__, getLirecouleurDictionary,__lirecouleur_alterne_phonemes__,
        importStylesLireCouleur,getLirecouleurURL, __lirecouleur_recharger_styles__)


l_styles_phon = ['phon_a', 'phon_e', 'phon_i', 'phon_u', 'phon_ou', 'phon_ez', 'phon_o_ouvert', 'phon_et',
    'phon_an', 'phon_on', 'phon_eu', 'phon_in', 'phon_un', 'phon_muet',
    'phon_r', 'phon_l', 'phon_m', 'phon_n', 'phon_v', 'phon_z',
    'phon_ge', 'phon_f', 'phon_s', 'phon_ch', 'phon_p', 'phon_t', 'phon_k', 'phon_b',
    'phon_d', 'phon_g', 'phon_ks', 'phon_gz', 'phon_w', 'phon_wa', 'phon_y', 'phon_ng', 'phon_gn']

######################################################################################
# Gestionnaire d'événement de la boite de dialogue
######################################################################################
class CancelActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer):
        self.controlContainer = controlContainer

    def actionPerformed(self, __actionEvent):
        self.controlContainer.endExecute()

class ConfigurationPhonemesActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer):
        self.controlContainer = controlContainer

    def getState(self, val):
        try:
            return self.controlContainer.getControl('chk_'+val).State
        except:
            return False

    def actionPerformed(self, __actionEvent):
        global l_styles_phon

        settings = Settings()

        selectphonemes = settings.get('__selection_phonemes__')

        selectphonemes['a'] = self.getState("phon_a")
        selectphonemes['e'] = selectphonemes['e_comp'] = self.getState('phon_ez')
        selectphonemes['e^'] = selectphonemes['e^_comp'] = self.getState('phon_et')
        selectphonemes['q'] = self.getState('phon_e')
        selectphonemes['u'] = self.getState('phon_ou')
        selectphonemes['i'] = self.getState('phon_i')
        selectphonemes['y'] = self.getState('phon_u')
        selectphonemes['o'] = selectphonemes['o_comp'] = selectphonemes['o_ouvert'] = self.getState('phon_o_ouvert')

        selectphonemes['x'] = selectphonemes['x^'] = self.getState('phon_eu')
        selectphonemes['a~'] = self.getState('phon_an')
        selectphonemes['e~'] = self.getState('phon_in')
        selectphonemes['x~'] = self.getState('phon_un')
        selectphonemes['o~'] = self.getState('phon_on')
        selectphonemes['wa'] = self.getState('phon_wa')
        selectphonemes['j'] = self.getState('phon_y')

        selectphonemes['n'] = self.getState('phon_n')
        selectphonemes['g~'] = self.getState('phon_ng')
        selectphonemes['n~'] = self.getState('phon_gn')

        selectphonemes['l'] = self.getState('phon_l')
        selectphonemes['m'] = self.getState('phon_m')
        selectphonemes['r'] = self.getState('phon_r')

        selectphonemes['v'] = self.getState('phon_v')
        selectphonemes['z'] = selectphonemes['z_s'] = self.getState('phon_z')
        selectphonemes['z^'] = selectphonemes['z^_g'] = self.getState('phon_ge')

        selectphonemes['f'] = selectphonemes['f_ph'] = self.getState('phon_f')
        selectphonemes['s'] = selectphonemes['s_c'] = selectphonemes['s_t'] = self.getState('phon_s')
        selectphonemes['s^'] = self.getState('phon_ch')

        selectphonemes['p'] = self.getState('phon_p')
        selectphonemes['t'] = self.getState('phon_t')
        selectphonemes['k'] = selectphonemes['k_qu'] = self.getState('phon_k')

        selectphonemes['b'] = self.getState('phon_b')
        selectphonemes['d'] = self.getState('phon_d')
        selectphonemes['g'] = selectphonemes['g_u'] = self.getState('phon_g')

        selectphonemes['ks'] = self.getState('phon_ks')
        selectphonemes['gz'] = self.getState('phon_gz')

        selectphonemes['#'] = self.getState('phon_muet')

        # considérer que la sélection des phonèmes 'voyelle' s'étend à 'yod'+'voyelle' et à 'wau'+'voyelle'
        for phon in ['a', 'a~', 'e', 'e^', 'e_comp', 'e^_comp', 'o', 'o~', 'i', 'e~', 'x', 'x^', 'u', 'q_caduc']:
            try:
                selectphonemes['j_'+phon] = selectphonemes[phon]
                selectphonemes['w_'+phon] = selectphonemes[phon]
            except:
                pass

        settings.setValue('__point__', self.controlContainer.getControl('chk_checkPoint').getState())

        settings.setValue('__selection_phonemes__', selectphonemes)
        self.controlContainer.endExecute()

class ConfigurationConfusionLettresActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer):
        self.controlContainer = controlContainer

    def getState(self, val):
        try:
            return self.controlContainer.getControl('chk_'+val).State
        except:
            return False

    def actionPerformed(self, __actionEvent):
        settings = Settings()

        selectlettres = settings.get('__selection_lettres__')

        selectlettres['b'] = self.getState("l_b")
        selectlettres['d'] = self.getState('l_d')
        selectlettres['p'] = self.getState('l_p')
        selectlettres['q'] = self.getState('l_k')
        selectlettres['m'] = self.getState('l_m')
        selectlettres['n'] = self.getState('l_n')
        selectlettres['r'] = self.getState('l_r')
        selectlettres['t'] = self.getState('l_t')
        selectlettres['f'] = self.getState('l_f')
        selectlettres['u'] = self.getState('l_u')

        settings.setValue('__selection_lettres__', selectlettres)
        self.controlContainer.endExecute()

class EditStyleActionListener(unohelper.Base, XActionListener):
    def __init__(self, ctx, document, stylname):
        self.ctx = ctx
        self.document = document
        self.stylname = stylname

    def actionPerformed(self, __actionEvent):
        dispatcher = self.ctx.ServiceManager.createInstanceWithContext( 'com.sun.star.frame.DispatchHelper', self.ctx)
        prop1 = create_uno_struct("com.sun.star.beans.PropertyValue")
        prop1.Name = 'Param'
        prop1.Value = self.stylname
        prop2 = create_uno_struct("com.sun.star.beans.PropertyValue")
        prop2.Name = 'Family'
        prop2.Value = 1
        dispatcher.executeDispatch(self.document.getCurrentController().getFrame(), ".uno:EditStyle", "", 0, (prop1,
        prop2,))

class ConfigurationStyleSyllDysActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer):
        self.controlContainer = controlContainer


    def actionPerformed(self, __actionEvent):
        global l_styles_phon

        settings = Settings()

        try:
            nbcouleurs = self.controlContainer.getControl('fieldCoul').getValue()
            settings.setValue('__alternate__', int(nbcouleurs))
        except:
            pass

        item1 = self.controlContainer.getControl('listTyp1Syll').getSelectedItemPos()
        item2 = self.controlContainer.getControl('listTyp2Syll').getSelectedItemPos()
        settings.setValue('__syllo__', (item1, item2))

        # selon le type de syllabes choisies, les e caducs doivent être affichés différemment
        selectphonemes = settings.get('__selection_phonemes__')
        if item2:
            selectphonemes['q_caduc'] = selectphonemes['yod_q_caduc'] = selectphonemes['#']
        else:
            selectphonemes['q_caduc'] = selectphonemes['yod_q_caduc'] = selectphonemes['q']
        settings.setValue('__selection_phonemes__', selectphonemes)

        self.controlContainer.endExecute()

class ConfigurationStyleAlternActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer):
        self.controlContainer = controlContainer


    def actionPerformed(self, __actionEvent):
        global l_styles_phon

        settings = Settings()

        nbcouleurs = self.controlContainer.getControl('fieldCoul').getValue()
        settings.setValue('__alternate__', int(nbcouleurs))

        self.controlContainer.endExecute()

class ConfigurationEspaceActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer):
        self.controlContainer = controlContainer

    def actionPerformed(self, __actionEvent):
        global l_styles_phon

        settings = Settings()

        nbesp = self.controlContainer.getControl('fieldEsp').getValue()
        settings.setValue('__subspaces__', int(nbesp))

        self.controlContainer.endExecute()

class MyActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer):
        self.controlContainer = controlContainer

    def actionPerformed(self, __actionEvent):
        settings = Settings()
        settings.setValue('__detection_phonemes__', self.controlContainer.getControl('chk_checkSimple').getState())
        settings.setValue('__template__', self.controlContainer.getControl('fieldTemp').getText())
        settings.setValue('__locale__', self.controlContainer.getControl('listLocale').getSelectedItem())

        item_syllo = self.controlContainer.getControl('chk_checkSyllo').getState()
        settings.setValue('__syllo__', (settings.get('__syllo__')[0], item_syllo))

        # selon le type de syllabes choisies, les e caducs doivent être affichés différemment
        selectphonemes = settings.get('__selection_phonemes__')
        if item_syllo:
            selectphonemes['q_caduc'] = selectphonemes['yod_q_caduc'] = selectphonemes['#']
        else:
            selectphonemes['q_caduc'] = selectphonemes['yod_q_caduc'] = selectphonemes['q']
        settings.setValue('__selection_phonemes__', selectphonemes)

        self.controlContainer.endExecute()

class TemplateActionListener(unohelper.Base, XActionListener):
    def __init__(self, controlContainer, fieldTemp, xContext):
        self.controlContainer = controlContainer
        self.fieldTemp = fieldTemp
        self.xContext = xContext

    def actionPerformed(self, __actionEvent):
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
    checkBP.Width  = 10
    checkBP.Height = 10
    checkBP.Name = "chk_"+name
    checkBP.TabIndex = index
    checkBP.State = etat
    checkBP.Label = ""
    dialogModel.insertByName(checkBP.Name, checkBP)

    # créer le label titre
    labelBP = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelBP.PositionX = px+14
    labelBP.PositionY = py
    labelBP.Width  = w
    labelBP.Height = 10
    labelBP.Name = name
    labelBP.TabIndex = 1
    labelBP.Label = label
    dialogModel.insertByName(labelBP.Name, labelBP)

######################################################################################
# Création d'un libellé
######################################################################################
def createLabel(dialogModel, px, py, name, index, label, w=58):
    labelBP = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelBP.PositionX = px
    labelBP.PositionY = py
    labelBP.Width  = w
    labelBP.Height = 10
    labelBP.Name = name
    labelBP.TabIndex = index
    labelBP.Label = label
    dialogModel.insertByName(labelBP.Name, labelBP)
    return labelBP

######################################################################################
# Création d'un bouton
######################################################################################
def createButton(dialogModel, px, py, name, label, w=30):
    button = dialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
    button.PositionX = px
    button.PositionY = py
    button.Width  = w
    button.Height = 14
    button.Name = name
    button.Label = label
    dialogModel.insertByName(button.Name, button)

######################################################################################
# Création d'une ligne de séparation
######################################################################################
def createSeparator(dialogModel, px, py, name, w=30):
    sep = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedLineModel")
    sep.PositionX = px
    sep.PositionY = py
    sep.Width  = w
    sep.Height  = 5
    sep.Name = name
    dialogModel.insertByName(sep.Name, sep)

######################################################################################
# Création d'une zone de saisie de type champ numérique
######################################################################################
def createNumericField(dialogModel, px, py, name, index, val, minv=2, maxv=4, w=60):
    checkNF = dialogModel.createInstance("com.sun.star.awt.UnoControlNumericFieldModel")
    checkNF.PositionX = px
    checkNF.PositionY = py
    checkNF.Width  = w
    checkNF.Height = 15
    checkNF.Name = name
    checkNF.TabIndex = index
    checkNF.Value = val
    checkNF.ValueMin = minv
    checkNF.ValueMax = maxv
    checkNF.ValueStep = 1
    checkNF.Spin = True
    checkNF.DecimalAccuracy = 0
    dialogModel.insertByName(checkNF.Name, checkNF)

######################################################################################
# Création d'un lien vers une URL (aide)
######################################################################################
def createLink(dialogModel, px, py, url, w=10):
    checkNF = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedHyperlinkModel")
    checkNF.PositionX = px
    checkNF.PositionY = py
    checkNF.Width  = w
    checkNF.Height = 15
    checkNF.Name = url+str(int(random.random()*1000))
    checkNF.Label = "?"
    checkNF.URL = url
    checkNF.TextColor = 0x00000ff
    dialogModel.insertByName(checkNF.Name, checkNF)

######################################################################################
# Création d'une boite de dialogue pour sélectionner les phonèmes à visualiser
######################################################################################
class GestionnaireConfiguration(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __gestionnaire_config_dialog__(desktop.getCurrentComponent(), self.ctx)

def gestionnaire_config_dialog( __args=None ):
    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    __gestionnaire_config_dialog__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __gestionnaire_config_dialog__(__xDocument, xContext):
    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    # récupération des infos de configuration
    settings = Settings()

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # décodage des phonèmes niveau débutant lecteur ou standard
    selectsimple = settings.get('__detection_phonemes__')

    # affichage des  caducs comme lettres muettes
    selectsyllo = settings.get('__syllo__')[1]

    # lecture du mode de décodage (dépend de la localisation)
    select_locale = settings.get('__locale__')

    # lecture de la période d'alternance de lignes
    tempFileName = settings.get('__template__')

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 200
    dialogModel.PositionY = 100
    dialogModel.Width = 230
    dialogModel.Height = 115
    dialogModel.Title = "Configuration générale LireCouleur"

    createLink(dialogModel, dialogModel.Width-12, 10, "http://lirecouleur.arkaline.fr/faqconfig/#general")

    createCheckBox(dialogModel, 10, 10, "checkSimple", 0,
                    "Détecter les semi-consonnes comme phonèmes indépendants", selectsimple, dialogModel.Width-10)

    createCheckBox(dialogModel, 10, 25, "checkSyllo", 0,
                    "Afficher les e caducs comme lettres muettes", selectsyllo, dialogModel.Width-10)

    labelListLocale = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelListLocale.PositionX = 10
    labelListLocale.PositionY = 42
    labelListLocale.Width  = 50
    labelListLocale.Height = 12
    labelListLocale.Name = "labelListLocale"
    labelListLocale.TabIndex = 1
    labelListLocale.Label = "Localisation : "
    dialogModel.insertByName(labelListLocale.Name, labelListLocale)

    listLocale = dialogModel.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listLocale.PositionX = labelListLocale.PositionX+labelListLocale.Width+5
    listLocale.PositionY = labelListLocale.PositionY
    listLocale.Width  = 50
    listLocale.Height  = 12
    listLocale.Name = "listLocale"
    listLocale.TabIndex = 1
    listLocale.Dropdown = True
    listLocale.MultiSelection = False
    listLocale.StringItemList = ("fr", "fr_CA", )
    if select_locale in listLocale.StringItemList:
        listLocale.SelectedItems = (listLocale.StringItemList.index(select_locale),)
    else:
        listLocale.SelectedItems = (0,)
    dialogModel.insertByName(listLocale.Name, listLocale)

    labelTemp = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelTemp.PositionX = 10
    labelTemp.PositionY = 62
    labelTemp.Width  = dialogModel.Width-12
    labelTemp.Height = 10
    labelTemp.Name = "labelTemp"
    labelTemp.TabIndex = 1
    labelTemp.Label = "Nom du fichier modèle :"
    dialogModel.insertByName(labelTemp.Name, labelTemp)

    fieldTemp = dialogModel.createInstance("com.sun.star.awt.UnoControlEditModel")
    fieldTemp.PositionX = 10
    fieldTemp.PositionY  = labelTemp.PositionY+labelTemp.Height+2
    fieldTemp.Width = dialogModel.Width-42
    fieldTemp.Height = 14
    fieldTemp.Name = "fieldTemp"
    fieldTemp.TabIndex = 0
    dialogModel.insertByName(fieldTemp.Name, fieldTemp)

    buttTemp = dialogModel.createInstance("com.sun.star.awt.UnoControlButtonModel")
    buttTemp.PositionX = fieldTemp.PositionX+fieldTemp.Width+2
    buttTemp.PositionY  = fieldTemp.PositionY
    buttTemp.Width = dialogModel.Width-buttTemp.PositionX-2
    buttTemp.Height = fieldTemp.Height
    buttTemp.Name = "buttTemp"
    buttTemp.TabIndex = 0
    buttTemp.Label = "..."
    dialogModel.insertByName(buttTemp.Name, buttTemp)

    # create the button model and set the properties
    createSeparator(dialogModel, 10, dialogModel.Height-21, "sep", dialogModel.Width-21)
    createButton(dialogModel, dialogModel.Width/2-61, dialogModel.Height-16, "okButtonName", "Valider", 60)
    createButton(dialogModel, dialogModel.Width/2+1, dialogModel.Height-16, "cancelButtonName", "Annuler", 60)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    # add the action listener
    controlContainer.getControl("okButtonName").addActionListener(MyActionListener(controlContainer))
    controlContainer.getControl("cancelButtonName").addActionListener(CancelActionListener(controlContainer))
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
# Ouverture de la boite de configuration d'un style de caractères
######################################################################################
class EditStyleMouseListener(unohelper.Base, XMouseListener):
    def __init__(self, xContext, xDocument, nstyle):
        self.ctx = xContext
        self.document = xDocument
        self.stylname = nstyle

    def mouseEntered(self, ev): pass
    def mouseExited(self, ev): pass
    def mousePressed(self, ev):
        if ev.Buttons == 1 and ev.ClickCount == 2:
            dispatcher = self.ctx.ServiceManager.createInstanceWithContext( 'com.sun.star.frame.DispatchHelper', self.ctx)
            prop1 = create_uno_struct("com.sun.star.beans.PropertyValue")
            prop1.Name = 'Param'
            prop1.Value = self.stylname
            prop2 = create_uno_struct("com.sun.star.beans.PropertyValue")
            prop2.Name = 'Family'
            prop2.Value = 1
            dispatcher.executeDispatch(self.document.getCurrentController().getFrame(), ".uno:EditStyle", "", 0, (prop1,
            prop2,))

    def mouseReleased(self, ev): pass

######################################################################################
# Création d'une boite de dialogue pour sélectionner les phonèmes à visualiser
######################################################################################
class ConfigurationPhonemes(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_phonemes__(desktop.getCurrentComponent(), self.ctx)

def configuration_phonemes( __args=None ):
    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    __configuration_phonemes__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __configuration_phonemes__(xDocument, xContext):
    global l_styles_phon

    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    # récupération des infos de configuration
    settings = Settings()

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # lecture pour savoir s'il faut mettre un point sous les lettres muettes
    selectpoint = settings.get('__point__')

    # read the already selected phonemes in the .lirecouleur file
    selectphonemes = settings.get('__selection_phonemes__')

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 200
    dialogModel.PositionY = 100
    dialogModel.Width = 220
    dialogModel.Height = 250
    dialogModel.Title = "Configuration : phonèmes"

    createLink(dialogModel, dialogModel.Width-12, 10, "http://lirecouleur.arkaline.fr/faqconfig/#phonemes")

    createLabel(dialogModel, 5, 10, "lbl_1", 1, "Choisir les phonèmes ; doublecliquer sur le libellé pour éditer le style", dialogModel.Width-12)

    # créer les checkboxes des phonèmes
    esp_y = 12 ; esp_x = 70
    i = 2 ; x = 10 ; y = 25
    createCheckBox(dialogModel, x, y, "phon_a", i, '[~a] ta', selectphonemes['a'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_e", i, '[~e] le', selectphonemes['q'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_i", i, '[~i] il', selectphonemes['i'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_u", i, '[~y] tu', selectphonemes['y'], 50)
    i += 1 ; y += esp_y

    x += esp_x ; y = 25
    createCheckBox(dialogModel, x, y, "phon_ou", i, '[~u] fou', selectphonemes['u'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_ez", i, '[~é] né', selectphonemes['e'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_o_ouvert", i, '[~o] mot', selectphonemes['o'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_et", i, '[~è] sel', selectphonemes['e^'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_an", i, '[~an] grand', selectphonemes['a~'], 50)
    i += 1 ; y += esp_y

    x += esp_x ; y = 25
    createCheckBox(dialogModel, x, y, "phon_on", i, '[~on] son', selectphonemes['o~'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_eu", i, '[~x] feu', selectphonemes['x'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_in", i, '[~in] fin', selectphonemes['e~'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_un", i, '[~un] un', selectphonemes['e~'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_wa", i, '[~w] noix', selectphonemes['w'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_y", i, '[~j] fille', selectphonemes['j'], 50)
    i += 1 ; y += esp_y

    x = 10
    createCheckBox(dialogModel, x, y, "phon_ng", i, '[~ng] parking', selectphonemes['g~'], 50)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_gn", i, '[~gn] ligne', selectphonemes['n~'], 50)
    i += 1

    x += esp_x
    createCheckBox(dialogModel, x, y, "phon_muet", i, '[#] lettres muettes, e caduc', selectphonemes['#'], 100)
    i += 1

    y += esp_y ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_r", i, '[~r] rat', selectphonemes['r'], 50)
    i += 1 ; x = 10 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_l", i, '[~l] ville', selectphonemes['l'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_m", i, '[~m] mami', selectphonemes['m'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_n", i, '[~n] âne', selectphonemes['n'], 50)

    i += 1 ; x = 10 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_v", i, '[~v] vélo', selectphonemes['v'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_z", i, '[~z] zoo', selectphonemes['z'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_ge", i, '[~ge] jupe', selectphonemes['z^'], 50)

    i += 1 ; x = 10 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_f", i, '[~f] effacer', selectphonemes['f'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_s", i, '[~s] scie', selectphonemes['s'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_ch", i, '[c~h] chat', selectphonemes['s^'], 50)

    i += 1 ; x = 10 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_p", i, '[~p] papa', selectphonemes['p'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_t", i, '[~t] tortue', selectphonemes['t'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_k", i, '[~k] coq', selectphonemes['k'], 50)

    i += 1 ; x = 10 ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_b", i, '[~b] bébé', selectphonemes['b'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_d", i, '[~d] dindon', selectphonemes['d'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_g", i, '[~g] gare', selectphonemes['g'], 50)

    i += 1 ; x = 10+esp_x ; y += esp_y
    createCheckBox(dialogModel, x, y, "phon_ks", i, '[ks] ksi', selectphonemes['ks'], 50)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "phon_gz", i, '[gz] exact', selectphonemes['gz'], 50)
    i += 1 ; x += esp_x

    createCheckBox(dialogModel, 10, dialogModel.Height-36, "checkPoint", 0,
                    "Placer des symboles sous les phonèmes sélectionnés", selectpoint, dialogModel.Width-10)

    # create the button model and set the properties
    createSeparator(dialogModel, 10, dialogModel.Height-21, "sep", dialogModel.Width-21)
    createButton(dialogModel, dialogModel.Width/2-61, dialogModel.Height-16, "okButtonName", "Valider", 60)
    createButton(dialogModel, dialogModel.Width/2+1, dialogModel.Height-16, "cancelButtonName", "Annuler", 60)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    # add the action listener
    for k in l_styles_phon:
        lblCtrl = controlContainer.getControl(k)
        if not lblCtrl is None:
            lblCtrl.addMouseListener(EditStyleMouseListener(xContext, xDocument, k))

    controlContainer.getControl("okButtonName").addActionListener(ConfigurationPhonemesActionListener(controlContainer))
    controlContainer.getControl("cancelButtonName").addActionListener(CancelActionListener(controlContainer))

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

######################################################################################
# Configuration de la fonction de coloriage des syllabes par alternance de couleurs
######################################################################################
class ConfigurationStyleSyllDys(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour sélectionner les phonèmes à visualiser."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_sylldys__(desktop.getCurrentComponent(), self.ctx)

def configuration_sylldys( __args=None ):
    """Ouvrir une fenêtre de dialogue pour éditer les styles de syllabes alternées."""
    __configuration_sylldys__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __configuration_sylldys__(xDocument, xContext):
    """Ouvrir une fenêtre de dialogue pour éditer les styles de syllabes alternées."""

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    # récupération des infos de configuration
    settings = Settings()

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # lecture de la période d'alternance de lignes, de syllabes, de sons ou de mots
    nbcouleurs = settings.get('__alternate__')

    # lecture pour savoir comment il faut afficher les syllabes
    selectsyllo = settings.get('__syllo__')

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 200
    dialogModel.PositionY = 100
    dialogModel.Width = 210
    dialogModel.Height = 140
    dialogModel.Title = "Configuration : syllabes en couleur"

    createLink(dialogModel, dialogModel.Width-12, 10, "http://lirecouleur.arkaline.fr/faqconfig/#sylldys")

    # créer les checkboxes des phonèmes
    labelCoul = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelCoul.PositionX = 10
    labelCoul.PositionY = 10
    labelCoul.Width  = dialogModel.Width-12
    labelCoul.Height = 16
    labelCoul.Name = "labelCoul"
    labelCoul.TabIndex = 1
    labelCoul.Label = "Période d'alternance des couleurs (lignes, syllabes, etc.) :"
    createNumericField(dialogModel, dialogModel.Width/2-30, labelCoul.PositionY+12, "fieldCoul", 0, nbcouleurs)
    dialogModel.insertByName(labelCoul.Name, labelCoul)

    labelRadio = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelRadio.PositionX = 10
    labelRadio.PositionY = labelCoul.PositionY+35
    labelRadio.Width  = dialogModel.Width-12
    labelRadio.Height = 10
    labelRadio.Name = "labelRadio"
    labelRadio.TabIndex = 1
    labelRadio.Label = "Souligner les syllabes :"
    dialogModel.insertByName(labelRadio.Name, labelRadio)

    listTyp1Syll = dialogModel.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listTyp1Syll.Width  = 65
    listTyp1Syll.Height  = 12
    listTyp1Syll.PositionX = dialogModel.Width/2-listTyp1Syll.Width
    listTyp1Syll.PositionY = labelRadio.PositionY+12
    listTyp1Syll.Name = "listTyp1Syll"
    listTyp1Syll.TabIndex = 1
    listTyp1Syll.Dropdown = True
    listTyp1Syll.MultiSelection = False
    listTyp1Syll.StringItemList = ("LireCouleur", "standard", )
    listTyp1Syll.SelectedItems = (selectsyllo[0]%2,)
    dialogModel.insertByName(listTyp1Syll.Name, listTyp1Syll)

    listTyp2Syll = dialogModel.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listTyp2Syll.Width  = listTyp1Syll.Width
    listTyp2Syll.Height  = listTyp1Syll.Height
    listTyp2Syll.PositionX = listTyp1Syll.PositionX+listTyp1Syll.Width+2
    listTyp2Syll.PositionY = listTyp1Syll.PositionY
    listTyp2Syll.Name = "listTyp2Syll"
    listTyp2Syll.TabIndex = 1
    listTyp2Syll.Dropdown = True
    listTyp2Syll.MultiSelection = False
    listTyp2Syll.StringItemList = ( "écrites", "orales" )
    listTyp2Syll.SelectedItems = (selectsyllo[1]%2,)
    dialogModel.insertByName(listTyp2Syll.Name, listTyp2Syll)

    createLabel(dialogModel, 10, listTyp2Syll.PositionY+25, "labelStyles", 1, "Editer les styles :")
    createButton(dialogModel, 30, listTyp2Syll.PositionY+37, "syll_dys_1", "style 1")
    createButton(dialogModel, 70, listTyp2Syll.PositionY+37, "syll_dys_2", "style 2")
    createButton(dialogModel, 110, listTyp2Syll.PositionY+37, "syll_dys_3", "style 3")
    createButton(dialogModel, 150, listTyp2Syll.PositionY+37, "syll_dys_4", "style 4")

    # create the button model and set the properties
    createSeparator(dialogModel, 10, dialogModel.Height-21, "sep", dialogModel.Width-21)
    createButton(dialogModel, dialogModel.Width/2-61, dialogModel.Height-16, "okButtonName", "Valider", 60)
    createButton(dialogModel, dialogModel.Width/2+1, dialogModel.Height-16, "cancelButtonName", "Annuler", 60)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    controlContainer.getControl("syll_dys_1").addActionListener(EditStyleActionListener(xContext, xDocument, "syll_dys_1"))
    controlContainer.getControl("syll_dys_2").addActionListener(EditStyleActionListener(xContext, xDocument, "syll_dys_2"))
    controlContainer.getControl("syll_dys_3").addActionListener(EditStyleActionListener(xContext, xDocument, "syll_dys_3"))
    controlContainer.getControl("syll_dys_4").addActionListener(EditStyleActionListener(xContext, xDocument, "syll_dys_4"))

    controlContainer.getControl("okButtonName").addActionListener(ConfigurationStyleSyllDysActionListener(controlContainer))
    controlContainer.getControl("cancelButtonName").addActionListener(CancelActionListener(controlContainer))

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

######################################################################################
# Configuration de la fonction de soulignage des syllabes
######################################################################################
class ConfigurationStyleSyllabes(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour la fonction "souligner les syllabes" """
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_syllabes__(desktop.getCurrentComponent(), self.ctx)

def configuration_syllabes( __args=None ):
    """Ouvrir une fenêtre de dialogue pour la fonction "souligner les syllabes" """
    __configuration_syllabes__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __configuration_syllabes__(__xDocument, xContext):
    """Ouvrir une fenêtre de dialogue pour la fonction "souligner les syllabes" """

    # récupération des infos de configuration
    settings = Settings()

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # lecture pour savoir comment il faut afficher les syllabes
    selectsyllo = settings.get('__syllo__')

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 200
    dialogModel.PositionY = 100
    dialogModel.Width = 210
    dialogModel.Height = 70
    dialogModel.Title = "Configuration : souligner les syllabes"

    labelRadio = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelRadio.PositionX = 10
    labelRadio.PositionY = 10
    labelRadio.Width  = dialogModel.Width-12
    labelRadio.Height = 10
    labelRadio.Name = "labelRadio"
    labelRadio.TabIndex = 1
    labelRadio.Label = "Souligner les syllabes :"
    dialogModel.insertByName(labelRadio.Name, labelRadio)

    listTyp1Syll = dialogModel.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listTyp1Syll.Width  = 65
    listTyp1Syll.Height  = 12
    listTyp1Syll.PositionX = dialogModel.Width/2-listTyp1Syll.Width
    listTyp1Syll.PositionY = labelRadio.PositionY+12
    listTyp1Syll.Name = "listTyp1Syll"
    listTyp1Syll.TabIndex = 1
    listTyp1Syll.Dropdown = True
    listTyp1Syll.MultiSelection = False
    listTyp1Syll.StringItemList = ("LireCouleur", "standard", )
    if selectsyllo[0] in [0, 1]:
        listTyp1Syll.SelectedItems = (selectsyllo[0],)
    else:
        listTyp1Syll.SelectedItems = (0,)
    dialogModel.insertByName(listTyp1Syll.Name, listTyp1Syll)

    listTyp2Syll = dialogModel.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listTyp2Syll.Width  = listTyp1Syll.Width
    listTyp2Syll.Height  = listTyp1Syll.Height
    listTyp2Syll.PositionX = listTyp1Syll.PositionX+listTyp1Syll.Width+2
    listTyp2Syll.PositionY = listTyp1Syll.PositionY
    listTyp2Syll.Name = "listTyp2Syll"
    listTyp2Syll.TabIndex = 1
    listTyp2Syll.Dropdown = True
    listTyp2Syll.MultiSelection = False
    listTyp2Syll.StringItemList = ( "écrites", "orales" )
    if selectsyllo[1] in [0, 1]:
        listTyp2Syll.SelectedItems = (selectsyllo[1],)
    else:
        listTyp2Syll.SelectedItems = (0,)
    dialogModel.insertByName(listTyp2Syll.Name, listTyp2Syll)

    # create the button model and set the properties
    createSeparator(dialogModel, 10, dialogModel.Height-21, "sep", dialogModel.Width-21)
    createButton(dialogModel, dialogModel.Width/2-61, dialogModel.Height-16, "okButtonName", "Valider", 60)
    createButton(dialogModel, dialogModel.Width/2+1, dialogModel.Height-16, "cancelButtonName", "Annuler", 60)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    controlContainer.getControl("okButtonName").addActionListener(ConfigurationStyleSyllDysActionListener(controlContainer))
    controlContainer.getControl("cancelButtonName").addActionListener(CancelActionListener(controlContainer))

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

######################################################################################
# Configuration de la fonction de coloriage des lignes par alternance de couleurs
######################################################################################
class ConfigurationStyleLignesAlternees(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer les styles de lignes alternées."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_lignes__(desktop.getCurrentComponent(), self.ctx)

def configuration_lignes( __args=None ):
    """Ouvrir une fenêtre de dialogue pour configurer les styles de lignes alternées."""
    __configuration_lignes__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __configuration_lignes__(xDocument, xContext):
    __configuration_alternance__(xDocument, xContext, "lignes", "altern_ligne_", "surligner1")

######################################################################################
# Configuration de la fonction de mise en évidence de la ponctuation
######################################################################################
class ConfigurationStylePonctuation(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer la fonction de mise en évidence de la ponctuation."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_style_caractere__(desktop.getCurrentComponent(), self.ctx, "ponctuation")

######################################################################################
# Configuration de la fonction de mise en évidence des liaisons
######################################################################################
class ConfigurationStyleLiaisons(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer la fonction de mise en évidence des liaisons."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_style_caractere__(desktop.getCurrentComponent(), self.ctx, "liaison")

######################################################################################
# Configuration de la fonction de mise en évidence des liaisons
######################################################################################
class ConfigurationStyleLiaisonsForcees(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour forcer le marquage comme liaison."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_style_caractere__(desktop.getCurrentComponent(), self.ctx, "liaison")

######################################################################################
# Configuration de la fonction de coloriage des mots par alternance de couleurs
######################################################################################
class ConfigurationStyleCouleurMots(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer les styles de mots alternés."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_couleur_mots__(desktop.getCurrentComponent(), self.ctx)

def configuration_couleur_mots( __args=None ):
    """Ouvrir une fenêtre de dialogue pour configurer les styles de mots alternés."""
    __configuration_couleur_mots__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __configuration_couleur_mots__(xDocument, xContext):
    __configuration_alternance__(xDocument, xContext, "mots", "mot_dys_", "mot_alternes")

######################################################################################
# Configuration de la fonction de séparation des mots
######################################################################################
class ConfigurationStyleSepareMots(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer la fonction de séparation des mots."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_style_caractere__(desktop.getCurrentComponent(), self.ctx, "espace")

######################################################################################
# Configuration de la fonction de coloriage des phonèmes par alternance de couleurs
######################################################################################
class ConfigurationStylePhonemesAlternes(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer les styles de phonèmes alternés."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_alterne_phonemes__(desktop.getCurrentComponent(), self.ctx)

def configuration_alterne_phonemes( __args=None ):
    """Ouvrir une fenêtre de dialogue pour configurer les styles de phonèmes alternés."""
    __configuration_alterne_phonemes__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __configuration_alterne_phonemes__(xDocument, xContext):
    __configuration_alternance__(xDocument, xContext, "phonèmes", "altern_phon_", "phonemes_alternes")

######################################################################################
# Boite de configuration générique pour les fonctions à alternance de couleurs
######################################################################################
def __configuration_alternance__(xDocument, xContext, titre, sb, url=""):
    """Ouvrir une fenêtre de dialogue pour configurer les styles de lignes alternées."""

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    # récupération des infos de configuration
    settings = Settings()

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # lecture de la période d'alternance de lignes, de syllabes, de sons ou de mots
    nbcouleurs = settings.get('__alternate__')

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 200
    dialogModel.PositionY = 100
    dialogModel.Width = 210
    dialogModel.Height = 100
    dialogModel.Title = "Configuration : alternance de "+titre

    createLink(dialogModel, dialogModel.Width-12, 10, "http://lirecouleur.arkaline.fr/faqconfig/#"+url)

    # créer les checkboxes des phonèmes
    labelCoul = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelCoul.PositionX = 10
    labelCoul.PositionY = 10
    labelCoul.Width  = dialogModel.Width-12
    labelCoul.Height = 16
    labelCoul.Name = "labelCoul"
    labelCoul.TabIndex = 1
    labelCoul.Label = "Période d'alternance des couleurs (lignes, syllabes, etc.) :"
    createNumericField(dialogModel, dialogModel.Width/2-30, labelCoul.PositionY+12, "fieldCoul", 0, nbcouleurs)
    dialogModel.insertByName(labelCoul.Name, labelCoul)

    createLabel(dialogModel, 10, labelCoul.PositionY+30, "labelStyles", 1, "Editer les styles :")
    createButton(dialogModel, 30, labelCoul.PositionY+42, "style_1", "style 1")
    createButton(dialogModel, 70, labelCoul.PositionY+42, "style_2", "style 2")
    createButton(dialogModel, 110, labelCoul.PositionY+42, "style_3", "style 3")
    createButton(dialogModel, 150, labelCoul.PositionY+42, "style_4", "style 4")

    # create the button model and set the properties
    createSeparator(dialogModel, 10, dialogModel.Height-21, "sep", dialogModel.Width-21)
    createButton(dialogModel, dialogModel.Width/2-61, dialogModel.Height-16, "okButtonName", "Valider", 60)
    createButton(dialogModel, dialogModel.Width/2+1, dialogModel.Height-16, "cancelButtonName", "Annuler", 60)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    controlContainer.getControl("style_1").addActionListener(EditStyleActionListener(xContext, xDocument, sb+"1"))
    controlContainer.getControl("style_2").addActionListener(EditStyleActionListener(xContext, xDocument, sb+"2"))
    controlContainer.getControl("style_3").addActionListener(EditStyleActionListener(xContext, xDocument, sb+"3"))
    controlContainer.getControl("style_4").addActionListener(EditStyleActionListener(xContext, xDocument, sb+"4"))

    controlContainer.getControl("okButtonName").addActionListener(ConfigurationStyleAlternActionListener(controlContainer))
    controlContainer.getControl("cancelButtonName").addActionListener(CancelActionListener(controlContainer))

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

######################################################################################
# Configuration de la fonction de coloriage des consonnes et des voyelles
######################################################################################
class ConfigurationConsonneVoyelle(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer les styles des consonnes et des voyelles."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_consonne_voyelle__(desktop.getCurrentComponent(), self.ctx)

def configuration_consonne_voyelle( __args=None ):
    """Ouvrir une fenêtre de dialogue pour configurer les styles des consonnes et des voyelles."""
    __configuration_consonne_voyelle__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

######################################################################################
# Boite de configuration générique pour la fonction "graphèmes complexes"
######################################################################################
def __configuration_consonne_voyelle__(xDocument, xContext):
    """Ouvrir une fenêtre de dialogue pour configurer les styles des graphèmes complexes."""

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 200
    dialogModel.PositionY = 100
    dialogModel.Width = 210
    dialogModel.Height = 70
    dialogModel.Title = "Configuration : consonnes et voyelles"

    createLink(dialogModel, dialogModel.Width-12, 10, "http://lirecouleur.arkaline.fr/faqconfig/#consonne_voyelle")

    createLabel(dialogModel, 10, 10, "labelStyles", 1, "Editer les styles de caractères :", 100)
    createButton(dialogModel, 30, 22, "phon_voyelle", "voyelles", 60)
    createButton(dialogModel, 120, 22, "phon_consonne", "consonnes", 60)

    # create the button model and set the properties
    createButton(dialogModel, dialogModel.Width/2-20, dialogModel.Height-16, "okButtonName", "Ok", 40)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    controlContainer.getControl("phon_voyelle").addActionListener(EditStyleActionListener(xContext, xDocument, "phon_voyelle"))
    controlContainer.getControl("phon_consonne").addActionListener(EditStyleActionListener(xContext, xDocument, "phon_consonne"))

    createSeparator(dialogModel, 10, dialogModel.Height-21, "sep", dialogModel.Width-21)
    controlContainer.getControl("okButtonName").addActionListener(CancelActionListener(controlContainer))

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

######################################################################################
# Configuration de la fonction de coloriage des graphèmes complexes
######################################################################################
class ConfigurationStyleGraphemesComplexes(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer les styles des graphèmes complexes."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_graphemes_complexes__(desktop.getCurrentComponent(), self.ctx)

def configuration_graphemes_complexes( __args=None ):
    """Ouvrir une fenêtre de dialogue pour configurer les styles des graphèmes complexes."""
    __configuration_graphemes_complexes__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

######################################################################################
# Boite de configuration générique pour la fonction "graphèmes complexes"
######################################################################################
def __configuration_graphemes_complexes__(xDocument, xContext):
    """Ouvrir une fenêtre de dialogue pour configurer les styles des graphèmes complexes."""

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 200
    dialogModel.PositionY = 100
    dialogModel.Width = 210
    dialogModel.Height = 70
    dialogModel.Title = "Configuration : graphèmes complexes"

    createLink(dialogModel, dialogModel.Width-12, 10, "http://lirecouleur.arkaline.fr/faqconfig/#graphemes_complexes")

    createLabel(dialogModel, 10, 10, "labelStyles", 1, "Editer les styles de caractères :", 100)
    createButton(dialogModel, 20, 22, "phon_voyelle_comp", "voyelles complexes", 80)
    createButton(dialogModel, 110, 22, "phon_consonne_comp", "consonnes complexes", 80)

    # create the button model and set the properties
    createButton(dialogModel, dialogModel.Width/2-20, dialogModel.Height-16, "okButtonName", "Ok", 40)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    controlContainer.getControl("phon_voyelle_comp").addActionListener(EditStyleActionListener(xContext, xDocument, "phon_voyelle_comp"))
    controlContainer.getControl("phon_consonne_comp").addActionListener(EditStyleActionListener(xContext, xDocument, "phon_consonne_comp"))

    createSeparator(dialogModel, 10, dialogModel.Height-21, "sep", dialogModel.Width-21)
    controlContainer.getControl("okButtonName").addActionListener(CancelActionListener(controlContainer))

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

######################################################################################
# Configuration de la fonction de coloriage des lettres
######################################################################################
class ConfigurationConfusionLettres(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer les styles de lettres."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_confusion_lettres__(desktop.getCurrentComponent(), self.ctx)

def configuration_confusion_lettres( __args=None ):
    """Ouvrir une fenêtre de dialogue pour configurer les styles des lettres."""
    __configuration_confusion_lettres__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

######################################################################################
# Boite de configuration générique pour la fonction "confusion lettres"
######################################################################################
def __configuration_confusion_lettres__(xDocument, xContext):
    """Ouvrir une fenêtre de dialogue pour configurer les styles de lettre."""

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    # récupération des infos de configuration
    settings = Settings()

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # read the already selected letters
    selectlettres = settings.get('__selection_lettres__')

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 200
    dialogModel.PositionY = 100
    dialogModel.Width = 220
    dialogModel.Height = 90
    dialogModel.Title = "Configuration : confusions lettres"

    createLink(dialogModel, dialogModel.Width-12, 10, "http://lirecouleur.arkaline.fr/faqconfig/#confusion_lettres")

    createLabel(dialogModel, 10, 10, "lbl_1", 1, "Choisir les lettres ; doublecliquer sur le libellé pour éditer le style", dialogModel.Width-12)

    # créer les checkboxes des phonèmes
    esp_y = 12 ; esp_x = 50
    i = 2 ; x = 20 ; y = 25
    createCheckBox(dialogModel, x, y, "l_b", i, 'b', selectlettres['b'], 30)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "l_d", i, 'd', selectlettres['d'], 30)
    i += 1 ; x += esp_x ; y = 25
    createCheckBox(dialogModel, x, y, "l_p", i, 'p', selectlettres['p'], 30)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "l_k", i, 'q', selectlettres['q'], 30)
    i += 1 ; x += esp_x ; y = 25
    createCheckBox(dialogModel, x, y, "l_m", i, 'm', selectlettres['m'], 30)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "l_n", i, 'n', selectlettres['n'], 30)
    i += 1 ; x += esp_x ; y = 25
    createCheckBox(dialogModel, x, y, "l_r", i, 'r', selectlettres['r'], 30)
    i += 1 ; y += esp_y
    createCheckBox(dialogModel, x, y, "l_t", i, 't', selectlettres['t'], 30)
    i += 1 ; x =20 ; y += esp_y
    createCheckBox(dialogModel, x, y, "l_f", i, 'f', selectlettres['f'], 30)
    i += 1 ; x += esp_x
    createCheckBox(dialogModel, x, y, "l_u", i, 'u', selectlettres['u'], 30)

    # create the button model and set the properties
    createSeparator(dialogModel, 10, dialogModel.Height-21, "sep", dialogModel.Width-21)
    createButton(dialogModel, dialogModel.Width/2-61, dialogModel.Height-16, "okButtonName", "Valider", 60)
    createButton(dialogModel, dialogModel.Width/2+1, dialogModel.Height-16, "cancelButtonName", "Annuler", 60)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    # add the action listener
    controlContainer.getControl("l_b").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_b'))
    controlContainer.getControl("l_d").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_d'))
    controlContainer.getControl("l_p").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_p'))
    controlContainer.getControl("l_k").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_k'))
    controlContainer.getControl("l_m").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_m'))
    controlContainer.getControl("l_n").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_n'))
    controlContainer.getControl("l_r").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_r'))
    controlContainer.getControl("l_t").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_t'))
    controlContainer.getControl("l_f").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_f'))
    controlContainer.getControl("l_u").addMouseListener(EditStyleMouseListener(xContext, xDocument, 'phon_y'))

    controlContainer.getControl("okButtonName").addActionListener(ConfigurationConfusionLettresActionListener(controlContainer))
    controlContainer.getControl("cancelButtonName").addActionListener(CancelActionListener(controlContainer))

    # create a peer
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.ExtToolkit", xContext)

    controlContainer.setVisible(False);
    controlContainer.createPeer(toolkit, None);

    # execute it
    controlContainer.execute()

    # dispose the dialog
    controlContainer.dispose()

######################################################################################
# Configuration de la fonction de marquage des lettres muettes
######################################################################################
class ConfigurationStyleLMuettes(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour configurer le marquage des lettres muettes."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_style_caractere__(desktop.getCurrentComponent(), self.ctx, "phon_muet")

######################################################################################
# Ouverture de la boite de dialogue de configuration d'un style de caractère
######################################################################################
def __configuration_style_caractere__(xDocument, xContext, nstyle):
    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    dispatcher = xContext.ServiceManager.createInstanceWithContext( 'com.sun.star.frame.DispatchHelper', xContext)
    prop1 = create_uno_struct("com.sun.star.beans.PropertyValue")
    prop1.Name = 'Param'
    prop1.Value = nstyle
    prop2 = create_uno_struct("com.sun.star.beans.PropertyValue")
    prop2.Name = 'Family'
    prop2.Value = 1
    dispatcher.executeDispatch(xDocument.getCurrentController().getFrame(), ".uno:EditStyle", "", 0, (prop1,
    prop2,))

######################################################################################
# Configuration de la fonction d'espacement des mots
######################################################################################
class ConfigurationEspace(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour l'espacement des mots."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __configuration_espace__(desktop.getCurrentComponent(), self.ctx)

def configuration_espace( __args=None ):
    """Ouvrir une fenêtre de dialogue pour l'espacement des mots."""
    __configuration_espace__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

######################################################################################
# Boite de configuration générique pour les fonctions à alternance de couleurs
######################################################################################
def __configuration_espace__(__xDocument, xContext):
    """Ouvrir une fenêtre de dialogue pour l'espacement des mots."""

    # récupération des infos de configuration
    settings = Settings()

    # i18n
    i18n()

    # get the service manager
    smgr = xContext.ServiceManager

    # lecture de la période d'alternance de lignes, de syllabes, de sons ou de mots
    nbespaces = settings.get('__subspaces__')

    # create the dialog model and set the properties
    dialogModel = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", xContext)

    dialogModel.PositionX = 200
    dialogModel.PositionY = 100
    dialogModel.Width = 210
    dialogModel.Height = 70
    dialogModel.Title = "Configuration : espacement des mots"

    # créer le champ de saisie du nombre d'espaces
    labelEsp = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    labelEsp.PositionX = 10
    labelEsp.PositionY = 10
    labelEsp.Width  = dialogModel.Width-12
    labelEsp.Height = 16
    labelEsp.Name = "labelEsp"
    labelEsp.TabIndex = 1
    labelEsp.Label = "Nombre d'espaces entre chaque mot :"
    createNumericField(dialogModel, dialogModel.Width/2-30, labelEsp.PositionY+12, "fieldEsp", 0, nbespaces, 1, 10)
    dialogModel.insertByName(labelEsp.Name, labelEsp)

    # create the button model and set the properties
    createSeparator(dialogModel, 10, dialogModel.Height-21, "sep", dialogModel.Width-21)
    createButton(dialogModel, dialogModel.Width/2-61, dialogModel.Height-16, "okButtonName", "Valider", 60)
    createButton(dialogModel, dialogModel.Width/2+1, dialogModel.Height-16, "cancelButtonName", "Annuler", 60)

    # create the dialog control and set the model
    controlContainer = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", xContext);
    controlContainer.setModel(dialogModel);

    controlContainer.getControl("okButtonName").addActionListener(ConfigurationEspaceActionListener(controlContainer))
    controlContainer.getControl("cancelButtonName").addActionListener(CancelActionListener(controlContainer))

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

    def actionPerformed(self, __actionEvent):
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

    def actionPerformed(self, __actionEvent):
        # existe déjà ?
        key = self.field1.getText().strip().lower()
        phon = self.field2.getText().strip()
        syll = self.field3.getText().strip()

        ctrl = ''.join([ph.split('.')[0] for ph in re.split('/', phon)])
        if len(ctrl) > 0 and key != ctrl:
            # les phonèmes ne redonnent pas le mot utilisé comme clé d'index
            ctrl = '/'.join([ph.split('.')[0] for ph in re.split('/', phon)])
            MsgBox(self.parent, self.toolkit, "Phonèmes"+' : '+key+' <=> '+ctrl+' ... incorrect')
            return

        ctrl = ''.join(syll.split('/'))
        if len(ctrl) > 0 and key != ctrl:
            # les syllabes ne redonnent pas le mot utilisé comme clé d'index
            MsgBox(self.parent, self.toolkit, "Syllabes"+' : '+key+' <=> '+syll+' ... incorrect')
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

    def actionPerformed(self, __actionEvent):
        if self.listdictControl.getSelectedItemPos() >= 0:
            delLCDictEntry(self.listdictControl.getSelectedItem())
            self.listdict.removeItem(self.listdictControl.getSelectedItemPos())

class GestionnaireDictionnaire(unohelper.Base, XJobExecutor):
    """Ouvrir une fenêtre de dialogue pour gérer le dictionnaire des décodages spéciaux."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __gestionnaire_dictionnaire_dialog__(desktop.getCurrentComponent(), self.ctx)

def gestionnaire_dictionnaire_dialog( __args=None ):
    """Ouvrir une fenêtre de dialogue pour gérer le dictionnaire des décodages spéciaux."""
    __gestionnaire_dictionnaire_dialog__(XSCRIPTCONTEXT.getDocument(), XSCRIPTCONTEXT.getComponentContext())

def __gestionnaire_dictionnaire_dialog__(xDocument, xContext):
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
    dialogModel.Title = "Dictionnaire LireCouleur"

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
    label1.Label = "Entrée dictionnaire"

    label2 = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    label2.PositionX = label1.PositionX+label1.Width+2
    label2.PositionY = label1.PositionY
    label2.Width  = 130
    label2.Height = 10
    label2.Name = "label2"
    label2.TabIndex = 1
    label2.Label = "Phonèmes"

    label3 = dialogModel.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    label3.PositionX = label2.PositionX+label2.Width+2
    label3.PositionY = label1.PositionY
    label3.Width  = dialogModel.Width-2-label3.PositionX
    label3.Height = 10
    label3.Name = "label3"
    label3.TabIndex = 1
    label3.Label = "Syllabes"

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

###################################################################################
# Élimine tout style de caractère
###################################################################################
class StyleDefaut(unohelper.Base, XJobExecutor):
    """Applique le style par défaut à la sélection"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_defaut__(desktop.getCurrentComponent())

def lirecouleur_defaut( __args=None ):
    """Applique le style par défaut à la sélection"""
    __lirecouleur_defaut__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Recode le texte sélectionné en noir
###################################################################################
class StyleNoir(unohelper.Base, XJobExecutor):
    """Recode le texte sélectionné en noir"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_noir__(desktop.getCurrentComponent())

def lirecouleur_noir( __args=None ):
    """Recode le texte sélectionné en noir"""
    __lirecouleur_noir__(XSCRIPTCONTEXT.getDocument())

###################################################################################
# Espace les mots de la sélection en dupliquant les espaces
###################################################################################
class StyleEspace(unohelper.Base, XJobExecutor):
    """Espace les mots de la sélection"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_espace__(desktop.getCurrentComponent())

def lirecouleur_espace( __args=None ):
    """Espace les mots de la sélection"""
    __lirecouleur_espace__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les mots de la sélection en dupliquant les espaces
###################################################################################
class StyleSepareMots(unohelper.Base, XJobExecutor):
    """Sépare les mots de la sélection en coloriant les espaces"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_espace__(desktop.getCurrentComponent())
        __lirecouleur_separe_mots__(desktop.getCurrentComponent())

def lirecouleur_separe_mots( __args=None ):
    """Sépare les mots de la sélection en coloriant les espaces"""
    __lirecouleur_espace__(XSCRIPTCONTEXT.getDocument())
    __lirecouleur_separe_mots__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les mots de la sélection en dupliquant les espaces
###################################################################################
class StyleCouleurMots(unohelper.Base, XJobExecutor):
    """Colorie les mots en alternant les couleurs (comme syll_dys)"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_couleur_mots__(desktop.getCurrentComponent())

def lirecouleur_couleur_mots( __args=None ):
    """Colorie les mots en alternant les couleurs (comme syll_dys)"""
    __lirecouleur_couleur_mots__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les lignes de la sélection
###################################################################################
class StylePara(unohelper.Base, XJobExecutor):
    """Espace les lignes de la sélection"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_espace_lignes__(desktop.getCurrentComponent())

def lirecouleur_espace_lignes( __args=None ):
    """Espace les lignes de la sélection"""
    __lirecouleur_espace_lignes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les lignes et les mots de la sélection
###################################################################################
class StyleLarge(unohelper.Base, XJobExecutor):
    """Espace les lignes et les mots de la sélection"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_large__(desktop.getCurrentComponent())

def lirecouleur_large( __args=None ):
    """Espace les lignes et les mots de la sélection"""
    __lirecouleur_large__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Espace les lignes de la sélection ainsi que les caractères
###################################################################################
class StyleExtraLarge(unohelper.Base, XJobExecutor):
    """Espace les lignes de la sélection ainsi que les caractères"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_extra_large__(desktop.getCurrentComponent())

def lirecouleur_extra_large( __args=None ):
    """Espace les lignes de la sélection ainsi que les caractères"""
    __lirecouleur_extra_large__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Marque les phonèmes sous forme de couleurs en fonction des styles du document
###################################################################################
class StylePhonemes(unohelper.Base, XJobExecutor):
    """Colorie les phonèmes en couleurs arc en ciel"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_phonemes__(desktop.getCurrentComponent())

def lirecouleur_phonemes( __args=None ):
    """Colorie les phonèmes en couleurs arc en ciel"""
    __lirecouleur_phonemes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Marque les phonèmes sous forme de couleurs en fonction des styles du document
###################################################################################
class StyleGraphemesComplexes(unohelper.Base, XJobExecutor):
    """Colorie les graphèmes complexes"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_graphemes_complexes__(desktop.getCurrentComponent())

def lirecouleur_graphemes_complexes( __args=None ):
    """Colorie les graphèmes complexes"""
    __lirecouleur_graphemes_complexes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Marque les syllabes sous forme de ponts.
###################################################################################
class StyleSyllabes(unohelper.Base, XJobExecutor):
    """Mise en évidence des syllabes soulignées"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_syllabes__(desktop.getCurrentComponent(),  "souligne")

def lirecouleur_syllabes( __args=None ):
    """Mise en évidence des syllabes soulignées"""
    __lirecouleur_syllabes__(XSCRIPTCONTEXT.getDocument(), 'souligne')

###################################################################################
# Marque les syllabes en alternant les couleurs
###################################################################################
class StyleSyllDys(unohelper.Base, XJobExecutor):
    """Mise en évidence des syllabes -- dyslexiques"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_syllabes__(desktop.getCurrentComponent(), "dys")

def lirecouleur_sylldys( __args=None ):
    """Mise en évidence des syllabes -- dyslexiques"""
    xDocument = XSCRIPTCONTEXT.getDocument()

    __lirecouleur_syllabes__(xDocument, 'dys')


###################################################################################
# Supprime les arcs sous les syllabes dans le texte sélectionné.
###################################################################################
class SupprimerSyllabes(unohelper.Base, XJobExecutor):
    """Supprime les formes ajoutées sur la page pour marquer les syllabes"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_suppr_syllabes__(desktop.getCurrentComponent())

def lirecouleur_suppr_syllabes( __args=None ):
    """Supprime les cuvettes qui marquent les liaisons"""
    __lirecouleur_suppr_syllabes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Ne marque que les lettres muettes dans le texte sélectionné.
###################################################################################
class StyleLMuettes(unohelper.Base, XJobExecutor):
    """Met uniquement en évidence les lettres muettes"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_l_muettes__(desktop.getCurrentComponent())

def lirecouleur_l_muettes( __args=None ):
    """Met uniquement en évidence les lettres muettes"""
    __lirecouleur_l_muettes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Formatte toute la sélection comme phonème muet
###################################################################################
class StylePhonMuet(unohelper.Base, XJobExecutor):
    """Formate la sélection comme phonème muet"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_phon_muet__(desktop.getCurrentComponent())

def lirecouleur_phon_muet( __args=None ):
    """Formate la sélection comme phonème muet"""
    __lirecouleur_phon_muet__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Supprime d'éventuelles décorations sous certains sons
###################################################################################
class SupprimerDecos(unohelper.Base, XJobExecutor):
    """Supprime les formes ajoutées sur la page pour marquer certains sons"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_suppr_decos__(desktop.getCurrentComponent())

def lirecouleur_suppr_decos( __args=None ):
    """Supprime les formes ajoutées sur al page pour marquer certains sons"""
    __lirecouleur_suppr_decos__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Marque la ponctuation d'un texte
###################################################################################
class StylePonctuation(unohelper.Base, XJobExecutor):
    """Marque la ponctuation d'un texte."""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_ponctuation__(desktop.getCurrentComponent())

def lirecouleur_ponctuation( __args=None ):
    """Marque la ponctuation d'un texte."""
    __lirecouleur_ponctuation__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Marque les liaisons dans le texte sélectionné.
###################################################################################
class StyleLiaisons(unohelper.Base, XJobExecutor):
    """Mise en évidence des liaisons"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_espace__(desktop.getCurrentComponent())
        __lirecouleur_liaisons__(desktop.getCurrentComponent())

def lirecouleur_liaisons( __args=None ):
    """Mise en évidence des liaisons"""
    __lirecouleur_espace__(XSCRIPTCONTEXT.getDocument())
    __lirecouleur_liaisons__(XSCRIPTCONTEXT.getDocument())

class StyleLiaisonsForcees(unohelper.Base, XJobExecutor):
    """Forcer la mise en évidence des liaisons (mode enseignant)"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_espace__(desktop.getCurrentComponent())
        __lirecouleur_liaisons__(desktop.getCurrentComponent(), forcer=True)

def lirecouleur_liaisons_forcees( __args=None ):
    """Mise en évidence des liaisons"""
    __lirecouleur_espace__(XSCRIPTCONTEXT.getDocument())
    __lirecouleur_liaisons__(XSCRIPTCONTEXT.getDocument(), forcer=True)


###################################################################################
# Colorie les lettres sélectionnées pour éviter des confusions.
###################################################################################
class ConfusionLettres(unohelper.Base, XJobExecutor):
    """Colorie les lettres sélectionnées pour éviter les confusions"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_confusion_lettres__(desktop.getCurrentComponent())

def lirecouleur_confusion_lettres( __args=None ):
    """Colorie les lettres sélectionnées pour éviter les confusions"""
    __lirecouleur_confusion_lettres__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Colorie les consonnes et les voyelles.
###################################################################################
class ConsonneVoyelle(unohelper.Base, XJobExecutor):
    """Colorie les consonnes et les voyelles"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_consonne_voyelle__(desktop.getCurrentComponent())

def lirecouleur_consonne_voyelle( __args=None ):
    """Colorie les consonnes et les voyelles"""
    __lirecouleur_consonne_voyelle__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Colorie les lignes avec une alternance de couleurs.
###################################################################################
class StyleLignesAlternees(unohelper.Base, XJobExecutor):
    """Alterne les styles pour les lignes du document"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_lignes__(desktop.getCurrentComponent())

def lirecouleur_lignes( __args=None ):
    """Alterne les styles pour les lignes du document -- dyslexiques"""
    __lirecouleur_lignes__(XSCRIPTCONTEXT.getDocument())


###################################################################################
# Colorie les phonèmes avec une alternance de couleurs.
###################################################################################
class StylePhonemesAlternes(unohelper.Base, XJobExecutor):
    """Alterne les styles pour les phonèmes du document"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_alterne_phonemes__(desktop.getCurrentComponent())

def lirecouleur_alterne_phonemes( __args=None ):
    """Alterne les styles pour les phonèmes du document -- dyslexiques"""
    __lirecouleur_alterne_phonemes__(XSCRIPTCONTEXT.getDocument())


"""
    Création d'un nouveau document LireCouleur
"""
class NewLireCouleurDocument(unohelper.Base, XJobExecutor):
    """Création d'un nouveau document LireCouleur"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __new_lirecouleur_document__(desktop.getCurrentComponent(), self.ctx)

def new_lirecouleur_document(__args=None):
    __new_lirecouleur_document__(XSCRIPTCONTEXT.getDocument(), uno.getComponentContext())

###################################################################################
# Lit le passage courant sous le curseur
###################################################################################
class LireCouleurModeleDocument(unohelper.Base, XJobExecutor):
    """Enregistrer le document courant comme modèle LireCouleur"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_modele_document__(desktop.getCurrentComponent(), self.ctx)

def lirecouleur_modele_document(__args=None):
    __lirecouleur_modele_document__(XSCRIPTCONTEXT.getDocument(), uno.getComponentContext())

def __lirecouleur_modele_document__(xDocument, xContext):
    # récupération du nom du fichier courant
    __curUrl = xDocument.getURL()

    # recherche d'un nouveau nom de fichier
    i = 1
    url = os.sep.join([getLirecouleurURL(), "template", "lirecouleur_"+str(i)+".odt"])
    while os.path.isfile(uno.fileUrlToSystemPath(url)):
        i += 1
        url = os.sep.join([getLirecouleurURL(), "template", "lirecouleur_"+str(i)+".odt"])

    # configuration du fichier modèle et enregistrement
    settings = Settings()
    settings.setValue('__template__', url)
    xDocument.storeAsURL(url, ())

    # fermer le fichier courant et réouvrir le fichier d'origine
    __new_lirecouleur_document__(xDocument, xContext)
    xDocument.close(True)

###################################################################################
# Lit le passage courant sous le curseur
###################################################################################
class LireCouleurRechargerStyles(unohelper.Base, XJobExecutor):
    """Recharger les styles de caractères à partir du modèle LireCouleur"""
    def __init__(self, ctx):
        self.ctx = ctx
    def trigger(self, __args):
        desktop = self.ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', self.ctx)
        __lirecouleur_recharger_styles__(desktop.getCurrentComponent())

def lirecouleur_recharger_styles(__args=None):
    __lirecouleur_recharger_styles__(XSCRIPTCONTEXT.getDocument())

###################################################################################
# lists the scripts, that shall be visible inside OOo. Can be omitted.
###################################################################################
g_exportedScripts = lirecouleur_defaut, lirecouleur_espace, lirecouleur_phonemes, lirecouleur_syllabes, \
lirecouleur_sylldys, lirecouleur_l_muettes, gestionnaire_config_dialog, lirecouleur_liaisons, \
lirecouleur_liaisons_forcees, lirecouleur_confusion_lettres, lirecouleur_suppr_syllabes, lirecouleur_lignes, \
lirecouleur_ponctuation, lirecouleur_suppr_decos, lirecouleur_phon_muet, lirecouleur_graphemes_complexes, \
new_lirecouleur_document, gestionnaire_dictionnaire_dialog, lirecouleur_espace_lignes, lirecouleur_consonne_voyelle, \
lirecouleur_large, lirecouleur_extra_large, lirecouleur_noir, lirecouleur_separe_mots, \
lirecouleur_couleur_mots, lirecouleur_alterne_phonemes, lirecouleur_recharger_styles, \
configuration_phonemes, configuration_sylldys, configuration_lignes, configuration_couleur_mots, \
configuration_alterne_phonemes, configuration_graphemes_complexes, configuration_consonne_voyelle, \
configuration_confusion_lettres, configuration_syllabes, configuration_espace, lirecouleur_modele_document,

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
    ConfusionLettres,'org.lirecouleur.ConfusionLettres', \
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
    StylePonctuation,'org.lirecouleur.StylePonctuation', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StylePhonMuet,'org.lirecouleur.StylePhonMuet', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    StyleGraphemesComplexes,'org.lirecouleur.StyleGraphemesComplexes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    NewLireCouleurDocument,'org.lirecouleur.NewLireCouleurDocument', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    GestionnaireDictionnaire,'org.lirecouleur.GestionnaireDictionnaire', \
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

g_ImplementationHelper.addImplementation( \
    StylePhonemesAlternes,'org.lirecouleur.StylePhonemesAlternes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationConsonneVoyelle,'org.lirecouleur.ConfigurationConsonneVoyelle', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationConfusionLettres,'org.lirecouleur.ConfigurationConfusionLettres', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleLMuettes,'org.lirecouleur.ConfigurationStyleLMuettes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationPhonemes,'org.lirecouleur.ConfigurationPhonemes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStylePhonemesAlternes,'org.lirecouleur.ConfigurationStylePhonemesAlternes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleGraphemesComplexes,'org.lirecouleur.ConfigurationStyleGraphemesComplexes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleSyllDys,'org.lirecouleur.ConfigurationStyleSyllDys', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleSyllabes,'org.lirecouleur.ConfigurationStyleSyllabes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleLMuettes,'org.lirecouleur.ConfigurationStyleLMuettes', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationEspace,'org.lirecouleur.ConfigurationEspace', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleCouleurMots,'org.lirecouleur.ConfigurationStyleCouleurMots', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleSepareMots,'org.lirecouleur.ConfigurationStyleSepareMots', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleLignesAlternees,'org.lirecouleur.ConfigurationStyleLignesAlternees', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStylePonctuation,'org.lirecouleur.ConfigurationStylePonctuation', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleLiaisons,'org.lirecouleur.ConfigurationStyleLiaisons', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    ConfigurationStyleLiaisonsForcees,'org.lirecouleur.ConfigurationStyleLiaisonsForcees', \
    ('com.sun.star.task.Job',))

g_ImplementationHelper.addImplementation( \
    LireCouleurModeleDocument,'org.lirecouleur.LireCouleurModeleDocument', \
    ('com.sun.star.task.Job',))


g_ImplementationHelper.addImplementation( \
    LireCouleurRechargerStyles,'org.lirecouleur.LireCouleurRechargerStyles', \
    ('com.sun.star.task.Job',))

"""

"""
if __name__ == "__main__":
    # get the uno component context from the PyUNO runtime
    localContext = uno.getComponentContext()

    # create the UnoUrlResolver
    resolver = localContext.ServiceManager.createInstanceWithContext(
                "com.sun.star.bridge.UnoUrlResolver", localContext )

    # connect to the running office
    ctx = resolver.resolve( "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext" )
    smgr = ctx.ServiceManager

    # get the central desktop object
    desktop = smgr.createInstanceWithContext( "com.sun.star.frame.Desktop",ctx)

    # access the current writer document
    xDocument = desktop.getCurrentComponent()

    __lirecouleur_phonemes__(xDocument)
    #__configuration_phonemes__(xDocument, ctx)
    #__lirecouleur_recharger_styles__(xDocument)
