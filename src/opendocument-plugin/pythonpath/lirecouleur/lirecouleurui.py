#!/usr/bin/env python
# -*- coding: UTF-8 -*-

###################################################################################
# Macro destinée à l'affichage de textes en couleur et à la segmentation
# de mots en syllabes
#
# voir http://lirecouleur.arkaline.fr
#
# @author Marie-Pierre Brungard
# @version 3.7
# @since 2015
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
import gettext
import os
import sys
import re

from .utils import (Settings, create_uno_service, create_uno_struct)
from .lirecouleur import (generer_paragraphe_phonemes, pretraitement_texte, nettoyeur_caracteres, loadLCDict, u,
                          teste_liaison, generer_paragraphe_syllabes)

__version__ = "4.7"

# create LANG environment variable
import locale
if os.getenv('LANG') is None:
    lang, enc = locale.getdefaultlocale()
    os.environ['LANG'] = lang
#os.environ['LANGUAGE'] = os.environ['LANG']

#########################################################################################################
#########################################################################################################
#
#    Fonctions préliminaires utilitaires
#
#                                    @@@@@@@@@@@@@@@@@@@@@@
#
#########################################################################################################
#########################################################################################################
def getLirecouleurTemplateURL():
    settings = Settings()
    url = settings.get('__template__')
    if len(url) > 0:
        return url

    localdir = os.sep.join([getLirecouleurDirectory(), 'locale'])
    loclang = os.environ['LANG']
    tempname = os.sep.join([localdir, loclang, "lirecouleur.ott"])
    if os.path.isfile(tempname):
        return uno.systemPathToFileUrl(tempname)
    loclang = loclang.split('.')[0]
    tempname = os.sep.join([localdir, loclang, "lirecouleur.ott"])
    if os.path.isfile(tempname):
        return uno.systemPathToFileUrl(tempname)
    loclang = loclang.split('_')[0]
    tempname = os.sep.join([localdir, loclang, "lirecouleur.ott"])
    if os.path.isfile(tempname):
        return uno.systemPathToFileUrl(tempname)
    
    url = getLirecouleurURL()
    if not url is None:
        url = os.sep.join([url, "template", "lirecouleur.ott"])
        if os.path.isfile(uno.fileUrlToSystemPath(url)):
            return url
    for chem in sys.path:
        url = os.sep.join([chem, "template", "lirecouleur.ott"])
        if os.path.isfile(url):
            return uno.systemPathToFileUrl(url)
    return ""

def getLirecouleurTemplateDirURL():
    url = getLirecouleurTemplateURL()
    if len(url) > 0:
        url = os.sep.join(url.split(os.sep)[:-1])+os.sep
    return url

def getLirecouleurDictionary():
    localdir = os.sep.join([getLirecouleurDirectory(), 'locale'])
    loclang = os.environ['LANG']
    tempname = os.sep.join([localdir, loclang, "lirecouleur.dic"])
    if os.path.isfile(tempname):
        return tempname
    loclang = loclang.split('.')[0]
    tempname = os.sep.join([localdir, loclang, "lirecouleur.dic"])
    if os.path.isfile(tempname):
        return tempname
    loclang = loclang.split('_')[0]
    tempname = os.sep.join([localdir, loclang, "lirecouleur.dic"])
    if os.path.isfile(tempname):
        return tempname
    return os.sep.join([getLirecouleurDirectory(), "lirecouleur.dic"])

"""
    morceau de code très sale pour identifier si on utilise OpenOffice ou LibreOffice : les 2 n'ont pas
    la même façon de noter le style par défaut.
"""
def getOOoSetupNode(sNodePath):
    oConfigProvider = create_uno_service('com.sun.star.configuration.ConfigurationProvider')
    ppp = create_uno_struct("com.sun.star.beans.PropertyValue")
    ppp.Name = "nodepath"
    ppp.Value = sNodePath
    return oConfigProvider.createInstanceWithArguments("com.sun.star.configuration.ConfigurationAccess", (ppp,))

def getOOoSetupValue(sNodePath, sProperty):
    xConfig = getOOoSetupNode(sNodePath)
    return xConfig.getByName(sProperty)

"""
    Get the URL of LireCouleur
"""
def getLirecouleurURL():
    """Get the URL of LireCouleur"""
    try:
        pip = uno.getComponentContext().getValueByName("/singletons/com.sun.star.deployment.PackageInformationProvider")
        url = pip.getPackageLocation("lire.libre.lirecouleur")
        if len(url) > 0:
            return url
    except:
        pass

    try:
        # just for debugging outside the extension scope
        filename = uno.fileUrlToSystemPath(__file__)
        return uno.systemPathToFileUrl(os.path.dirname(os.path.abspath(filename)))
    except:
        pass

    try:
        xPathSettingsService = create_uno_service('com.sun.star.util.PathSettings')
        xUserPath = xPathSettingsService.getPropertyValue('UserConfig').split(os.sep)[:-1]
        xUserPath.extend(['Scripts', 'python'])
        return os.sep.join(xUserPath)
    except:
        pass
    return None

"""
    Get the name of the directory of LireCouleur
"""
def getLirecouleurDirectory():
    """Get the name of the directory of LireCouleur"""
    try:
        return uno.fileUrlToSystemPath(getLirecouleurURL())
    except:
        return ""

"""

"""
def i18n():
    localdir = os.sep.join([getLirecouleurDirectory(), 'locale'])
    gettext.bindtextdomain('lirecouleur', localdir)
    gettext.textdomain('lirecouleur')

#########################################################################################################
#########################################################################################################
#
#    Cette partie du code est destinée à la présentation dans OOo des phonèmes
#    et des syllabes de différentes manières.
#
#                                    @@@@@@@@@@@@@@@@@@@@@@
#
#########################################################################################################
#########################################################################################################

###################################################################################
# Ensemble des styles d'affichage des phonèmes selon différents codages
# voir http://wiki.services.openoffice.org/wiki/Documentation/DevGuide/Text/Formatting
###################################################################################
style_phon_perso = {
        'verb_3p':{'CharStyleName':'conjug_3p'},
        '#':{'CharStyleName':'phon_muet'},
        'q_caduc':{'CharStyleName':'phon_e_caduc'},
        'a':{'CharStyleName':'phon_a'},
        'q':{'CharStyleName':'phon_e'},
        'i':{'CharStyleName':'phon_i'},
        'o':{'CharStyleName':'phon_o'},
        'o_comp':{'CharStyleName':'phon_o_comp'},
        'o_ouvert':{'CharStyleName':'phon_o_ouvert'},
        'u':{'CharStyleName':'phon_ou'},
        'y':{'CharStyleName':'phon_u'},
        'e':{'CharStyleName':'phon_ez'},
        'e_comp':{'CharStyleName':'phon_ez_comp'},
        'w':{'CharStyleName':'phon_w'},
        'wa':{'CharStyleName':'phon_wa'},
        'e^':{'CharStyleName':'phon_et'},
        'e^_comp':{'CharStyleName':'phon_et_comp'},
        'a~':{'CharStyleName':'phon_an'},
        'e~':{'CharStyleName':'phon_in'},
        'x~':{'CharStyleName':'phon_un'},
        'o~':{'CharStyleName':'phon_on'},
        'x':{'CharStyleName':'phon_oe'},
        'x^':{'CharStyleName':'phon_eu'},
        'j':{'CharStyleName':'phon_y'},
        'z_s':{'CharStyleName':'phon_z'},
        'g_u':{'CharStyleName':'phon_g'},
        'z^_g':{'CharStyleName':'phon_ge'},
        's_x':{'CharStyleName':'phon_s'},
        'n~':{'CharStyleName':'phon_gn'},
        'p':{'CharStyleName':'phon_p'},
        't':{'CharStyleName':'phon_t'},
        'k':{'CharStyleName':'phon_k'},
        'k_qu':{'CharStyleName':'phon_k'},
        'b':{'CharStyleName':'phon_b'},
        'd':{'CharStyleName':'phon_d'},
        'g':{'CharStyleName':'phon_g'},
        'f':{'CharStyleName':'phon_f'},
        'f_ph':{'CharStyleName':'phon_f'},
        's':{'CharStyleName':'phon_s'},
        's_c':{'CharStyleName':'phon_s'},
        's_t':{'CharStyleName':'phon_s'},
        's^':{'CharStyleName':'phon_ch'},
        'v':{'CharStyleName':'phon_v'},
        'z':{'CharStyleName':'phon_z'},
        'z^':{'CharStyleName':'phon_ge'},
        'm':{'CharStyleName':'phon_m'},
        'n':{'CharStyleName':'phon_n'},
        'l':{'CharStyleName':'phon_l'},
        'r':{'CharStyleName':'phon_r'},
        'ks':{'CharStyleName':'phon_ks'},
        'gz':{'CharStyleName':'phon_gz'},
        'espace':{'CharStyleName':'espace'},
        'liaison':{'CharStyleName':'liaison'},
        'consonne':{'CharStyleName':'phon_consonne'},
        'voyelle':{'CharStyleName':'phon_voyelle'},
        'ponctuation':{'CharStyleName':'ponctuation'}
        }

style_phon_complexes = {
        'verb_3p':{'CharStyleName':'conjug_3p'},
        '#':{'CharStyleName':'phon_muet'},
        'o_comp':{'CharStyleName':'phon_voyelle_comp'},
        'u':{'CharStyleName':'phon_voyelle_comp'},
        'e_comp':{'CharStyleName':'phon_voyelle_comp'},
        'w':{'CharStyleName':'phon_voyelle_comp'},
        'wa':{'CharStyleName':'phon_voyelle_comp'},
        'e^_comp':{'CharStyleName':'phon_voyelle_comp'},
        'a~':{'CharStyleName':'phon_voyelle_comp'},
        'e~':{'CharStyleName':'phon_voyelle_comp'},
        'x~':{'CharStyleName':'phon_voyelle_comp'},
        'o~':{'CharStyleName':'phon_voyelle_comp'},
        'x':{'CharStyleName':'phon_voyelle_comp'},
        'x^':{'CharStyleName':'phon_voyelle_comp'},
        'j':{'CharStyleName':'phon_consonne_comp'},
        'z_s':{'CharStyleName':'phon_consonne_comp'},
        'g_u':{'CharStyleName':'phon_consonne_comp'},
        'z^_g':{'CharStyleName':'phon_consonne_comp'},
        's_x':{'CharStyleName':'phon_consonne_comp'},
        'n~':{'CharStyleName':'phon_consonne_comp'},
        'k_qu':{'CharStyleName':'phon_consonne_comp'},
        'f_ph':{'CharStyleName':'phon_consonne_comp'},
        's_c':{'CharStyleName':'phon_consonne_comp'},
        's_t':{'CharStyleName':'phon_consonne_comp'},
        's^':{'CharStyleName':'phon_consonne_comp'},
        'ks':{'CharStyleName':'phon_consonne_comp'},
        'gz':{'CharStyleName':'phon_consonne_comp'},
        'espace':{'CharStyleName':'espace'},
        'liaison':{'CharStyleName':'liaison'},
        'consonne':{'CharStyleName':'phon_consonne'},
        'voyelle':{'CharStyleName':'phon_voyelle'},
        'ponctuation':{'CharStyleName':'ponctuation'}
        }

__style_phon_perso__ = {
        'verb_3p':{'CharColor':0x00aaaaaa},
        '#':{'CharColor':0x00aaaaaa},
        '#_amb':{'CharColor':0x0000000},
        'q_caduc':{'CharColor':0X00aaaaaa},
        'a':{'CharColor':0x000068de},
        'a~':{'CharColor':0x000068de, 'CharShadowed':True},
        'q':{'CharColor':0X00ef001e},
        'i':{'CharColor':0X003deb3d},
        'e~':{'CharColor':0X003deb3d, 'CharShadowed':True},
        'o':{'CharColor':0X00de7004},
        'o_comp':{'CharColor':0X00de7004},
        'o_ouvert':{'CharColor':0X00de7004},
        'o~':{'CharColor':0X00de7004, 'CharShadowed':True},
        'u':{'CharColor':0X00ffc305},
        'y':{'CharColor':0X005c8526},
        'x~':{'CharColor':0X005c8526, 'CharShadowed':True},
        'e':{'CharColor':0X00008080},
        'e_comp':{'CharColor':0X00008080},
        'e^':{'CharColor':0X000ecd5, 'CharShadowed':True},
        'e^_comp':{'CharColor':0X000ecd5, 'CharShadowed':True},
        'x':{'CharColor':0X00dc2300},
        'x^':{'CharColor':0X00800000},
        'w':{'CharColor':0X00892ca0},
        'wa':{'CharColor':0X00892ca0},
        'j':{'CharColor':0X00892ca0, 'CharShadowed':True},
        'z_s':{'CharColor':0x0000000, 'CharWeight':150.0},
        'g_u':{'CharColor':0x0000000, 'CharWeight':150.0},
        'z^_g':{'CharColor':0x0000000, 'CharWeight':150.0},
        's_x':{'CharColor':0x0000000, 'CharWeight':150.0},
        'n~':{'CharColor':0x0000000, 'CharWeight':150.0},
        'p':{'CharColor':0x0000000, 'CharWeight':150.0},
        't':{'CharColor':0x0000000, 'CharWeight':150.0},
        'k':{'CharColor':0x0000000, 'CharWeight':150.0},
        'k_qu':{'CharColor':0x0000000, 'CharWeight':150.0},
        'b':{'CharColor':0x0000000, 'CharWeight':150.0},
        'd':{'CharColor':0x0000000, 'CharWeight':150.0},
        'g':{'CharColor':0x0000000, 'CharWeight':150.0},
        'f':{'CharColor':0x0000000, 'CharWeight':150.0},
        'f_ph':{'CharColor':0x0000000, 'CharWeight':150.0},
        's':{'CharColor':0x0000000, 'CharWeight':150.0},
        's_c':{'CharColor':0x0000000, 'CharWeight':150.0},
        's_t':{'CharColor':0x0000000, 'CharWeight':150.0},
        's^':{'CharColor':0x0000000, 'CharWeight':150.0},
        'v':{'CharColor':0x0000000, 'CharWeight':150.0},
        'z':{'CharColor':0x0000000, 'CharWeight':150.0},
        'z^':{'CharColor':0x0000000, 'CharWeight':150.0},
        'm':{'CharColor':0x0000000, 'CharWeight':150.0},
        'n':{'CharColor':0x0000000, 'CharWeight':150.0},
        'l':{'CharColor':0x0000000, 'CharWeight':150.0},
        'r':{'CharColor':0x0000000, 'CharWeight':150.0},
        'ks':{'CharColor':0x0000000, 'CharWeight':150.0},
        'gz':{'CharColor':0x0000000, 'CharWeight':150.0},
        'espace':{'CharBackColor':0x00ff00ff},
        'liaison':{'CharScaleWidth':200, 'CharUnderline':10},
        'consonne':{'CharColor':0x000000ff},
        'voyelle':{'CharColor':0x00ff0000},
        'ponctuation':{'CharBackColor':0x00ff0000}
        }

__style_phon_complexes__ = {
        'verb_3p':{'CharColor':0x0000000, 'CharContoured':True},
        '#':{'CharColor':0x0000000, 'CharContoured':True},
        'q_caduc':{'CharColor':0x00000000},
        'a':{'CharColor':0x0000000},
        'q':{'CharColor':0x0000000},
        'i':{'CharColor':0x0000000},
        'o':{'CharColor':0x0000000},
        'o_comp':{'CharColor':0x00ff950e},
        'o_ouvert':{'CharColor':0x0000000},
        'u':{'CharColor':0x00ff950e},
        'y':{'CharColor':0x0000000},
        'e':{'CharColor':0x0000000},
        'e_comp':{'CharColor':0x00ff950e},
        'w':{'CharColor':0x00ff950e},
        'wa':{'CharColor':0x00ff950e},
        'e^':{'CharColor':0x0000000},
        'e^_comp':{'CharColor':0x00ff950e},
        'a~':{'CharColor':0x00ff950e},
        'e~':{'CharColor':0x00ff950e},
        'x~':{'CharColor':0x00ff950e},
        'o~':{'CharColor':0x00ff950e},
        'x':{'CharColor':0x00ff950e},
        'x^':{'CharColor':0x00ff950e},
        'j':{'CharColor':0x00aecf00},
        'z_s':{'CharColor':0x00aecf00},
        'g_u':{'CharColor':0x00aecf00},
        'z^_g':{'CharColor':0x00aecf00},
        's_x':{'CharColor':0x00aecf00},
        'n~':{'CharColor':0x00aecf00},
        'p':{'CharColor':0x0000000},
        't':{'CharColor':0x0000000},
        'k':{'CharColor':0x0000000},
        'k_qu':{'CharColor':0x00aecf00},
        'b':{'CharColor':0x0000000},
        'd':{'CharColor':0x0000000},
        'g':{'CharColor':0x0000000},
        'f':{'CharColor':0x0000000},
        'f_ph':{'CharColor':0x00aecf00},
        's':{'CharColor':0x0000000},
        's_c':{'CharColor':0x00aecf00},
        's_t':{'CharColor':0x00aecf00},
        's^':{'CharColor':0x00aecf00},
        'v':{'CharColor':0x0000000},
        'z':{'CharColor':0x0000000},
        'z^':{'CharColor':0x0000000},
        'm':{'CharColor':0x0000000},
        'n':{'CharColor':0x0000000},
        'l':{'CharColor':0x0000000},
        'r':{'CharColor':0x0000000},
        'ks':{'CharColor':0x00aecf00},
        'gz':{'CharColor':0x00aecf00},
        '#_amb':{'CharColor':0x0000000},
        'espace':{'CharBackColor':0x00ff00ff},
        'liaison':{'CharScaleWidth':200, 'CharUnderline':10},
        'consonne':{'CharColor':0x000000ff},
        'voyelle':{'CharColor':0x00ff0000},
        'ponctuation':{'CharBackColor':0x00ff0000}
        }

style_phon_altern = {
        '1' : {'CharStyleName':'altern_phon_1'},
        '2' : {'CharStyleName':'altern_phon_2'},
        '3' : {'CharStyleName':'altern_phon_3'},
        '4' : {'CharStyleName':'altern_phon_4'}
        }

__style_phon_altern__ = {
        '1' : {'CharColor':0x000000ff},
        '2' : {'CharColor':0x00ff0000},
        '3' : {'CharColor':0x0000ff00},
        '4' : {'CharColor':0x00ff00ff}
        }

style_syll_dys = {
        '1': {'CharStyleName':'syll_dys_1'},
        '2': {'CharStyleName':'syll_dys_2'},
        '3': {'CharStyleName':'syll_dys_3'},
        '4': {'CharStyleName':'syll_dys_4'}
        }

__style_syll_dys__ = {
        '1': {'CharColor':0x000000ff},
        '2': {'CharColor':0x00ff0000},
        '3': {'CharColor':0x0000ff00},
        '4': {'CharColor':0x00ff00ff}
        }

style_mot_dys = {
        '1': {'CharStyleName':'mot_dys_1'},
        '2': {'CharStyleName':'mot_dys_2'},
        '3': {'CharStyleName':'mot_dys_3'},
        '4': {'CharStyleName':'mot_dys_4'}
        }

__style_mot_dys__ = {
        '1': {'CharColor':0x000000ff},
        '2': {'CharColor':0x00ff0000},
        '3': {'CharColor':0x0000ff00},
        '4': {'CharColor':0x00ff00ff}
        }

style_yod = {
        'a':{'CharStyleName':'yod_phon_a'},
        'q':{'CharStyleName':'yod_phon_e'},
        'q_caduc':{'CharStyleName':'yod_phon_e_caduc'},
        'i':{'CharStyleName':'yod_phon_i'},
        'o':{'CharStyleName':'yod_phon_o'},
        'o_comp':{'CharStyleName':'yod_phon_o_comp'},
        'o_ouvert':{'CharStyleName':'yod_phon_o_ouvert'},
        'u':{'CharStyleName':'yod_phon_ou'},
        'e':{'CharStyleName':'yod_phon_ez'},
        'e_comp':{'CharStyleName':'yod_phon_ez_comp'},
        'e^':{'CharStyleName':'yod_phon_et'},
        'e^_comp':{'CharStyleName':'yod_phon_et_comp'},
        'a~':{'CharStyleName':'yod_phon_an'},
        'e~':{'CharStyleName':'yod_phon_in'},
        'x~':{'CharStyleName':'yod_phon_un'},
        'o~':{'CharStyleName':'yod_phon_on'},
        'x':{'CharStyleName':'yod_phon_oe'},
        'x^':{'CharStyleName':'yod_phon_eu'}
        }

__style_yod__ = {
        'a':{'CharColor':__style_phon_perso__['a']['CharColor'], 'CharUnderline':11},
        'a~':{'CharColor':__style_phon_perso__['a~']['CharColor'], 'CharUnderline':11},
        'q':{'CharColor':__style_phon_perso__['q']['CharColor'], 'CharUnderline':11},
        'q_caduc':{'CharColor':__style_phon_perso__['q_caduc']['CharColor'], 'CharUnderline':11},
        'i':{'CharColor':__style_phon_perso__['i']['CharColor'], 'CharUnderline':11},
        'e~':{'CharColor':__style_phon_perso__['e~']['CharColor'], 'CharUnderline':11},
        'o':{'CharColor':__style_phon_perso__['o']['CharColor'], 'CharUnderline':11},
        'o_comp':{'CharColor':__style_phon_perso__['o_comp']['CharColor'], 'CharUnderline':11},
        'o_ouvert':{'CharColor':__style_phon_perso__['o_ouvert']['CharColor'], 'CharUnderline':11},
        'o~':{'CharColor':__style_phon_perso__['o~']['CharColor'], 'CharUnderline':11},
        'u':{'CharColor':__style_phon_perso__['u']['CharColor'], 'CharUnderline':11},
        'x~':{'CharColor':__style_phon_perso__['x~']['CharColor'], 'CharUnderline':11},
        'e':{'CharColor':__style_phon_perso__['e']['CharColor'], 'CharUnderline':11},
        'e_comp':{'CharColor':__style_phon_perso__['e_comp']['CharColor'], 'CharUnderline':11},
        'e^':{'CharColor':__style_phon_perso__['e^']['CharColor'], 'CharUnderline':11},
        'e^_comp':{'CharColor':__style_phon_perso__['e^_comp']['CharColor'], 'CharUnderline':11},
        'x':{'CharColor':__style_phon_perso__['x']['CharColor'], 'CharUnderline':11},
        'x^':{'CharColor':__style_phon_perso__['x^']['CharColor'], 'CharUnderline':11}
        }

style_wau = {
        'a':{'CharStyleName':'wau_phon_a'},
        'i':{'CharStyleName':'wau_phon_i'},
        'e':{'CharStyleName':'wau_phon_ez'},
        'e_comp':{'CharStyleName':'wau_phon_ez_comp'},
        'e^':{'CharStyleName':'wau_phon_et'},
        'e^_comp':{'CharStyleName':'wau_phon_et_comp'},
        'a~':{'CharStyleName':'wau_phon_an'},
        'e~':{'CharStyleName':'wau_phon_in'},
        'x~':{'CharStyleName':'wau_phon_un'},
        'o~':{'CharStyleName':'wau_phon_on'},
        'x^':{'CharStyleName':'wau_phon_eu'}
        }

__style_wau__ = {
        'a':{'CharColor':__style_phon_perso__['a']['CharColor'], 'CharUnderline':12},
        'i':{'CharColor':__style_phon_perso__['i']['CharColor'], 'CharUnderline':12},
        'e':{'CharColor':__style_phon_perso__['e']['CharColor'], 'CharUnderline':12},
        'e_comp':{'CharColor':__style_phon_perso__['e_comp']['CharColor'], 'CharUnderline':12},
        'e^':{'CharColor':__style_phon_perso__['e^']['CharColor'], 'CharUnderline':11},
        'e^_comp':{'CharColor':__style_phon_perso__['e^_comp']['CharColor'], 'CharUnderline':12},
        'a~':{'CharColor':__style_phon_perso__['a~']['CharColor'], 'CharUnderline':12},
        'e~':{'CharColor':__style_phon_perso__['e~']['CharColor'], 'CharUnderline':12},
        'x~':{'CharColor':__style_phon_perso__['x~']['CharColor'], 'CharUnderline':12},
        'o~':{'CharColor':__style_phon_perso__['o~']['CharColor'], 'CharUnderline':12},
        'x^':{'CharColor':__style_phon_perso__['x^']['CharColor'], 'CharUnderline':12}
        }

style_semi = {
        'j' : style_yod,
        'w' : style_wau
        }

######################################################################################
#
######################################################################################
styles_phonemes = {
        'perso' : style_phon_perso,
        'complexes' : style_phon_complexes,
        'alterne' : style_phon_altern
        }

styles_syllabes = {
        'dys' : style_syll_dys
        }


styles_mots = {
        'dys' : style_mot_dys
        }

######################################################################################
#
######################################################################################
__styles_lignes_altern__ = {
        '1':{'CharBackColor':0x00ffff66},
        '2':{'CharBackColor':0x0023ff23},
        '3':{'CharBackColor':0x00ff9966},
        '4':{'CharBackColor':0x0000ffdc}
        }

styles_lignes_altern = {
        '1':{'CharStyleName':'altern_ligne_1'},
        '2':{'CharStyleName':'altern_ligne_2'},
        '3':{'CharStyleName':'altern_ligne_3'},
        '4':{'CharStyleName':'altern_ligne_4'}
        }

styles_lignes = 'altern_ligne_'

######################################################################################
# Création des styles de caractères nécessaires à l'application
######################################################################################
def createCharacterStyles(xModel, style_nom, style_forme):
    """ Création des styles de caractères nécessaires à l'application """
    charStyles = xModel.getStyleFamilies().getByName('CharacterStyles')

    # then create the other character styles
    for phon in style_nom.keys():
        charstylename = style_nom[phon]['CharStyleName']
        if len(charstylename) > 0 and not charStyles.hasByName(charstylename):
            try:
                charstylestruct = style_forme[phon]
                tmp_style = xModel.createInstance('com.sun.star.style.CharacterStyle')    # create a char style
                for kpv in charstylestruct.keys():
                    tmp_style.setPropertyValue(kpv, charstylestruct[kpv])
                tmp_style.setParentStyle('LireCouleur')    # set parent charstyle
                charStyles.insertByName(charstylename, tmp_style)
            except:
                pass

def makeShape(oDrawDoc, cShapeClassName, oPosition=None, oSize=None):
    """Create a new shape of the specified class.
    Position and size arguments are optional.
    """
    oShape = oDrawDoc.createInstance(cShapeClassName)

    if oPosition != None:
        oShape.Position = oPosition
    if oSize != None:
        oShape.Size = oSize

    return oShape

def makeTextShape(oDrawDoc, oPosition=None, oSize=None):
    """Create a new TextShape with an optional position and size."""
    oShape = makeShape(oDrawDoc, "com.sun.star.drawing.TextShape", oPosition, oSize)
    oShape.TextHorizontalAdjust = 0
    oShape.TextVerticalAdjust = 0
    oShape.TextAutoGrowWidth = True
    oShape.TextAutoGrowHeight = True
    oShape.TextLeftDistance = 0
    oShape.TextRightDistance = 0
    oShape.TextUpperDistance = 0
    oShape.TextLowerDistance = 0
    return oShape

def makeSize(nWidth, nHeight):
    """Create a com.sun.star.awt.Size struct."""
    oSize = create_uno_struct("com.sun.star.awt.Size")
    oSize.Width = nWidth
    oSize.Height = nHeight
    return oSize

def makePoint(nX, nY):
    """Create a com.sun.star.awt.Point struct."""
    oPoint = create_uno_struct("com.sun.star.awt.Point")
    oPoint.X = nX
    oPoint.Y = nY
    return oPoint

######################################################################################
# Récupération éventuelle des styles de caractères
######################################################################################
__memDocument__ = None
def importStylesLireCouleur(xModel):
    global __memDocument__
    if __memDocument__ != xModel:
        # si on n'a pas changé de document, pas besoin de recharger les styles
        __memDocument__ = xModel
    
        try:
            """
                Importation des styles à partir d'un fichier odt
            """
            ''' chemin d'accès au fichier qui contient les styles à utiliser '''
            url = getLirecouleurTemplateURL()

            ppp1 = create_uno_struct("com.sun.star.beans.PropertyValue")
            ppp1.Name = "LoadPageStyles"
            ppp1.Value = False
            ppp2 = create_uno_struct("com.sun.star.beans.PropertyValue")
            ppp2.Name = "LoadFrameStyles"
            ppp2.Value = False
            ppp3 = create_uno_struct("com.sun.star.beans.PropertyValue")
            ppp3.Name = "LoadNumberingStyles"
            ppp3.Value = False
            ppp4 = create_uno_struct("com.sun.star.beans.PropertyValue")
            ppp4.Name = "LoadTextStyles" # on veut écraser uniquement les styles de texte
            ppp4.Value = True
            ppp5 = create_uno_struct("com.sun.star.beans.PropertyValue")
            ppp5.Name = "OverwriteStyles" # on ne veut pas écraser les styles existants
            ppp5.Value = False
            xModel.getStyleFamilies().loadStylesFromURL(url, (ppp1, ppp2, ppp3, ppp4, ppp5,))
        except:            
            createCharacterStyles(xModel, style_phon_perso, __style_phon_perso__)
            createCharacterStyles(xModel, style_phon_complexes, __style_phon_complexes__)
            createCharacterStyles(xModel, style_syll_dys, __style_syll_dys__)
            createCharacterStyles(xModel, style_mot_dys, __style_mot_dys__)
            createCharacterStyles(xModel, styles_lignes_altern, __styles_lignes_altern__)
            createCharacterStyles(xModel, style_phon_altern, __style_phon_altern__)
            createCharacterStyles(xModel, style_yod, __style_yod__)
            createCharacterStyles(xModel, style_wau, __style_wau__)
    
    # ajuster le style des e caduc en fonction du choix d'affichage entre "syllabes orales" ou "syllabes écrites"
    settings = Settings()
    if settings.get('__syllo__')[1]:
        # syllabes orales : e caduc affiché comme le phonème muet
        style_phon_perso['q_caduc'] = style_phon_perso['#']
        style_yod['q_caduc']['CharStyleName'] = 'phon_y'
    else:
        # syllabes écrites : e caduc affiché comme le e
        style_phon_perso['q_caduc'] = style_phon_perso['q']
        style_yod['q_caduc']['CharStyleName'] = 'yod_phon_e_caduc'

######################################################################################
# Place un point sous une lettre muette
######################################################################################
def marquePoint(xDocument, txt_phon, cursor):
    from com.sun.star.text.TextContentAnchorType import AT_CHARACTER
    from com.sun.star.text.WrapTextMode import THROUGHT
    from com.sun.star.text.RelOrientation import CHAR
    from com.sun.star.text.HoriOrientation import LEFT
    from com.sun.star.text.VertOrientation import CHAR_BOTTOM

    xText = cursor.getText()
    __oWindow = xDocument.getCurrentController().getFrame().getContainerWindow()

    xViewCursorSupplier = xDocument.getCurrentController()
    xTextViewCursor = xViewCursorSupplier.getViewCursor()
    xTextViewCursor.gotoRange(cursor, False) # remet le curseur physique au début (du mot)
    x0 = xTextViewCursor.Position.X

    hh = cursor.getPropertyValue("CharHeight")

    # déplace le curseur physique pour calculer la longueur de la cuvette à dessiner
    xTextViewCursor.goRight(len(txt_phon), False)
    x1 = xTextViewCursor.Position.X
    if x1 < x0:
        xTextViewCursor.goLeft(len(txt_phon), False)
        xTextViewCursor.gotoEndOfLine(False)
        x1 = xTextViewCursor.Position.X
    ll = x1 - x0 # longueur de la place

    # définition de l'arc de cercle (cuvette)
    sz = makeSize(hh*8, hh*8)
    oShape = makeShape(xDocument, "com.sun.star.drawing.EllipseShape")
    oShape.Title= '__l_muette__'
    oShape.LineWidth = hh
    oShape.Size = sz

    # ces lignes sont à placer AVANT le "insertTextContent" pour que la forme soit bien configurée
    oShape.AnchorType = AT_CHARACTER # com.sun.star.text.TextContentAnchorType.AT_CHARACTER
    oShape.HoriOrient = LEFT # com.sun.star.text.HoriOrientation.LEFT
    oShape.LeftMargin = (ll-sz.Width)/2
    oShape.HoriOrientRelation = CHAR # com.sun.star.text.RelOrientation.CHAR
    oShape.VertOrient = CHAR_BOTTOM # com.sun.star.text.VertOrientation.CHAR_BOTTOM
    oShape.VertOrientRelation = CHAR # com.sun.star.text.RelOrientation.CHAR

    # insertion de la forme dans le texte à la position du curseur
    xText.insertTextContent(cursor, oShape, False)
    cursor = deplacerADroite(txt_phon, cursor)

    # cette ligne est à placer APRÈS le "insertTextContent" qui écrase la propriété
    oShape.TextWrap = THROUGHT

    oShape.FillColor = 0x00888888
    oShape.LineStyle = 0

    return cursor

######################################################################################
# Place un point sous une lettre muette
######################################################################################
def marqueImage(xDocument, stylphon, txt_phon, cursor):
    from com.sun.star.text.TextContentAnchorType import AT_CHARACTER
    from com.sun.star.text.WrapTextMode import THROUGHT
    from com.sun.star.text.RelOrientation import CHAR
    from com.sun.star.text.HoriOrientation import LEFT
    from com.sun.star.text.VertOrientation import CHAR_BOTTOM

    # définition de l'arc de cercle (cuvette)
    try:
        fimgname = getLirecouleurTemplateDirURL()+style_phon_perso[stylphon]['CharStyleName']+".png"
    except:
        return deplacerADroite(txt_phon, cursor)
    if os.path.isfile(uno.fileUrlToSystemPath(fimgname)):
        hh = cursor.getPropertyValue("CharHeight")
        
        xViewCursorSupplier = xDocument.getCurrentController()
        xTextViewCursor = xViewCursorSupplier.getViewCursor()
        xTextViewCursor.gotoRange(cursor, False) # remet le curseur physique au début (du mot)
        x0 = xTextViewCursor.Position.X

        # déplace le curseur physique pour calculer la longueur de la cuvette à dessiner
        xTextViewCursor.goRight(len(txt_phon), False)
        x1 = xTextViewCursor.Position.X
        if x1 < x0:
            xTextViewCursor.goLeft(len(txt_phon), False)
            xTextViewCursor.gotoEndOfLine(False)
            x1 = xTextViewCursor.Position.X
        ll = x1 - x0 # longueur de la place

        sz = makeSize(hh*20, hh*20)
        oShape = makeShape(xDocument, "com.sun.star.drawing.GraphicObjectShape")
        oShape.GraphicURL = fimgname
        oShape.Title= '_img_sous_'
        oShape.Size = sz
        oShape.FillTransparence = 100
        oShape.LineTransparence = 100
        ##print (oShape.Title, oShape.GraphicURL)

        # ces lignes sont à placer AVANT le "insertTextContent" pour que la forme soit bien configurée
        oShape.AnchorType = AT_CHARACTER # com.sun.star.text.TextContentAnchorType.AT_CHARACTER
        oShape.HoriOrient = LEFT # com.sun.star.text.HoriOrientation.LEFT
        oShape.LeftMargin = max(0, (ll-sz.Width)/2)
        oShape.HoriOrientRelation = CHAR # com.sun.star.text.RelOrientation.CHAR
        oShape.VertOrient = CHAR_BOTTOM # com.sun.star.text.VertOrientation.CHAR_BOTTOM
        oShape.VertOrientRelation = CHAR # com.sun.star.text.RelOrientation.CHAR

        # insertion de la forme dans le texte à la position du curseur
        cursor.getText().insertTextContent(cursor, oShape, False)
        cursor = deplacerADroite(txt_phon, cursor)

        # cette ligne est à placer APRÈS le "insertTextContent" qui écrase la propriété
        oShape.TextWrap = THROUGHT

        #oShape.FillColor = 0x00888888
        #oShape.LineStyle = 0
    else:
        cursor = deplacerADroite(txt_phon, cursor)

    return cursor

###################################################################################
# Applique un style de caractères donné
###################################################################################
def setStyle(styl, ooocursor):
    for kpv in styl:
        try:
            ooocursor.setPropertyValue(kpv, styl[kpv])
        except:
            pass

###################################################################################
# Insertion d'une chaîne de caractères selon un style donné. Retourne la position
# suivante à laquelle insérer sous la forme d'un curseur
###################################################################################
def deplacerADroite(texte, ooocursor):
    try:
        ooocursor.goRight(len(texte), False)
    except:
        pass

    return ooocursor

###################################################################################
# Insertion d'une chaîne de caractères selon un style donné. Retourne la position
# suivante à laquelle insérer sous la forme d'un curseur
###################################################################################
def formaterTexte(texte, ooocursor, choix_styl):
    lgr_texte = len(texte)

    # coloriage du phonème courant
    ncurs = None
    try:
        ncurs = ooocursor.getText().createTextCursorByRange(ooocursor)
        ncurs.goRight(lgr_texte, True)
    except:
        pass

    if choix_styl == "defaut":
        try:
            ncurs.setPropertyToDefault("CharStyleName")
            ncurs.setPropertyToDefault("ParaLineSpacing")
            ncurs.setPropertyToDefault("CharKerning")
            ncurs.setPropertyToDefault("CharHeight")
            ncurs.setPropertyToDefault("CharBackColor")
            #ncurs.setAllPropertiesToDefault()
        except:
            pass
    elif choix_styl == "noir":
        try:
            ncurs.setPropertyToDefault("CharStyleName")
            ncurs.setPropertyToDefault("CharBackColor")
        except:
            pass
    else:
        setStyle(choix_styl, ncurs)
    del ncurs

    # déplacer le curseur après le phonème courant
    return deplacerADroite(texte, ooocursor)

###################################################################################
# Transcode les phonèmes en couleurs selon le style choisi
###################################################################################
def code_phonemes(xDocument, phonemes, style, cursor, selecteurphonemes=None, decos_phonemes=False):
    stylphon = ''
    nb_phon = len(phonemes)
    i_phon = range(nb_phon)

    cur = cursor
    for i in i_phon:
        phon = phonemes[i]

        if len(phon) > 0:
            stylphon = phon[0]
            txt_phon = phon[1]

            if len(stylphon) == 0:
                cur = deplacerADroite(txt_phon, cur)
            else:
                # voir si le phonème est sélectionné ou non pour affichage
                try:
                    if selecteurphonemes[stylphon] == 0:
                        stylphon = ''
                except:
                    stylphon = ''

                # insertion du texte
                if len(stylphon) == 0:
                    # pas de style : déplacer simplement le curseur
                    cur = deplacerADroite(txt_phon, cur)
                else:
                    if stylphon.startswith('j_') or stylphon.startswith('w_') or stylphon.startswith('y_'):
                        # appliquer le style de la voyelle avec marquage de la semi-voyelle sur la première lettre
                        il = 1
                        if stylphon.startswith('w_') and txt_phon.startswith('ou'):
                            # micmac pour savoir s'il faut souligner une ou 2 lettres
                            il = 2
                        if stylphon.startswith('j_') and txt_phon.startswith('ill'):
                            # micmac pour savoir s'il faut souligner une ou 3 lettres
                            il = 3
                        cur = formaterTexte(txt_phon[:il], cur, style_semi[stylphon[0]][stylphon[2:]])
                        txt_phon = txt_phon[il:]
                        stylphon = stylphon[2:]
                    if stylphon in styles_phonemes[style]:
                        # appliquer le style demandé
                        cur = formaterTexte(txt_phon, cur, styles_phonemes[style][stylphon])
                        if decos_phonemes and xDocument.supportsService("com.sun.star.text.TextDocument"):
                            cur.goLeft(len(txt_phon), False)
                            if stylphon == '#':
                                cur = marquePoint(xDocument, txt_phon, cur)
                            else:
                                cur = marqueImage(xDocument, stylphon, txt_phon, cur)
                    else:
                        # style non défini : appliquer le style par défaut
                        cur = formaterTexte(txt_phon, cur, 'noir')

    return cur

###################################################################################
# Transcode les syllabes selon le style choisi
###################################################################################
def code_syllabes(xDocument, syllabes, isyl, style, cursor, nb_altern=3):
    import math
    from com.sun.star.text.TextContentAnchorType import AT_CHARACTER
    from com.sun.star.text.WrapTextMode import THROUGHT
    from com.sun.star.text.RelOrientation import CHAR
    from com.sun.star.text.HoriOrientation import LEFT
    from com.sun.star.text.VertOrientation import CHAR_BOTTOM
    from com.sun.star.drawing.FillStyle import NONE
    from com.sun.star.drawing.CircleKind import ARC

    sz_syllabes = len(syllabes)
    nisyl = isyl

    if style == 'souligne' and xDocument.supportsService("com.sun.star.text.TextDocument"):
        try:
            """
                Traitement par ajout de formes coupes en arc de cercle pour indiquer les syllabes
            """
            #if sz_syllabes < 2:
                #return deplacerADroite(syllabes[0], cursor), nisyl

            xText = cursor.getText()
            mot = pretraitement_texte(''.join(syllabes).lower())

            xViewCursorSupplier = xDocument.getCurrentController()
            xTextViewCursor = xViewCursorSupplier.getViewCursor()
            xTextViewCursor.gotoRange(cursor, False) # remet le curseur physique au début (du mot)
            x1 = xTextViewCursor.Position.X

            hh = cursor.getPropertyValue("CharHeight")
            for j in range(sz_syllabes):
                # déplace le curseur physique pour calculer la longueur de la cuvette à dessiner
                x0 = x1
                xTextViewCursor.goRight(len(syllabes[j]), False)
                x1 = xTextViewCursor.Position.X
                if x1 < x0:
                    xTextViewCursor.goLeft(len(syllabes[j]), False)
                    xTextViewCursor.gotoEndOfLine(False)
                    x1 = xTextViewCursor.Position.X
                ll = x1 - x0 # longueur de la cuvette

                # définition de l'arc de cercle (cuvette)
                sz = makeSize(ll, min(hh*25, 600))
                oShape = makeShape(xDocument, "com.sun.star.drawing.EllipseShape")
                oShape.Title= '__'+mot+'__'
                #oShape.FillStyle = uno.getConstantByName("com.sun.star.drawing.FillStyle.NONE")
                # Bug https://bugs.freedesktop.org/show_bug.cgi?id=66031
                # uno.getConstantByName no longer works for enum members
                oShape.FillStyle = NONE
                #oShape.CircleKind = uno.getConstantByName("com.sun.star.drawing.CircleKind.ARC")
                # Bug https://bugs.freedesktop.org/show_bug.cgi?id=66031
                # uno.getConstantByName no longer works for enum members
                oShape.CircleKind = ARC
                oShape.CircleStartAngle = -6*math.pi*1000
                oShape.CircleEndAngle = 0
                oShape.LineWidth = hh
                oShape.Size = sz

                # ces lignes sont à placer AVANT le "insertTextContent" pour que la forme soit bien configurée
                oShape.AnchorType = AT_CHARACTER # com.sun.star.text.TextContentAnchorType.AT_CHARACTER
                oShape.HoriOrient = LEFT # com.sun.star.text.HoriOrientation.LEFT
                oShape.HoriOrientPosition = 0
                oShape.HoriOrientRelation = CHAR # com.sun.star.text.RelOrientation.CHAR
                oShape.VertOrient = CHAR_BOTTOM # com.sun.star.text.VertOrientation.CHAR_BOTTOM
                oShape.VertOrientPosition = 0
                oShape.VertOrientRelation = CHAR # com.sun.star.text.RelOrientation.CHAR

                # insertion de la forme dans le texte à la position du curseur
                xText.insertTextContent(cursor, oShape, False)
                cursor = deplacerADroite(syllabes[j], cursor)

                # cette ligne est à placer APRÈS le "insertTextContent" qui écrase la propriété
                oShape.TextWrap = THROUGHT

            return cursor, nisyl
        except:
            pass

    """
        Traitement par coloriage des syllabes (affectation d'un style de caractère)
    """
    for j in range(sz_syllabes):
        cursor = formaterTexte(syllabes[j], cursor, styles_syllabes[style][str(nisyl+1)])
        nisyl += 1
        nisyl = nisyl%nb_altern

    return cursor, nisyl

###################################################################################
# Récupère le textRange correspondant au mot sous le curseur ou à la sélection
###################################################################################
def getXCellTextRange(xDocument, xCursor):
    xTextRanges = []
    if xCursor.supportsService("com.sun.star.text.TextTableCursor"):
        cellRangeName = xCursor.getRangeName()
        #print(cellRangeName)
        startColumn = cellRangeName.split(':')[0][0]
        endColumn = cellRangeName.split(':')[1][0]
        startRow = cellRangeName.split(':')[0][1]
        endRow = cellRangeName.split(':')[1][1]
        oTable = xDocument.getCurrentController().getViewCursor().TextTable #########
        for col in range(ord(startColumn)-64, ord(endColumn)-63):
            for row in range(int(startRow), int(endRow)+1):
                cellName = chr(col+64)+str(row)
                cell = oTable.getCellByName(cellName)
                try:
                    xTextRanges.append(cell.getText().createTextCursorByRange(cell))
                except:
                    pass
    return xTextRanges

def extraitMots(xCursor):
    """
        Extrait les mots d'un curseur de texte
    """
    lWordCursors = []
    xText = xCursor.getText() ## get the XText interface
    xtr_p = xText.createTextCursorByRange(xCursor)

    xtr_p.collapseToStart()
    xtr_p.gotoEndOfWord(True)
    while xtr_p.getText().compareRegionEnds(xtr_p, xCursor) > 0:
        # mot par mot
        if not xtr_p.isCollapsed():
            lWordCursors.append(xText.createTextCursorByRange(xtr_p))
        if not xtr_p.gotoNextWord(False):
            break
        xtr_p.gotoEndOfWord(True)

    # dernier morceau de mot
    if not xtr_p.isCollapsed():
        lWordCursors.append(xText.createTextCursorByRange(xtr_p))
    del xtr_p
    return lWordCursors

def segmenteParagraphe(xCursor):
    """
        Segmente un paragraphe en mots et non mots
    """
    lCursors = []
    xText = xCursor.getText() ## get the XText interface
    xtr_p = xText.createTextCursorByRange(xCursor)

    xtr_p.collapseToStart()
    xtr_p.gotoEndOfWord(True)
    while xtr_p.getText().compareRegionEnds(xtr_p, xCursor) > 0:
        # mot par mot
        if not xtr_p.isCollapsed():
            lCursors.append(xText.createTextCursorByRange(xtr_p))
        xtr_p.collapseToEnd()
        if not xtr_p.gotoNextWord(True):
            break
        if not xtr_p.isCollapsed():
            lCursors.append(xText.createTextCursorByRange(xtr_p))
        xtr_p.collapseToEnd()
        xtr_p.gotoEndOfWord(True)

    # dernier morceau de mot
    if not xtr_p.isCollapsed():
        lCursors.append(xText.createTextCursorByRange(xtr_p))
    del xtr_p
    return lCursors

def getXTextRange(xDocument, fonction='mot', mode=0):
    """
        Récupère le textRange correspondant au mot sous le curseur ou à la sélection
        mode = 0 : récupère le bloc de texte sélectionné
        mode = 1 : récupère le bloc segmenté en paragraphes
        mode = 2 : récupère le bloc segmenté en phrases
        mode = autre : récupère le bloc segmenté en unités de traitement les plus petites possibles
    """

    if not xDocument.supportsService("com.sun.star.text.TextDocument"):
        return []

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    #the writer controller impl supports the css.view.XSelectionSupplier interface
    xSelectionSupplier = xDocument.getCurrentController()
    xIndexAccess = xSelectionSupplier.getSelection()

    if xIndexAccess.supportsService("com.sun.star.text.TextTableCursor"):
        return getXCellTextRange(xDocument, xIndexAccess)

    xTextRanges = []
    xTextRange = None
    try:
        xTextRange = xIndexAccess.getByIndex(0)
    except:
        return None

    theString = xTextRange.getString()
    xText = xTextRange.getText() ## get the XText interface

    if len(theString)==0:
        # pas de texte sélectionné, il faut chercher le mot ou le paragraphe positionné sous le curseur
        try:
            if fonction == 'mot':
                # sélection du mot courant
                xWordCursor = xText.createTextCursorByRange(xTextRange)
                if not xWordCursor.isStartOfWord():
                    xWordCursor.gotoStartOfWord(False)
                xWordCursor.gotoEndOfWord(True)
                xTextRanges.append(xWordCursor)
            elif fonction == 'paragraphe':
                # sélection du paragraphe courant
                xCursor = xText.createTextCursorByRange(xTextRange)
                if not xCursor.isStartOfParagraph():
                    xCursor.gotoStartOfParagraph(False)
                xCursor.gotoEndOfParagraph(True)
                xTextRanges.append(xCursor)
            elif fonction == 'phrase':
                # sélection de la phrase courante
                xCursor = xText.createTextCursorByRange(xTextRange)
                if not xCursor.isStartOfSentence():
                    xCursor.gotoStartOfSentence(False)
                xCursor.gotoEndOfSentence(True)
                xTextRanges.append(xCursor)
            else:
                # sélection de tout le texte
                xCursor = xText.createTextCursorByRange(xDocument.getText())
                xCursor.gotoStart(False)
                xCursor.gotoEnd(True)
                xTextRanges.append(xCursor)
        except:
            pass
        return xTextRanges

    # Premier cas : lecture globale de tout ce qui a été sélectionné
    xtr_p = xText.createTextCursorByRange(xTextRange)
    if mode == 0:
        # récupération du bloc de texte sélectionné
        xTextRanges.append(xtr_p)
        return xTextRanges

    xtr_p.collapseToStart()
    if not xtr_p.isStartOfWord():
        xtr_p.gotoStartOfWord(False)
    xtr_p.gotoEndOfParagraph(True)

    # Deuxième cas : lecture paragraphe par paragraphe
    if mode == 1 or xtr_p.getText().compareRegionEnds(xtr_p, xTextRange) > 0:
        while xtr_p.getText().compareRegionEnds(xtr_p, xTextRange) > 0:
            # paragraphe par paragraphe
            if not xtr_p.isCollapsed():
                xTextRanges.append(xText.createTextCursorByRange(xtr_p))
            if not xtr_p.gotoNextParagraph(False):
                break
            xtr_p.gotoEndOfParagraph(True)

        # dernier morceau de paragraphe
        xtr_p.gotoRange(xTextRange, False)
        xtr_p.collapseToEnd()
        if not xtr_p.isEndOfWord():
            xtr_p.gotoEndOfWord(False)
        xtr_p.gotoStartOfParagraph(True)
        if xtr_p.getText().compareRegionStarts(xtr_p, xTextRange) > 0:
            xTextRanges.append(xText.createTextCursorByRange(xTextRange))
        else:
            if not xtr_p.isCollapsed():
                xTextRanges.append(xText.createTextCursorByRange(xtr_p))
        del xtr_p
        return xTextRanges

    # Troisième cas : lecture phrase par phrase
    xtr_p.collapseToStart()
    xtr_p.gotoEndOfSentence(True)
    if mode == 2 or xtr_p.getText().compareRegionEnds(xtr_p, xTextRange) > 0:
        # fin de phrase avant fin de sélection : on procède phrase par phrase
        while xtr_p.getText().compareRegionEnds(xtr_p, xTextRange) > 0:
            # phrase par phrase
            if not xtr_p.isCollapsed():
                xTextRanges.append(xText.createTextCursorByRange(xtr_p))
            if not xtr_p.gotoNextSentence(False):
                break
            xtr_p.gotoEndOfSentence(True)
        
        # dernier morceau de phrase
        xtr_p.gotoRange(xTextRange, False)
        xtr_p.collapseToEnd()
        if not xtr_p.isEndOfWord():
            xtr_p.gotoEndOfWord(False)
        xtr_p.collapseToEnd()
        xtr_p.gotoStartOfSentence(True)
        if not xtr_p.isCollapsed():
            xTextRanges.append(xText.createTextCursorByRange(xtr_p))
        del xtr_p
        return xTextRanges

    # Quatrième cas : lecture mot par mot
    xtr_p.collapseToStart()
    xtr_p.gotoEndOfWord(True)
    while xtr_p.getText().compareRegionEnds(xtr_p, xTextRange) > 0:
        # mot par mot
        if not xtr_p.isCollapsed():
            xTextRanges.append(xText.createTextCursorByRange(xtr_p))
        if not xtr_p.gotoNextWord(False):
            break
        xtr_p.gotoEndOfWord(True)

    # dernier morceau de mot
    if not xtr_p.isCollapsed():
        xTextRanges.append(xText.createTextCursorByRange(xtr_p))
    del xtr_p

    return xTextRanges

#########################################################################################################
#########################################################################################################
###                                       FONCTIONS D'INTERFACE
#########################################################################################################
#########################################################################################################

###################################################################################
# Remet un paragraphe dans son style d'origine en espaçant les mots
###################################################################################
def colorier_defaut(paragraphe, cursor, choix):
    # placer le curseur au début de la zone de traitement
    cursor.collapseToStart()
    cursor2 = cursor.getText().createTextCursorByRange(cursor)

    # suppressions et remplacements de caractères perturbateurs
    paragraphe = nettoyeur_caracteres(paragraphe)

    # code le coloriage du paragraphe
    curs = formaterTexte(paragraphe, cursor, choix)

    # supprimer les espaces dupliqués
    if (choix == 'defaut'):
        # replacer le curseur au début de la zone de traitement
        curs = cursor2

        i = 0
        while i < len(paragraphe):
            j = i
            if (paragraphe[i] == ' '):
                k = 0
                while (i < len(paragraphe)) and (paragraphe[i] == ' '):
                    i += 1
                    k += 1
                curs = deplacerADroite(paragraphe[j:j+1], curs)
                if k > 1:
                    # il y a plusieurs espaces à remplacer par un seul
                    ncurs = curs.getText().createTextCursorByRange(curs)
                    ncurs.goRight(k-1, True)
                    ncurs.setString("")
                    del ncurs
            else:
                while (i < len(paragraphe)) and (paragraphe[i] != ' '):
                    i += 1
                curs = deplacerADroite(paragraphe[j:i], curs)
    del cursor2

###################################################################################
# Conversion d'un paragraphe en mettant ses phonèmes en couleur
###################################################################################
def colorier_phonemes_style(xDocument, paragraphe, cursor, style, nb_altern=2, point_sm=False):
    # chargement du dictionnaire de décodage
    loadLCDict(getLirecouleurDictionary())

    # lecture des informations de configuration
    settings = Settings()

    # savoir si on détecte les phonèmes standard ou pour des débutants lecteurs
    detection_phonemes_debutant = settings.get('__detection_phonemes__')

    # récup du masque des phonèmes à afficher
    selecteurphonemes = settings.get('__selection_phonemes__')

    lMots = extraitMots(cursor)
    for curMot in lMots:
        # suppressions et remplacements de caractères perturbateurs
        paragraphe = nettoyeur_caracteres(curMot.getString())

        # traite le paragraphe en phonèmes
        pp = generer_paragraphe_phonemes(paragraphe, detection_phonemes_debutant)

        # code le coloriage du paragraphe
        curs = curMot
        curs.collapseToStart()
        if style == 'alterne':
            for umot in pp:
                if isinstance(umot, list):
                    # recodage du mot en couleurs
                    iphon = 0
                    for i in range(len(umot)):
                        phon = umot[i]
                        if len(phon) > 0:
                            curs = formaterTexte(phon[1], curs, style_phon_altern[str(iphon+1)])
                            iphon = (iphon + 1)%nb_altern
                else:
                    # passage de la portion de texte non traitée (ponctuation, espaces...)
                    curs = deplacerADroite(umot, curs)
        else:
            for umot in pp:
                if isinstance(umot, list):
                    # recodage du mot en couleurs
                    curs = code_phonemes(xDocument, umot, style, curs, selecteurphonemes, point_sm)
                else:
                    # passage de la portion de texte non traitée (ponctuation, espaces...)
                    curs = deplacerADroite(umot, curs)

        # ménage
        del pp
    del lMots

###################################################################################
# Conversion d'un paragraphe en mettant les lettres muettes en évidence
###################################################################################
def colorier_lettres_muettes(xDocument, paragraphe, cursor, style):
    # chargement du dictionnaire de décodage
    loadLCDict(getLirecouleurDictionary())

    # récupération de l'information sur le marquage des lettres muettes par des points
    settings = Settings()
    point_lmuette = settings.get('__point__')
    e_caduc = settings.get('__syllo__')[1] #indique si les e caducs doivent être marqués comme des lettres muettes

    # récup du masque des phonèmes à afficher : uniquement les lettres muettes
    selecteurphonemes = {'#':1, 'verb_3p':1}
    if e_caduc:
        selecteurphonemes['q_caduc'] = 1

    lMots = extraitMots(cursor)
    for curMot in lMots:
        # suppressions et remplacements de caractères perturbateurs
        paragraphe = nettoyeur_caracteres(curMot.getString())

        # traite le paragraphe en phonèmes
        pp = generer_paragraphe_phonemes(paragraphe)

        # code le coloriage du paragraphe
        curs = curMot
        curs.collapseToStart()
        for umot in pp:
            if isinstance(umot, list):
                # recodage du mot en couleurs
                curs = code_phonemes(xDocument, umot, style, curs, selecteurphonemes, point_lmuette)
            else:
                # passage de la portion de texte non traitée (ponctuation, espaces...)
                curs = deplacerADroite(umot, curs)

        # ménage
        del pp
    del lMots

###################################################################################
# Marque les liaisons dans un paragraphe
###################################################################################
def colorier_liaisons(__texte, cursor, style, forcer=False):
    # segmente le texte en portions mots / non mots
    pp = segmenteParagraphe(cursor)
    
    # code le coloriage du paragraphe
    l_pp = len(pp)
    if l_pp < 2:
        return

    xText = pp[0].getText()
    mot_prec = u(pp[0].getString())
    mot_prec = re.sub(u('[\'´’]'), '@', mot_prec.lower())
    umot = u(pp[1].getString())
    umot = re.sub(u('[\'´’]'), '@', umot.lower())
    mot_suiv = ""
    for i_mot in range(1,l_pp-1):
        mot_suiv = u(pp[i_mot+1].getString())
        mot_suiv = re.sub(u('[\'´’]'), '@', mot_suiv.lower())
        format_liaison = False

        if len(umot.strip()) == 0:
            if forcer or teste_liaison(mot_prec, mot_suiv):
                # formatage de la liaison
                curs = pp[i_mot]
                curs.collapseToStart()
                curs = formaterTexte(umot, curs, styles_phonemes[style]['liaison'])
                format_liaison = True
                
                # formater la dernière lettre du mot précédent comme lettre non muette
                cur_p = xText.createTextCursorByRange(pp[i_mot-1])
                cur_p.collapseToEnd()
                cur_p.goLeft(1, True)
                if cur_p.getPropertyValue("CharStyleName") == "phon_muet":
                    try:
                        cur_p.setPropertyToDefault("CharStyleName")
                    except:
                        pass
                del cur_p

        if not format_liaison:
            # mot : déplacement à droite
            curs = xText.createTextCursorByRange(pp[i_mot])
            curs = deplacerADroite(umot, curs)
            del curs

        mot_prec = umot
        umot = mot_suiv
    del pp

###################################################################################
# Conversion d'un paragraphe en mettant ses syllabes en évidence
###################################################################################
def colorier_syllabes_style(xDocument, paragraphe, cursor, style, nb_altern):
    # chargement du dictionnaire de décodage
    loadLCDict(getLirecouleurDictionary())

    # récupération de l'information sur le choix entre syllabes orales ou syllabes écrites
    settings = Settings()
    choix_syllo = settings.get('__syllo__')

    # savoir si on détecte les phonèmes standard ou pour des débutants lecteurs
    detection_phonemes_debutant = settings.get('__detection_phonemes__')

    # placer le curseur au début de la zone de traitement
    cursor.collapseToStart()

    # suppressions et remplacements de caractères perturbateurs
    paragraphe = nettoyeur_caracteres(paragraphe)

    # traite le paragraphe en phonèmes
    pp = generer_paragraphe_phonemes(paragraphe, detection_phonemes_debutant)

    # recompose les syllabes
    ps = generer_paragraphe_syllabes(pp, choix_syllo)

    # code le coloriage du paragraphe
    curs = cursor
    isyl = 0
    for i in range(len(ps)):
        try:
            if isinstance(ps[i], list):
                # recodage du mot en couleurs
                curs, isyl = code_syllabes(xDocument, ps[i], isyl, style, curs, nb_altern)
            else:
                # passage de la portion de texte non traitée (ponctuation, espaces...)
                curs = deplacerADroite(ps[i], curs)
        except:
            # passage de la portion de texte non traitée (ponctuation, espaces...)
            curs = deplacerADroite(ps[i], curs)

    # ménage
    del ps
    del pp

###################################################################################
# Colorie les lettres sélectionnées pour éviter les confusions
###################################################################################
def colorier_confusion_lettres(paragraphe, cursor, style):
    # placer le curseur au début de la zone de traitement
    cursor.collapseToStart()

    # suppression des \r qui engendrent des décalages de codage sous W*
    paragraphe = paragraphe.replace('\r', '')

    # lecture du nombre d'espaces pour remplacer un espace standard
    settings = Settings()
    sel_lettres = settings.get('__selection_lettres__')

    # code le coloriage des lettres
    ensemble_confus = [k for k in sel_lettres.keys() if sel_lettres[k]]
    phons_lettres = dict([[lettre,generer_paragraphe_phonemes(lettre)[0][0][0]] for lettre in ensemble_confus])
    curs = cursor
    i = 0
    while i < len(paragraphe):
        j = i
        if paragraphe[i] in ensemble_confus:
            while (i < len(paragraphe)) and (paragraphe[i] == paragraphe[j]):
                i += 1
            curs = formaterTexte(paragraphe[j:i], curs, styles_phonemes[style][phons_lettres[paragraphe[j]]])
        else:
            while (i < len(paragraphe)) and not(paragraphe[i] in ensemble_confus):
                i += 1
            curs = deplacerADroite(paragraphe[j:i], curs)

###################################################################################
# Colorie les consonnes et les voyelles
###################################################################################
def colorier_consonnes_voyelles(paragraphe, cursor, style):
    # placer le curseur au début de la zone de traitement
    cursor.collapseToStart()

    # suppression des \r qui engendrent des décalages de codage sous W*
    paragraphe = paragraphe.replace('\r', '')

    # code le coloriage du paragraphe
    e_consonnes = []
    for lettre in ['b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','z']:
        e_consonnes.append(lettre)
        e_consonnes.append(lettre.upper())
    e_voyelles = []
    for lettre in ['a','e','i','o','u','y',u('é'),u('è'),u('ë'),u('ê'),u('à'),u('â'),u('ä'),u('î'),u('î'),u('ù'),u('û'),u('ö'),u('ô')]:
        e_voyelles.append(lettre)
        e_voyelles.append(lettre.upper())

    curs = cursor
    i = 0
    while i < len(paragraphe):
        j = i
        if paragraphe[i] in e_consonnes:
            while (i < len(paragraphe)) and (paragraphe[i] in e_consonnes):
                i += 1
            curs = formaterTexte(paragraphe[j:i], curs, styles_phonemes[style]['consonne'])
        elif paragraphe[i] in e_voyelles:
            while (i < len(paragraphe)) and (paragraphe[i] in e_voyelles):
                i += 1
            curs = formaterTexte(paragraphe[j:i], curs, styles_phonemes[style]['voyelle'])
        else:
            while (i < len(paragraphe)) and not(paragraphe[i] in e_consonnes) and not(paragraphe[i] in e_voyelles):
                i += 1
            curs = deplacerADroite(paragraphe[j:i], curs)

###################################################################################
# Suppression des arcs de marquage des syllabes pur le paragraphe sélectionné
###################################################################################
def supprimer_arcs_syllabes(xDocument, texte, __cursor):
    if xDocument.supportsService("com.sun.star.drawing.DrawingDocument"):
        oDrawDocCtrl = xDocument.getCurrentController()
        oDrawPage = oDrawDocCtrl.getCurrentPage()
    else:
        oDrawPage = xDocument.DrawPage

    ultexte = pretraitement_texte(texte)
    mots = ['__'+x+'__' for x in ultexte.split()] # extraire des étiquettes des mots"

    shapesup=[]
    nNumShapes = oDrawPage.getCount()
    for x in range (nNumShapes): # toutes les formes de la page
        oShape = oDrawPage.getByIndex(x)
        if oShape.Title in mots:
            shapesup.append(oShape)

    for oShape in shapesup:
        oDrawPage.remove(oShape)
    del shapesup

###################################################################################
# Suppression des décorations sous les sons pour la page en cours
###################################################################################
def supprimer_deco_sons(xDocument):
    oDrawPage = xDocument.DrawPage

    shapesup=[]
    nNumShapes = oDrawPage.getCount()
    for x in range (nNumShapes): # toutes les formes de la page
        oShape = oDrawPage.getByIndex(x)
        if oShape.Title == '__l_muette__' or oShape.Title == '_img_sous_':
            shapesup.append(oShape)

    for oShape in shapesup:
        oDrawPage.remove(oShape)
    del shapesup

#########################################################################################################
#########################################################################################################
#
#    À partir de là, le code ne fait que déclarer les points d'entrées dans l'extension.
#    Pour chaque type de traitement, on a successivement :
#        - une classe, nécessaire comme point d'entrée dans l'extension
#        - une fonction, nécessaire comme point d'entrée sous forme de macro simple
#        - la fonction qui extrait le texte et lance le traitement
#
#                                    @@@@@@@@@@@@@@@@@@@@@@
#
#########################################################################################################
#########################################################################################################

###################################################################################
# Élimine tout style de caractère
###################################################################################
def __lirecouleur_defaut__(xDocument, choix='defaut'):
    """Applique le style par défaut à la sélection"""
    try:
        xTextRange = getXTextRange(xDocument, fonction='paragraphe', mode=0)
        if xTextRange == None:
            return False
        for xtr in xTextRange:
            theString = xtr.getString()

            colorier_defaut(theString, xtr, choix)
        del xTextRange
    except:
        return False
    return True

###################################################################################
# Recode le texte sélectionné en noir
###################################################################################
def __lirecouleur_noir__(xDocument):
    """Recode le texte sélectionné en noir"""
    __lirecouleur_suppr_decos__(xDocument)
    __lirecouleur_defaut__(xDocument, 'noir')

###################################################################################
# Espace les mots de la sélection en dupliquant les espaces
###################################################################################
def __lirecouleur_espace__(xDocument):
    """Espace les mots de la sélection"""
    try:
        xTextRange = getXTextRange(xDocument, fonction='paragraphe', mode=0)
        if xTextRange == None:
            return False

        # lecture du nombre d'espaces pour remplacer un espace standard
        settings = Settings()
        nb_sub_espaces = settings.get('__subspaces__')
        sub_espaces = ''.join([' ' for i in range(nb_sub_espaces)])

        for xtr in xTextRange:
            paragraphe = xtr.getString()

            # placer le curseur au début de la zone de traitement
            xtr.collapseToStart()
            curs = xtr

            # suppressions et remplacements de caractères perturbateurs
            paragraphe = nettoyeur_caracteres(paragraphe)

            # code la duplication des espaces
            i = 0
            while i < len(paragraphe):
                j = i
                if (paragraphe[i] == ' '):
                    k = 0
                    while (i < len(paragraphe)) and (paragraphe[i] == ' '):
                        i += 1
                        k += 1

                    if k != nb_sub_espaces:
                        # il y n'y a pas le bon nombre d'espaces
                        ncurs = curs.getText().createTextCursorByRange(curs)
                        ncurs.goRight(k, True)
                        ncurs.setString(sub_espaces)
                        ncurs.collapseToEnd()
                        del curs
                        curs = ncurs
                    else:
                        curs.goRight(k, False)
                else:
                    while (i < len(paragraphe)) and (paragraphe[i] != ' '):
                        i += 1
                    curs = deplacerADroite(paragraphe[j:i], curs)
        del xTextRange
    except:
        return False
    return True

###################################################################################
# Espace les mots de la sélection en dupliquant les espaces
###################################################################################
def __lirecouleur_separe_mots__(xDocument):
    """Sépare les mots de la sélection en coloriant les espaces"""
    xTextRange = getXTextRange(xDocument, fonction='phrase', mode=0)
    if xTextRange == None:
        return False

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)
    stylEspace = styles_phonemes['perso']['espace']

    for xTextR in xTextRange:
        xText = xTextR.getText()
        xWordCursor = xText.createTextCursorByRange(xTextR)
        xWordCursor.collapseToStart()
                    
        # placement au début du dernier mot du paragraphe
        xTextR.collapseToEnd()
        xTextR.gotoPreviousWord(False)
        xTextR.gotoStartOfWord(False)
        xTextR.collapseToStart()

        i = 0
        while xText.compareRegionStarts(xWordCursor, xTextR) > 0 and i < 10000:
            # mot par mot
            xWordCursor.gotoEndOfWord(True)
            xWordCursor.collapseToEnd()
            
            if not xWordCursor.gotoNextWord(True):
                return True
            if xWordCursor.isEndOfParagraph():
                xWordCursor.gotoNextParagraph(False)
            if not xWordCursor.gotoStartOfWord(True):
                return True

            setStyle(stylEspace, xWordCursor)
            xWordCursor.collapseToEnd()
            i += 1

    return True

###################################################################################
# Espace les mots de la sélection en dupliquant les espaces
###################################################################################
def __lirecouleur_couleur_mots__(xDocument):
    """Sépare les mots de la sélection en coloriant les espaces"""
    xTextRange = getXTextRange(xDocument, fonction='paragraphe', mode=0)
    if xTextRange == None:
        return False

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    # récup de la période d'alternance des couleurs
    settings = Settings()
    nb_altern = settings.get('__alternate__')

    imot = 0
    for xTextR in xTextRange:
        xText = xTextR.getText()
        xWordCursor = xText.createTextCursorByRange(xTextR)
        xWordCursor.collapseToStart()
        xWordCursor.gotoStartOfWord(False)
        
        # placement à la fin du dernier mot du paragraphe
        xTextR.collapseToEnd()
        xTextR.gotoPreviousWord(False)
        xTextR.gotoStartOfWord(False)
        xTextR.gotoEndOfWord(True)
        
        i = 0
        while xText.compareRegionEnds(xWordCursor, xTextR) >= 0 and i < 10000:
            xWordCursor.collapseToStart()
            xWordCursor.gotoStartOfWord(False)
            xWordCursor.gotoEndOfWord(True)
            setStyle(styles_mots['dys'][str(imot+1)], xWordCursor)
            imot = (imot + 1) % nb_altern 
            
            # mot suivant
            xWordCursor.collapseToEnd()
            if not xWordCursor.gotoNextWord(False):
                return True
            if xWordCursor.isEndOfParagraph():
                xWordCursor.gotoNextParagraph(False)
            i += 1

    return True

###################################################################################
# Espace les lignes de la sélection
###################################################################################
def __lirecouleur_espace_lignes__(xDocument):
    try:
        xTextRange = getXTextRange(xDocument, fonction='paragraphe', mode=0)
        if xTextRange == None:
            return False
        
        for xtr in xTextRange:
            args = xtr.getPropertyValue('ParaLineSpacing')
            args.Height += 10
            xtr.setPropertyValue('ParaLineSpacing', args)
        del xTextRange
    except:
        return False
    return True

###################################################################################
# Espace les lignes et les mots de la sélection
###################################################################################
def __lirecouleur_large__(xDocument):
    # espacement des mots
    __lirecouleur_espace__(xDocument)

    try:
        xTextRange = getXTextRange(xDocument, fonction='paragraphe', mode=0)
        if xTextRange == None:
            return False
        
        for xtr in xTextRange:
            # double interligne
            args = xtr.getPropertyValue('ParaLineSpacing')
            args.Height = 200
            xtr.setPropertyValue('ParaLineSpacing', args)

            # espacement des caractères normal
            xtr.setPropertyValue('CharKerning', 100)

            # taille de caractères : 16 points minimum
            args = xtr.getPropertyValue('CharHeight')
            if (args < 16.0):
                xtr.setPropertyValue('CharHeight', 16.0)
        del xTextRange
    except:
        return False
    return True

###################################################################################
# Espace les lignes de la sélection ainsi que les caractères
###################################################################################
def __lirecouleur_extra_large__(xDocument):
    # espacement des mots
    __lirecouleur_large__(xDocument)

    try:
        xTextRange = getXTextRange(xDocument, fonction='paragraphe', mode=0)
        if xTextRange == None:
            return False
        
        for xtr in xTextRange:
            # espacement des caractères
            args = xtr.getPropertyValue('CharKerning')
            if (args < 200):
                xtr.setPropertyValue('CharKerning', 200)

        del xTextRange
    except:
        return False
    return True

###################################################################################
# Marque les phonèmes sous forme de couleurs en fonction des styles du document
###################################################################################
def __lirecouleur_phonemes__(xDocument):
    """Colorie les phonèmes en couleurs arc en ciel"""
    xTextRange = getXTextRange(xDocument, fonction='mot', mode=3)
    if xTextRange == None:
        return False

    # récup de l'option de superposition de fonction
    settings = Settings()
    superpose = settings.get('__superpose__')
    point_sm = settings.get('__point__')

    try:
        for xtr in xTextRange:
            theString = xtr.getString()
            if not superpose:
                xtrTemp = xDocument.getText().createTextCursorByRange(xtr)
                colorier_defaut(theString, xtrTemp, 'noir')
                del xtrTemp
            colorier_phonemes_style(xDocument, theString, xtr, 'perso', 2, point_sm)
        del xTextRange
    except:
        return False
    return True

###################################################################################
# Colorie les phonèmes avec une alternance de typographie
###################################################################################
def __lirecouleur_alterne_phonemes__(xDocument):
    """Colorie les phonèmes avec une alternance de typographie"""
    xTextRange = getXTextRange(xDocument, fonction='mot', mode=3)
    if xTextRange == None:
        return False

    # récup de la période d'alternance des styles et de l'option de superposition de fonction
    settings = Settings()
    nb_altern = settings.get('__alternate__')
    superpose = settings.get('__superpose__')

    try:
        for xtr in xTextRange:
            theString = xtr.getString()
            if not superpose:
                xtrTemp = xDocument.getText().createTextCursorByRange(xtr)
                colorier_defaut(theString, xtrTemp, 'noir')
                del xtrTemp
            colorier_phonemes_style(xDocument, theString, xtr, 'alterne', nb_altern)
        del xTextRange
    except:
        return False
    return __lirecouleur_l_muettes__(xDocument)

###################################################################################
# Marque les graphèmes complexes en fonction des styles du document
###################################################################################
def __lirecouleur_graphemes_complexes__(xDocument):
    """Colorie les graphèmes complexes"""
    xTextRange = getXTextRange(xDocument, fonction='mot', mode=3)
    if xTextRange == None:
        return False

    # récup de l'option de superposition de fonction
    settings = Settings()
    superpose = settings.get('__superpose__')

    try:
        for xtr in xTextRange:
            theString = xtr.getString()
            if not superpose:
                xtrTemp = xDocument.getText().createTextCursorByRange(xtr)
                colorier_defaut(theString, xtrTemp, 'noir')
                del xtrTemp
            colorier_phonemes_style(xDocument, theString, xtr, 'complexes')
        del xTextRange
    except:
        return False
    return True

###################################################################################
# Marque les syllabes en alternant les couleurs
###################################################################################
def __lirecouleur_syllabes__(xDocument, style = 'souligne'):
    """Mise en évidence des syllabes soulignées"""
    try:
        xTextRange = getXTextRange(xDocument, fonction='mot', mode=1)
        if xTextRange == None:
            return False

        # Importer les styles de coloriage de texte
        importStylesLireCouleur(xDocument)

        # récup de la période d'alternance des couleurs et de l'option de superposition de fonction
        settings = Settings()
        nb_altern = settings.get('__alternate__')
        superpose = settings.get('__superpose__')

        for xtr in xTextRange:
            theString = xtr.getString()
            if not superpose:
                xtrTemp = xDocument.getText().createTextCursorByRange(xtr)
                colorier_defaut(theString, xtrTemp, 'noir')
                del xtrTemp
            colorier_syllabes_style(xDocument, theString, xtr, style, nb_altern)
        del xTextRange
    except:
        return False
    return __lirecouleur_l_muettes__(xDocument)

###################################################################################
# Supprime les arcs sous les syllabes dans le texte sélectionné.
###################################################################################
def __lirecouleur_suppr_syllabes__(xDocument):
    try:
        xTextRange = getXTextRange(xDocument, fonction='mot', mode=3)
        if xTextRange == None:
            return False
        for xtr in xTextRange:
            theString = xtr.getString()
            supprimer_arcs_syllabes(xDocument, theString, xtr)
        del xTextRange
    except:
        return False
    return True

###################################################################################
# Ne marque que les lettres muettes dans le texte sélectionné.
###################################################################################
def __lirecouleur_l_muettes__(xDocument):
    """Met uniquement en évidence les lettres muettes"""
    try:
        xTextRange = getXTextRange(xDocument, fonction='mot', mode=1)
        if xTextRange == None:
            return False

        for xtr in xTextRange:
            theString = xtr.getString()
            colorier_lettres_muettes(xDocument, theString, xtr, 'perso')

        del xTextRange
    except:
        return False
    return True

###################################################################################
# Formatte toute la sélection comme phonème muet
###################################################################################
def __lirecouleur_phon_muet__(xDocument):
    """Met uniquement en évidence les lettres muettes"""
    try:
        # Importer les styles de coloriage de texte
        importStylesLireCouleur(xDocument)

        #the writer controller impl supports the css.view.XSelectionSupplier interface
        xSelectionSupplier = xDocument.getCurrentController()
        xIndexAccess = xSelectionSupplier.getSelection()
        xTextRange = xIndexAccess.getByIndex(0)
    
        if xTextRange == None or len(xTextRange.getString()) == 0:
            return False

        # récupération de l'information sur le marquage des lettres muettes par des points
        settings = Settings()
        point_lmuette = settings.get('__point__')

        xtr = xTextRange.getText().createTextCursorByRange(xTextRange)
        theString = xtr.getString()
        xtr.collapseToStart()
        xtr = formaterTexte(theString, xtr, styles_phonemes['perso']['#'])
        if point_lmuette and xDocument.supportsService("com.sun.star.text.TextDocument"):
            xtr.goLeft(len(theString), False)
            xtr = marquePoint(xDocument, theString, xtr)

        del xtr
    except:
        return False
    return True

###################################################################################
# Supprime d'éventuelles décorations sous certains sons
###################################################################################
def __lirecouleur_suppr_decos__(xDocument):
    try:
        supprimer_deco_sons(xDocument)
    except:
        return False
    return True

###################################################################################
# Marque la ponctuation d'un texte
###################################################################################
def __lirecouleur_ponctuation__(xDocument):
    # caractères de ponctuation recherchés
    ponctuation = u('.!?…,;:«»—()[]')

    #the writer controller impl supports the css.view.XSelectionSupplier interface
    xSelectionSupplier = xDocument.getCurrentController()
    xIndexAccess = xSelectionSupplier.getSelection()
    xTextRange = xIndexAccess.getByIndex(0)
    if xTextRange is None or len(xTextRange.getString()) == 0:
        xTextRange = getXTextRange(xDocument, fonction='texte', mode=0)[0]

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    # placer le curseur au début de la zone de traitement
    curs = xTextRange.getText().createTextCursorByRange(xTextRange)
    curs.collapseToStart()

    # suppressions et remplacements de caractères perturbateurs
    utexte = u(xTextRange.getString()) # codage unicode
    paragraphe = nettoyeur_caracteres(utexte)
    l_para = len(paragraphe)

    # code le coloriage du paragraphe
    i = 0
    while i < l_para:
        j = i
        # parcours jusqu'à la prochaine marque de ponctuation
        while i < l_para and ponctuation.find(paragraphe[i]) < 0:
            i += 1
        curs = deplacerADroite(paragraphe[j:i], curs)

        if i < l_para and paragraphe[i] in ponctuation:
            j = i
            while i < l_para and ponctuation.find(paragraphe[i]) >= 0:
                i += 1
            curs = formaterTexte(paragraphe[j:i], curs, style_phon_perso['ponctuation'])
    del curs
    del xTextRange

###################################################################################
# Marque les liaisons dans le texte sélectionné.
###################################################################################
def __lirecouleur_liaisons__(xDocument, forcer=False):
    """Mise en évidence des liaisons"""
    
    # Commencer par espacer les mots du texte
    __lirecouleur_espace__(xDocument)
    
    # Mettre les liaisons en évidence
    xTextRange = getXTextRange(xDocument, fonction='paragraphe', mode=1)
    if xTextRange == None:
        return False
    for xtr in xTextRange:
        try:
            theString = xtr.getString()
            colorier_liaisons(theString, xtr, 'perso', forcer)
        except:
            pass
    del xTextRange
    return True

###################################################################################
# Colorie les lettres sélectionnées pour éviter des confusions.
###################################################################################
def __lirecouleur_confusion_lettres__(xDocument):
    """Colorie les lettres sélectionnées pour éviter les confusions"""
    try:
        xTextRange = getXTextRange(xDocument, fonction='paragraphe', mode=1)
        if xTextRange == None:
            return False
        for xtr in xTextRange:
            theString = xtr.getString()

            colorier_confusion_lettres(theString, xtr, 'perso')
        del xTextRange
    except:
        return False
    return True

###################################################################################
# Colorie les consonnes et les voyelles.
###################################################################################
def __lirecouleur_consonne_voyelle__(xDocument):
    """Colorie les consonnes et les voyelles"""
    try:
        xTextRange = getXTextRange(xDocument, fonction='paragraphe', mode=1)
        if xTextRange == None:
            return False
        for xtr in xTextRange:
            theString = xtr.getString()

            colorier_consonnes_voyelles(theString, xtr, 'complexes')
        del xTextRange
    except:
        return False
    return True

###################################################################################
# Colorie les lignes avec une alternance de couleurs.
###################################################################################
def __lirecouleur_lignes__(xDocument):
    #the writer controller impl supports the css.view.XSelectionSupplier interface
    xSelectionSupplier = xDocument.getCurrentController()
    xIndexAccess = xSelectionSupplier.getSelection()
    xTextRange = xIndexAccess.getByIndex(0)
    if xTextRange is None or len(xTextRange.getString()) == 0:
        xTextRange = getXTextRange(xDocument, fonction='texte', mode=0)[0]

    # Importer les styles de coloriage de texte
    importStylesLireCouleur(xDocument)

    # récup de la période d'alternance des couleurs
    settings = Settings()
    nb_altern = settings.get('__alternate__')

    xText = xTextRange.getText()
    xCursPara = xText.createTextCursorByRange(xTextRange)
    
    xCursLi = xSelectionSupplier.getViewCursor()
    xCursLi.gotoRange(xTextRange, False)
    xCursLi.collapseToStart()
    xCursLi.gotoStartOfLine(False)
    stylignes = [dict([['CharStyleName',styles_lignes+str(i+1)]]) for i in range(nb_altern)]
    nligne = 0

    while xText.compareRegionEnds(xCursLi, xTextRange) >= 0:
        # paragraphe par paragraphe
        xCursPara.gotoEndOfParagraph(False)
        while xText.compareRegionEnds(xCursLi, xCursPara) >= 0:
            # ligne par ligne
            xCursLi.gotoStartOfLine(False)
            xCursLi.gotoEndOfLine(True)
            setStyle(stylignes[nligne], xCursLi)
            ll = u(xCursLi.getString())

            # fait pour éviter de changer de couleur de ligne lorsqu'une ligne est vide
            if len(ll.encode('UTF-8')) > 0:
                nligne = (nligne + 1) % nb_altern

            # retour au début de ligne et passage à la ligne suivante
            xCursLi.collapseToStart()
            if not xCursLi.goDown(1, False):
                del xCursPara
                return True
            
        if not xCursPara.gotoNextParagraph(False):
            del xCursPara
            return True

    return True

"""
    Création d'un nouveau document LireCouleur
"""
def __new_lirecouleur_document__(__xDocument, ctx):
    url = getLirecouleurTemplateURL()
    try:
        desktop = create_uno_service('com.sun.star.frame.Desktop', ctx)
        if url.endswith('.odt'):
            ppp = create_uno_struct("com.sun.star.beans.PropertyValue")
            ppp.Name = "AsTemplate" # le fichier va servir de modèle
            ppp.Value = True
            desktop.loadComponentFromURL(url, "_blank", 0, (ppp,))
        else:
            desktop.loadComponentFromURL(url, "_blank", 0, ())
        return
    except:
        pass

    try:
        desktop.loadComponentFromURL('private:factory/swriter', "_blank", 0, ())
    except:
        pass

"""
    Recharger les styles de caractères depuis le modèle LireCouleur
"""
def __lirecouleur_recharger_styles__(xDocument):
    try:
        """
            Importation des styles à partir d'un fichier odt
        """
        ''' chemin d'accès au fichier qui contient les styles à utiliser '''
        url = getLirecouleurTemplateURL()
        ppp1 = create_uno_struct("com.sun.star.beans.PropertyValue")
        ppp1.Name = "LoadPageStyles"
        ppp1.Value = False
        ppp2 = create_uno_struct("com.sun.star.beans.PropertyValue")
        ppp2.Name = "LoadFrameStyles"
        ppp2.Value = False
        ppp3 = create_uno_struct("com.sun.star.beans.PropertyValue")
        ppp3.Name = "LoadNumberingStyles"
        ppp3.Value = False
        ppp4 = create_uno_struct("com.sun.star.beans.PropertyValue")
        ppp4.Name = "LoadTextStyles" # on veut uniquement les styles de texte
        ppp4.Value = True
        ppp5 = create_uno_struct("com.sun.star.beans.PropertyValue")
        ppp5.Name = "OverwriteStyles" # on veut écraser les styles existants
        ppp5.Value = True
        xDocument.getStyleFamilies().loadStylesFromURL(url, (ppp1, ppp2, ppp3, ppp4, ppp5,))
    except:
        pass



