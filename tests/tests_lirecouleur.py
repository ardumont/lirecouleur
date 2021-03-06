#!/usr/bin/env python
# -*- coding: utf-8 -*-

###################################################################################
# Jeu de tests unitaires de LireCouleur. Les tests portent sur la génération de
# phonèmes et de syllabes. Chaque jeu de règle de lirecouleur.py fait l'objet
# d'un test de décodage en phonèmes. Le décodage en syllabes porte sur des mots
# réguliers et sur des mots irréguliers, avec vérification du décodage phonémique
# au préalable.
#
# voir http://www.arkaline.fr/doku.php?id=logiciels:lirecouleur
#
# Copyright (c) 2016-2020 by Marie-Pierre Brungard
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

import unittest
from lirecouleur import *


from typing import Iterable, Tuple


class TestSonsIsoles(unittest.TestCase):
    def setUp(self):
        self.voyelles = [
            [('a', 'a')], [('q', 'e')], [('i', 'i')], [('i', 'y')],
            [('o', 'o')], [('o_comp', 'au')], [('o_comp', 'eau')], [('y', 'u')], [('u', 'ou')],
            [('a~', 'en')], [('a~', 'an')], [('a~', 'am')], [('x~', 'un')],
            [('x~', 'um')], [('e~', 'in')], [('e~', 'im')], [('e', u('é'))], [('e_comp', 'er')],
            [('e_comp', 'ez')], [('e_comp', 'et')], [('e^', u('è'))], [('e^_comp', 'est')],
            [('e_comp', 'ai')], [('e^_comp', 'ei')], [('wa', 'oi')], [('w_e~', 'oin')]]

        self.consonnes = [
            [('b', 'b')], [('s_c', 'c')], [('d', 'd')], [('f', 'f')],
            [('g', 'g')], [('#', 'h')], [('i', 'i')], [('z^', 'j')], [('k', 'k')], [('l', 'l')],
            [('m', 'm')], [('n', 'n')], [('p', 'p')], [('k', 'q')], [('r', 'r')], [('s', 's')],
            [('t', 't')], [('v', 'v')], [('w', 'w')], [('#', 'x')], [('#', 'z')]]

    def test_sons_voyelles(self):
        for phonemes in self.voyelles:
            voyelle, son = phonemes[0]
            self.assertEqual(extraire_phonemes(son, son, 0), phonemes)

    def test_sons_consonnes(self):
        for phonemes in self.consonnes:
            _, son = phonemes[0]
            self.assertEqual(extraire_phonemes(son, son, 0), phonemes)


class MixinTest(unittest.TestCase):
    def assert_mots_ok(self,
                       mots: Iterable[Tuple[str, Iterable[Tuple[str, str]]]]):
         for mot, phonemes in mots:
             mot = pretraitement_texte(mot)
             expected_phonemes = [
                 (phoneme, u(grapheme)) for phoneme, grapheme in phonemes
             ]
             actual_phonemes = extraire_phonemes(mot, mot, 0)
             # contrôle de l'extraction de phonèmes
             self.assertEqual(actual_phonemes, expected_phonemes)


class TestMotsRegleA(MixinTest):
    def test_mots(self):
        mots = [
            ('baye', [('b', 'b'), ('a', 'a'), ('j', 'y'), ('q_caduc', 'e')]),
            ('cobaye', [('k', 'c'), ('o', 'o'), ('b', 'b'), ('a', 'a'),
                        ('j', 'y'), ('q_caduc', 'e')]),
            ('pays', [('p', 'p'), ('e^_comp', 'a'), ('i', 'y'), ('#', 's')]),
            ('paysan', [('p', 'p'), ('e^_comp', 'a'), ('i', 'y'), ('z_s', 's'),
                        ('a~', 'an')]),
            ('paysanne', [('p', 'p'), ('e^_comp', 'a'), ('i', 'y'),
                          ('z_s', 's'), ('a', 'a'), ('n', 'nn'),
                          ('q_caduc', 'e')]),
            ('taureau', [('t', 't'), ('o_comp', 'au'), ('r', 'r'),
                         ('o_comp', 'eau')]),
            ('ail', [('a', 'a'), ('j', 'il')]),
            ('maille', [('m', 'm'), ('a', 'a'), ('j', 'ill'),
                        ('q_caduc', 'e')]),
            ('ainsi', [('e~', 'ain'), ('s', 's'), ('i', 'i')]),
            ('capitaine', [('k', 'c'), ('a', 'a'), ('p', 'p'), ('i', 'i'),
                           ('t', 't'), ('e^_comp', 'ai'), ('n', 'n'),
                           ('q_caduc', 'e')]),
            ('main', [('m', 'm'), ('e~', 'ain')]),
            ('plaint', [('p', 'p'), ('l', 'l'), ('e~', 'ain'), ('#', 't')]),
            ('vaincu', [('v', 'v'), ('e~', 'ain'), ('k', 'c'), ('y', 'u')]),
            ('salade', [('s', 's'), ('a', 'a'), ('l', 'l'), ('a', 'a'),
                        ('d', 'd'), ('q_caduc', 'e')]),
            ('appât', [('a', 'a'), ('p', 'pp'), ('a', 'â'), ('#', 't')]),
            ('déjà', [('d', 'd'), ('e', 'é'), ('z^', 'j'), ('a', 'à')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleB(MixinTest):
    def test_mots(self):
        mots = [
            ('bébé', [('b', 'b'), ('e', 'é'), ('b', 'b'), ('e', 'é')]),
            ('rabbin', [('r', 'r'), ('a', 'a'), ('b', 'bb'), ('e~', 'in')]),
            ('plomb', [('p', 'p'), ('l', 'l'), ('o~', 'om'), ('#', 'b')])
        ]

        self.assert_mots_ok(mots)

class TestMotsRegleC(MixinTest):
    def test_mots(self):
        mots = [
        ('ce', [('s_c', 'c'), ('q', 'e')]),
        ('ci', [('s_c', 'c'), ('i', 'i')]),
        ('cygne', [('s_c', 'c'), ('i', 'y'), ('n~', 'gn'), ('q_caduc', 'e')]),
        ('choeur', [('k', 'ch'), ('x', 'oeu'), ('r', 'r')]),
        ('chorale', [('k', 'ch'), ('o_ouvert', 'o'), ('r', 'r'), ('a', 'a'), ('l', 'l'), ('q_caduc', 'e')]),
        ('psychologue', [('p', 'p'), ('s', 's'), ('i', 'y'), ('k', 'ch'), ('o', 'o'), ('l', 'l'), ('o', 'o'), ('g_u', 'gu'), ('q_caduc', 'e')]),
        ('brachiosaure', [('b', 'b'), ('r', 'r'), ('a', 'a'), ('k', 'ch'), ('j_o', 'io'), ('z_s', 's'), ('o_comp', 'au'), ('r', 'r'), ('q_caduc', 'e')]),
        ('chiroptère', [('k', 'ch'), ('i', 'i'), ('r', 'r'), ('o_ouvert', 'o'), ('p', 'p'), ('t', 't'), ('e^', 'è'), ('r', 'r'), ('q_caduc', 'e')]),
        ('chrétien', [('k', 'ch'), ('r', 'r'), ('e', 'é'), ('t', 't'), ('j_e~', 'ien')]),
        ('synchroniser', [('s', 's'), ('e~', 'yn'), ('k', 'ch'), ('r', 'r'), ('o', 'o'), ('n', 'n'), ('i', 'i'), ('z_s', 's'), ('e_comp', 'er')]),
        ('chat', [('s^', 'ch'), ('a', 'a'), ('#', 't')]),
        ('tabac', [('t', 't'), ('a', 'a'), ('b', 'b'), ('a', 'a'), ('#', 'c')]),
        ('donc', [('d', 'd'), ('o~', 'on'), ('k', 'c')]),
        ('blanc',  [('b', 'b'), ('l', 'l'), ('a~', 'an'), ('#', 'c')]),
        ('tronc', [('t', 't'), ('r', 'r'), ('o~', 'on'), ('#', 'c')]),
        ('bac', [('b', 'b'), ('a', 'a'), ('k', 'c')]),
        ('maçon', [('m', 'm'), ('a', 'a'), ('s', 'ç'), ('o~', 'on')]),
        ('archéologie', [('a', 'a'), ('r', 'r'), ('k', 'ch'), ('e', 'é'), ('o', 'o'), ('l', 'l'), ('o_ouvert', 'o'), ('z^_g', 'g'), ('i', 'i'), ('#', 'e')]),
        ('chlorure', [('k', 'ch'), ('l', 'l'), ('o_ouvert', 'o'), ('r', 'r'), ('y', 'u'), ('r', 'r'), ('q_caduc', 'e')]),
        ('orchestre', [('o_ouvert', 'o'), ('r', 'r'), ('k', 'ch'), ('e^_comp', 'e'), ('s', 's'), ('t', 't'), ('r', 'r'), ('q_caduc', 'e')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleD(MixinTest):
    def test_mots(self):
        mots = [
        ('rade', [('r', 'r'), ('a', 'a'), ('d', 'd'), ('q_caduc', 'e')]),
        ('fond', [('f', 'f'), ('o~', 'on'), ('#', 'd')]),
        ('retard', [('r', 'r'), ('q', 'e'), ('t', 't'), ('a', 'a'), ('r', 'r'), ('#', 'd')])
        ]
        self.assert_mots_ok(mots)


class TestMotsRegleE(MixinTest):
    def test_mots(self):
        mots = [
        ('serpent', [('s', 's'), ('e^_comp', 'e'), ('r', 'r'), ('p', 'p'), ('a~', 'en'), ('#', 't')]),
        ('apparemment', [('a', 'a'), ('p', 'pp'), ('a', 'a'), ('r', 'r'), ('a', 'e'), ('m', 'mm'), ('a~', 'en'), ('#', 't')]),
        ('aiment', [('e^_comp', 'ai'), ('m', 'm'), ('q_caduc', 'e'), ('verb_3p', 'nt')]),
        ('batiment', [('b', 'b'), ('a', 'a'), ('t', 't'), ('i', 'i'), ('m', 'm'), ('a~', 'en'), ('#', 't')]),
        ('aimaient', [('e^_comp', 'ai'), ('m', 'm'), ('e^_comp', 'ai'), ('verb_3p', 'ent')]),
        ('clef', [('k', 'c'), ('l', 'l'), ('e_comp', 'ef')]),
        ('hier', [('#', 'h'), ('j_e^_comp', 'ie'), ('r', 'r')]),
        ('femme', [('f', 'f'), ('a', 'e'), ('m', 'mm'), ('q_caduc', 'e')]),
        ('lemme', [('l', 'l'), ('e^_comp', 'e'), ('m', 'mm'), ('q_caduc', 'e')]),
        ('emmener', [('a~', 'em'), ('m', 'm'), ('q', 'e'), ('n', 'n'), ('e_comp', 'er')]),
        ('copient', [('k', 'c'), ('o', 'o'), ('p', 'p'), ('i', 'i'), ('#', 'ent')]),
        ('chien', [('s^', 'ch'), ('j_e~', 'ien')]),
        ('aimez', [('e^_comp', 'ai'), ('m', 'm'), ('e_comp', 'ez')]),
        ('aimer', [('e^_comp', 'ai'), ('m', 'm'), ('e_comp', 'er')]),
        ('pied', [('p', 'p'), ('j_e_comp', 'ied')]),
        ('pique', [('p', 'p'), ('i', 'i'), ('k_qu', 'qu'), ('q_caduc', 'e')]),
        ('figue', [('f', 'f'), ('i', 'i'), ('g_u', 'gu'), ('q_caduc', 'e')]),
        ('je', [('z^', 'j'), ('q', 'e')]),
        ('mes', [('m', 'm'), ('e_comp', 'es')]),
        ('rein', [('r', 'r'), ('e~', 'ein')]),
        ('eu', [('y', 'eu')]),
        ('monsieur', [('m', 'm'), ('q', 'on'), ('s', 's'), ('j_x^', 'ieu'), ('#', 'r')]),
        ('jeudi', [('z^', 'j'), ('x^', 'eu'), ('d', 'd'), ('i', 'i')]),
        ('jeune', [('z^', 'j'), ('x', 'eu'), ('n', 'n'), ('q_caduc', 'e')]),
        ('leur', [('l', 'l'), ('x', 'eu'), ('r', 'r')]),
        ('eux', [('x^', 'eu'), ('#', 'x')]),
        ('est', [('e^_comp', 'est')]),
        ('et', [('e_comp', 'et')]),
        ('soleil', [('s', 's'), ('o', 'o'), ('l', 'l'), ('e^_comp', 'e'), ('j', 'il')]),
        ('geyser', [('z^_g', 'g'), ('e^_comp', 'ey'), ('z_s', 's'), ('e^_comp', 'e'), ('r', 'r')]),
        ('miel', [('m', 'm'), ('j_e^_comp', 'ie'), ('l', 'l')]),
        ('sec', [('s', 's'), ('e^_comp', 'e'), ('k', 'c')]),
        ('ennemi', [('e^_comp', 'e'), ('n', 'nn'), ('q', 'e'), ('m', 'm'), ('i', 'i')]),
        ('ennui', [('a~', 'en'), ('n', 'n'), ('y', 'u'), ('i', 'i')]),
        ('escargot', [('e^_comp', 'e'), ('s', 's'), ('k', 'c'), ('a', 'a'), ('r', 'r'), ('g', 'g'), ('o', 'o'), ('#', 't')]),
        ('abbaye', [('a', 'a'), ('b', 'bb'), ('e^_comp', 'a'), ('i', 'y'), ('#', 'e')]),
        ('que', [('k_qu', 'qu'), ('q', 'e')]),
        ('geai', [('z^_g', 'g'), ('#', 'e'), ('e^_comp', 'ai')]),
        ('jean', [('z^', 'j'), ('#', 'e'), ('a~', 'an')]),
        ('asseoir', [('a', 'a'), ('s', 'ss'), ('#', 'e'), ('wa', 'oi'), ('r', 'r')]),
        ('correcte', [('k', 'c'), ('o_ouvert', 'o'), ('r', 'rr'), ('e^_comp', 'e'), ('k', 'c'), ('t', 't'), ('q_caduc', 'e')]),
        ('aster', [('a', 'a'), ('s', 's'), ('t', 't'), ('e^_comp', 'e'), ('r', 'r')]),
        ('cher', [('s^', 'ch'), ('e^_comp', 'e'), ('r', 'r')]),
        ('coréen', [('k', 'c'), ('o_ouvert', 'o'), ('r', 'r'), ('e', 'é'), ('e~', 'en')]),
        ('lycéen', [('l', 'l'), ('i', 'y'), ('s_c', 'c'), ('e', 'é'), ('e~', 'en')]),
        ('examen', [('e^', 'e'), ('gz', 'x'), ('a', 'a'), ('m', 'm'), ('e~', 'en')]),
        ('golem', [('g', 'g'), ('o', 'o'), ('l', 'l'), ('e^_comp', 'e'), ('m', 'm')]),
        ('cet', [('s_c', 'c'), ('e^_comp', 'e'), ('t', 't')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleG(MixinTest):
    def test_mots(self):
        mots = [
        ('gagner', [('g', 'g'), ('a', 'a'), ('n~', 'gn'), ('e_comp', 'er')]),
        ('gamme', [('g', 'g'), ('a', 'a'), ('m', 'mm'), ('q_caduc', 'e')]),
        ('gomme', [('g', 'g'), ('o_ouvert', 'o'), ('m', 'mm'), ('q_caduc', 'e')]),
        ('gypse', [('z^_g', 'g'), ('i', 'y'), ('p', 'p'), ('s', 's'), ('q_caduc', 'e')]),
        ('geste', [('z^_g', 'g'), ('e^_comp', 'e'), ('s', 's'), ('t', 't'), ('q_caduc', 'e')]),
        ('poing', [('p', 'p'), ('w_e~', 'oin'), ('#', 'g')]),
        ('doigt', [('d', 'd'), ('wa', 'oi'), ('#', 'g'), ('#', 't')]),
        ('gourd', [('g', 'g'), ('u', 'ou'), ('r', 'r'), ('#', 'd')]),
        ('sang', [('s', 's'), ('a~', 'an'), ('#', 'g')]),
        ('long', [('l', 'l'), ('o~', 'on'), ('#', 'g')]),
        ('hareng', [('#', 'h'), ('a', 'a'), ('r', 'r'), ('a~', 'en'), ('#', 'g')]),
        ('aiguille', [('e^_comp', 'ai'), ('g', 'g'), ('y', 'u'), ('i', 'i'), ('j', 'll'), ('q_caduc', 'e')]),
        ('argument', [('a', 'a'), ('r', 'r'), ('g', 'g'), ('y', 'u'), ('m', 'm'), ('a~', 'en'), ('#', 't')]),
        ('vingt', [('v', 'v'), ('e~', 'in'), ('#', 'g'), ('t', 't')]),
        ('vague', [('v', 'v'), ('a', 'a'), ('g_u', 'gu'), ('q_caduc', 'e')]),
        ('grog', [('g', 'g'), ('r', 'r'), ('o', 'o'), ('g', 'g')]),
        ('parking', [('p', 'p'), ('a', 'a'), ('r', 'r'), ('k', 'k'), ('i', 'i'), ('g~', 'ng')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleH(MixinTest):
    def test_mots(self):
        mots = [
        ('hibou', [('#', 'h'), ('i', 'i'), ('b', 'b'), ('u', 'ou')]),
        ('thé', [('t', 't'), ('#', 'h'), ('e', 'é')])
        ]
        self.assert_mots_ok(mots)


class TestMotsRegleI(MixinTest):
    def test_mots(self):
        mots = [
        ('ding', [('d', 'd'), ('i', 'i'), ('g~', 'ng')]),
        ('lin', [('l', 'l'), ('e~', 'in')]),
        ('imbiber', [('e~', 'im'), ('b', 'b'), ('i', 'i'), ('b', 'b'), ('e_comp', 'er')]),
        ('illumina', [('i', 'i'), ('l', 'll'), ('y', 'u'), ('m', 'm'), ('i', 'i'), ('n', 'n'), ('a', 'a')]),
        ('ville', [('v', 'v'), ('i', 'i'), ('l', 'll'), ('q_caduc', 'e')]),
        ('mille', [('m', 'm'), ('i', 'i'), ('l', 'll'), ('q_caduc', 'e')]),
        ('fille', [('f', 'f'), ('i', 'i'), ('j', 'll'), ('q_caduc', 'e')]),
        ('tranquille', [('t', 't'), ('r', 'r'), ('a~', 'an'), ('k_qu', 'qu'), ('i', 'i'), ('l', 'll'), ('q_caduc', 'e')]),
        ('appuient', [('a', 'a'), ('p', 'pp'), ('y', 'u'), ('i', 'i'), ('#', 'ent')]),
        ('confient', [('k', 'c'), ('o~', 'on'), ('f', 'f'), ('i', 'i'), ('#', 'ent')]),
        ('copier', [('k', 'c'), ('o', 'o'), ('p', 'p'), ('j_e_comp', 'ier')]),
        ('pion', [('p', 'p'), ('j_o~', 'ion')]),
        ('chien', [('s^', 'ch'), ('j_e~', 'ien')]),
        ('cyan', [('s_c', 'c'), ('j_a~', 'yan')]),
        ('criant', [('k', 'c'), ('r', 'r'), ('i', 'i'), ('a~', 'an'), ('#', 't')]),
        ('maïs', [('m', 'm'), ('a', 'a'), ('i', 'ï'), ('#', 's')]),
        ('mistigri', [('m', 'm'), ('i', 'i'), ('s', 's'), ('t', 't'), ('i', 'i'), ('g', 'g'), ('r', 'r'), ('i', 'i')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleJ(MixinTest):
    def test_mots(self):
        mots = [
        ('joujou', [('z^', 'j'), ('u', 'ou'), ('z^', 'j'), ('u', 'ou')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleK(MixinTest):
    def test_mots(self):
        mots = [
        ('kaki', [('k', 'k'), ('a', 'a'), ('k', 'k'), ('i', 'i')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleL(MixinTest):
    def test_mots(self):
        mots = [
        ('il', [('i', 'i'), ('l', 'l')]),
        ('fusil', [('f', 'f'), ('y', 'u'), ('z_s', 's'), ('i', 'i'), ('#', 'l')]),
        ('outil', [('u', 'ou'), ('t', 't'), ('i', 'i'), ('#', 'l')]),
        ('gentil', [('z^_g', 'g'), ('a~', 'en'), ('t', 't'), ('i', 'i'), ('#', 'l')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleM(MixinTest):
    def test_mots(self):
        mots = [
        ('somme', [('s', 's'), ('o_ouvert', 'o'), ('m', 'mm'), ('q_caduc', 'e')]),
        ('automne', [('o_comp', 'au'), ('t', 't'), ('o', 'o'), ('#', 'm'), ('n', 'n'), ('q_caduc', 'e')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleN(MixinTest):
    def test_mots(self):
        mots = [
        ('tonne', [('t', 't'), ('o_ouvert', 'o'), ('n', 'nn'), ('q_caduc', 'e')]),
        ('lent', [('l', 'l'), ('a~', 'en'), ('#', 't')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleO(MixinTest):
    def test_mots(self):
        mots = [
        ('coin', [('k', 'c'), ('w_e~', 'oin')]),
        ('roi', [('r', 'r'), ('wa', 'oi')]),
        ('clou', [('k', 'c'), ('l', 'l'), ('u', 'ou')]),
        ('clown', [('k', 'c'), ('l', 'l'), ('u', 'ow'), ('n', 'n')]),
        ('bon', [('b', 'b'), ('o~', 'on')]),
        ('zoo', [('z', 'z'), ('o', 'oo')]),
        ('coefficient', [('k', 'c'), ('o', 'o'), ('e^_comp', 'e'), ('f', 'ff'), ('i', 'i'), ('s_c', 'c'), ('j_a~', 'ien'), ('#', 't')]),
        ('moelle', [('m', 'm'), ('wa', 'oe'), ('l', 'll'), ('q_caduc', 'e')]),
        ('foetus', [('f', 'f'), ('e', 'oe'), ('t', 't'), ('y', 'u'), ('#', 's')]),
        ('oeil', [('x', 'oe'), ('j', 'il')]),
        ('homme', [('#', 'h'), ('o_ouvert', 'o'), ('m', 'mm'), ('q_caduc', 'e')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleP(MixinTest):
    def test_mots(self):
        mots = [
        ('papa', [('p', 'p'), ('a', 'a'), ('p', 'p'), ('a', 'a')]),
        ('alpha', [('a', 'a'), ('l', 'l'), ('f_ph', 'ph'), ('a', 'a')]),
        ('loup', [('l', 'l'), ('u', 'ou'), ('#', 'p')]),
        ('camp', [('k', 'c'), ('a~', 'am'), ('#', 'p')]),
        ('drap', [('d', 'd'), ('r', 'r'), ('a', 'a'), ('#', 'p')]),
        ('trop', [('t', 't'), ('r', 'r'), ('o', 'o'), ('#', 'p')]),
        ('sirop', [('s', 's'), ('i', 'i'), ('r', 'r'), ('o', 'o'), ('#', 'p')]),
        ('salop', [('s', 's'), ('a', 'a'), ('l', 'l'), ('o', 'o'), ('#', 'p')]),
        ('corps', [('k', 'c'), ('o_ouvert', 'o'), ('r', 'r'), ('#', 'p'), ('#', 's')]),
        ('compte', [('k', 'c'), ('o~', 'om'), ('#', 'p'), ('t', 't'), ('q_caduc', 'e')]),
        ('piqure', [('p', 'p'), ('i', 'i'), ('k', 'q'), ('y', 'u'), ('r', 'r'), ('q_caduc', 'e')]),
        ('baptise', [('b', 'b'), ('a', 'a'), ('#', 'p'), ('t', 't'), ('i', 'i'), ('z_s', 's'), ('q_caduc', 'e')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleQ(MixinTest):
    def test_mots(self):
        mots = [
        ('quitte', [('k_qu', 'qu'), ('i', 'i'), ('t', 'tt'), ('q_caduc', 'e')]),
        ('coq', [('k', 'c'), ('o', 'o'), ('k', 'q')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleR(MixinTest):
    def test_mots(self):
        mots = [
        ('monsieur', [('m', 'm'), ('q', 'on'), ('s', 's'), ('j_x^', 'ieu'), ('#', 'r')]),
        ('messieurs', [('m', 'm'), ('e^_comp', 'e'), ('s', 'ss'), ('j_x^', 'ieu'), ('#', 'r'), ('#', 's')]),
        ('gars', [('g', 'g'), ('a', 'a'), ('#', 'rs')]),
        ('gare', [('g', 'g'), ('a', 'a'), ('r', 'r'), ('q_caduc', 'e')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleS(MixinTest):
    def test_mots(self):
        mots = [
        ('mars', [('m', 'm'), ('a', 'a'), ('r', 'r'), ('s', 's')]),
        ('os', [('o', 'o'), ('s', 's')]),
        ('bus', [('b', 'b'), ('y', 'u'), ('s', 's')]),
        ('parasol', [('p', 'p'), ('a', 'a'), ('r', 'r'), ('a', 'a'), ('s', 's'), ('o', 'o'), ('l', 'l')]),
        ('parasite', [('p', 'p'), ('a', 'a'), ('r', 'r'), ('a', 'a'), ('z_s', 's'), ('i', 'i'), ('t', 't'), ('q_caduc', 'e')]),
        ('atlas', [('a', 'a'), ('t', 't'), ('l', 'l'), ('a', 'a'), ('s', 's')]),
        ('bis', [('b', 'b'), ('i', 'i'), ('s', 's')]),
        ('bise', [('b', 'b'), ('i', 'i'), ('z_s', 's'), ('q_caduc', 'e')]),
        ('basse', [('b', 'b'), ('a', 'a'), ('s', 'ss'), ('q_caduc', 'e')]),
        ('chats', [('s^', 'ch'), ('a', 'a'), ('#', 't'), ('#', 's')]),
        ('schlem', [('s^', 'sch'), ('l', 'l'), ('e^_comp', 'e'), ('m', 'm')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleT(MixinTest):
    def test_mots(self):
        mots = [
        ('titi', [('t', 't'), ('i', 'i'), ('t', 't'), ('i', 'i')]),
        ('soutien', [('s', 's'), ('u', 'ou'), ('t', 't'), ('j_e~', 'ien')]),
        ('martien', [('m', 'm'), ('a', 'a'), ('r', 'r'), ('s_t', 't'), ('j_e~', 'ien')]),
        ('soulocratie', [('s', 's'), ('u', 'ou'), ('l', 'l'), ('o_ouvert', 'o'), ('k', 'c'), ('r', 'r'), ('a', 'a'), ('s_t', 't'), ('i', 'i'), ('#', 'e')]),
        ('vingt', [('v', 'v'), ('e~', 'in'), ('#', 'g'), ('t', 't')]),
        ('addition', [('a', 'a'), ('d', 'dd'), ('i', 'i'), ('s_t', 't'), ('j_o~', 'ion')]),
        ('yaourt', [('j_a', 'ya'), ('u', 'ou'), ('r', 'r'), ('t', 't')]),
        ('test', [('t', 't'), ('e^_comp', 'e'), ('s', 's'), ('t', 't')]),
        ('marrant', [('m', 'm'), ('a', 'a'), ('r', 'rr'), ('a~', 'an'), ('#', 't')]),
        ('instinct', [('e~', 'in'), ('s', 's'), ('t', 't'), ('e~', 'in'), ('#', 'c'), ('#', 't')]),
        ('succinct', [('s', 's'), ('y', 'u'), ('k', 'c'), ('s_c', 'c'), ('e~', 'in'), ('#', 'c'), ('#', 't')]),
        ('respect', [('r', 'r'), ('e^_comp', 'e'), ('s', 's'), ('p', 'p'), ('e^_comp', 'e'), ('#', 'c'), ('#', 't')]),
        ('aspect', [('a', 'a'), ('s', 's'), ('p', 'p'), ('e^_comp', 'e'), ('#', 'c'), ('#', 't')]),
        ('tact', [('t', 't'), ('a', 'a'), ('k', 'c'), ('t', 't')]),
        ('direct', [('d', 'd'), ('i', 'i'), ('r', 'r'), ('e^_comp', 'e'), ('k', 'c'), ('t', 't')]),
        ('infect', [('e~', 'in'), ('f', 'f'), ('e^_comp', 'e'), ('k', 'c'), ('t', 't')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleU(MixinTest):
    def test_mots(self):
        mots = [
        ('commun', [('k', 'c'), ('o', 'o'), ('m', 'mm'), ('x~', 'un')]),
        ('cercueil', [('s_c', 'c'), ('e^_comp', 'e'), ('r', 'r'), ('k', 'c'), ('x', 'ue'), ('j', 'il')]),
        ('maximum', [('m', 'm'), ('a', 'a'), ('ks', 'x'), ('i', 'i'), ('m', 'm'), ('o', 'u'), ('m', 'm')]),
        ('parfum', [('p', 'p'), ('a', 'a'), ('r', 'r'), ('f', 'f'), ('x~', 'um')]),
        ('boum', [('b', 'b'), ('u', 'ou'), ('m', 'm')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleV(MixinTest):
    def test_mots(self):
        mots = [
        ('vélo', [('v', 'v'), ('e', 'é'), ('l', 'l'), ('o', 'o')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleW(MixinTest):
    def test_mots(self):
        mots = [
        ('wagon', [('v', 'w'), ('a', 'a'), ('g', 'g'), ('o~', 'on')]),
        ('kiwi', [('k', 'k'), ('i', 'i'), ('w_i', 'wi')]),
        ('wapiti', [('wa', 'wa'), ('p', 'p'), ('i', 'i'), ('t', 't'), ('i', 'i')]),
        ('sandwich', [('s', 's'), ('a~', 'an'), ('d', 'd'), ('w_i', 'wi'), ('s^', 'ch')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleX(MixinTest):
    def test_mots(self):
        mots = [
        ('six', [('s', 's'), ('i', 'i'), ('s_x', 'x')]),
        ('dix', [('d', 'd'), ('i', 'i'), ('s_x', 'x')]),
        ('axe', [('a', 'a'), ('ks', 'x'), ('q_caduc', 'e')]),
        ('fixer', [('f', 'f'), ('i', 'i'), ('ks', 'x'), ('e_comp', 'er')]),
        ('boxe', [('b', 'b'), ('o', 'o'), ('ks', 'x'), ('q_caduc', 'e')]),
        ('xavier', [('gz', 'x'), ('a', 'a'), ('v', 'v'), ('j_e_comp', 'ier')]),
        ('exigu', [('e^', 'e'), ('gz', 'x'), ('i', 'i'), ('g_u', 'gu')]),
        ('exact', [('e^', 'e'), ('gz', 'x'), ('a', 'a'), ('k', 'c'), ('t', 't')]),
        ('hexagone', [('#', 'h'), ('e^', 'e'), ('gz', 'x'), ('a', 'a'), ('g', 'g'), ('o_ouvert', 'o'), ('n', 'n'), ('q_caduc', 'e')]),
        ('coexister', [('k', 'c'), ('o', 'o'), ('e^', 'e'), ('gz', 'x'), ('i', 'i'), ('s', 's'), ('t', 't'), ('e_comp', 'er')]),
        ('inexact', [('i', 'i'), ('n', 'n'), ('e^', 'e'), ('gz', 'x'), ('a', 'a'), ('k', 'c'), ('t', 't')]),
        ('réexamen', [('r', 'r'), ('e', 'é'), ('e^', 'e'), ('gz', 'x'), ('a', 'a'), ('m', 'm'), ('e~', 'en')]),
        ('préexister', [('p', 'p'), ('r', 'r'), ('e', 'é'), ('e^', 'e'), ('gz', 'x'), ('i', 'i'), ('s', 's'), ('t', 't'), ('e_comp', 'er')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleY(MixinTest):
    def test_mots(self):
        mots = [
        ('abbaye', [('a', 'a'), ('b', 'bb'), ('e^_comp', 'a'), ('i', 'y'), ('#', 'e')]),
        ('voyage', [('v', 'v'), ('wa', 'o'), ('j_a', 'ya'), ('z^_g', 'g'), ('q_caduc', 'e')]),
        ('pays', [('p', 'p'), ('e^_comp', 'a'), ('i', 'y'), ('#', 's')]),
        ('synchroniser', [('s', 's'), ('e~', 'yn'), ('k', 'ch'), ('r', 'r'), ('o', 'o'), ('n', 'n'), ('i', 'i'), ('z_s', 's'), ('e_comp', 'er')]),
        ('gymnaste', [('z^_g', 'g'), ('i', 'y'), ('m', 'm'), ('n', 'n'), ('a', 'a'), ('s', 's'), ('t', 't'), ('q_caduc', 'e')]),
        ('lyncher', [('l', 'l'), ('e~', 'yn'), ('s^', 'ch'), ('e_comp', 'er')]),
        ('dynamo', [('d', 'd'), ('i', 'y'), ('n', 'n'), ('a', 'a'), ('m', 'm'), ('o', 'o')])
        ]

        self.assert_mots_ok(mots)


class TestMotsRegleZ(MixinTest):
    def test_mots(self):
        mots = [
        ('zozoter', [('z', 'z'), ('o', 'o'), ('z', 'z'), ('o', 'o'), ('t', 't'), ('e_comp', 'er')])
        ]

        self.assert_mots_ok(mots)


class MixinSyllabeTest(unittest.TestCase):
    def assert_syllabes_ok(self, mots):
        for mot, metadata in mots.items():
            phonemes = metadata['phoneme']
            syllabes = metadata['syllabe']
            mot = pretraitement_texte(mot)
            # contrôle de type de chaîne
            self.assertEqual(mot, u(mot))
            # contrôle de l'extraction de phonèmes
            pp = extraire_phonemes(mot, mot, 0)
            self.assertEqual(pp, [
                (phoneme, u(grapheme)) for phoneme, grapheme in phonemes
            ])
            # contrôler ensuite le décodage en syllabes
            self.assertEqual(extraire_syllabes(pp), [u(syll) for syll in syllabes])


class TestSyllabesMots1(MixinSyllabeTest):
    def test_mots(self):
        mots = {
            'abri': {'phoneme': [('a', 'a'), ('b', 'b'), ('r', 'r'), ('i', 'i')],
                     'syllabe': ['a', 'bri']},
            'adresse': {'phoneme': [('a', 'a'),
                                    ('d', 'd'),
                                    ('r', 'r'),
                                    ('e^_comp', 'e'),
                                    ('s', 'ss'),
                                    ('q_caduc', 'e')],
                        'syllabe': ['a', 'dre', 'sse']},
            'appel': {'phoneme': [('a', 'a'), ('p', 'pp'), ('e^_comp', 'e'), ('l', 'l')],
                      'syllabe': ['a', 'ppel']},
            'approche': {'phoneme': [('a', 'a'),
                                     ('p', 'pp'),
                                     ('r', 'r'),
                                     ('o_ouvert', 'o'),
                                     ('s^', 'ch'),
                                     ('q_caduc', 'e')],
                         'syllabe': ['a', 'ppro', 'che']},
            'avenue': {'phoneme': [('a', 'a'),
                                   ('v', 'v'),
                                   ('q', 'e'),
                                   ('n', 'n'),
                                   ('y', 'u'),
                                   ('#', 'e')],
                       'syllabe': ['a', 've', 'nue']},
            'caisse': {'phoneme': [('k', 'c'),
                                   ('e^_comp', 'ai'),
                                   ('s', 'ss'),
                                   ('q_caduc', 'e')],
                       'syllabe': ['cai', 'sse']},
            'copieur': {'phoneme': [('k', 'c'),
                                    ('o', 'o'),
                                    ('p', 'p'),
                                    ('j_x', 'ieu'),
                                    ('r', 'r')],
                        'syllabe': ['co', 'pieur']},
            'couvée': {'phoneme': [('k', 'c'),
                                   ('u', 'ou'),
                                   ('v', 'v'),
                                   ('e', 'é'),
                                   ('#', 'e')],
                       'syllabe': ['cou', 'vée']},
            'explosion': {'phoneme': [('e^', 'e'),
                                      ('ks', 'x'),
                                      ('p', 'p'),
                                      ('l', 'l'),
                                      ('o', 'o'),
                                      ('z_s', 's'),
                                      ('j_o~', 'ion')],
                          'syllabe': ['ex', 'plo', 'sion']},
            'force': {'phoneme': [('f', 'f'),
                                  ('o_ouvert', 'o'),
                                  ('r', 'r'),
                                  ('s_c', 'c'),
                                  ('q_caduc', 'e')],
                      'syllabe': ['for', 'ce']},
            'friser': {'phoneme': [('f', 'f'),
                                   ('r', 'r'),
                                   ('i', 'i'),
                                   ('z_s', 's'),
                                   ('e_comp', 'er')],
                       'syllabe': ['fri', 'ser']},
            'fumer': {'phoneme': [('f', 'f'), ('y', 'u'), ('m', 'm'), ('e_comp', 'er')],
                      'syllabe': ['fu', 'mer']},
            'matin': {'phoneme': [('m', 'm'), ('a', 'a'), ('t', 't'), ('e~', 'in')],
                      'syllabe': ['ma', 'tin']},
            'meilleur': {'phoneme': [('m', 'm'),
                                     ('e^_comp', 'e'),
                                     ('j', 'ill'),
                                     ('x', 'eu'),
                                     ('r', 'r')],
                         'syllabe': ['me', 'illeur']},
            'muscle': {'phoneme': [('m', 'm'),
                                   ('y', 'u'),
                                   ('s', 's'),
                                   ('k', 'c'),
                                   ('l', 'l'),
                                   ('q_caduc', 'e')],
                       'syllabe': ['mus', 'cle']},
            'nul': {'phoneme': [('n', 'n'), ('y', 'u'), ('l', 'l')], 'syllabe': ['nul']},
            'onze': {'phoneme': [('o~', 'on'), ('z', 'z'), ('q_caduc', 'e')],
                     'syllabe': ['on', 'ze']},
            'pair': {'phoneme': [('p', 'p'), ('e^_comp', 'ai'), ('r', 'r')],
                     'syllabe': ['pair']},
            'piloter': {'phoneme': [('p', 'p'),
                                    ('i', 'i'),
                                    ('l', 'l'),
                                    ('o', 'o'),
                                    ('t', 't'),
                                    ('e_comp', 'er')],
                        'syllabe': ['pi', 'lo', 'ter']},
            'rétablir': {'phoneme': [('r', 'r'),
                                     ('e', 'é'),
                                     ('t', 't'),
                                     ('a', 'a'),
                                     ('b', 'b'),
                                     ('l', 'l'),
                                     ('i', 'i'),
                                     ('r', 'r')],
                         'syllabe': ['ré', 'ta', 'blir']},
            'soleil': {'phoneme': [('s', 's'),
                                   ('o', 'o'),
                                   ('l', 'l'),
                                   ('e^_comp', 'e'),
                                   ('j', 'il')],
                       'syllabe': ['so', 'leil']},
            'sonnerie': {'phoneme': [('s', 's'),
                                     ('o', 'o'),
                                     ('n', 'nn'),
                                     ('q', 'e'),
                                     ('r', 'r'),
                                     ('i', 'i'),
                                     ('#', 'e')],
                         'syllabe': ['so', 'nne', 'rie']},
            'talon': {'phoneme': [('t', 't'), ('a', 'a'), ('l', 'l'), ('o~', 'on')],
                      'syllabe': ['ta', 'lon']},
            'éponge': {'phoneme': [('e', 'é'),
                                   ('p', 'p'),
                                   ('o~', 'on'),
                                   ('z^_g', 'g'),
                                   ('q_caduc', 'e')],
                       'syllabe': ['é', 'pon', 'ge']}}

        self.assert_syllabes_ok(mots)


class TestSyllabesMots2(MixinSyllabeTest):
    def test_mots(self):
        mots = {
            'aiguille': {'phoneme': [('e^_comp', 'ai'),
                                     ('g', 'g'),
                                     ('y', 'u'),
                                     ('i', 'i'),
                                     ('j', 'll'),
                                     ('q_caduc', 'e')],
                         'syllabe': ['ai', 'gui', 'lle']},
            'automne': {'phoneme': [('o_comp', 'au'),
                                    ('t', 't'),
                                    ('o', 'o'),
                                    ('#', 'm'),
                                    ('n', 'n'),
                                    ('q_caduc', 'e')],
                        'syllabe': ['au', 'tom', 'ne']},
            'cassis': {'phoneme': [('k', 'c'),
                                   ('a', 'a'),
                                   ('s', 'ss'),
                                   ('i', 'i'),
                                   ('#', 's')],
                       'syllabe': ['ca', 'ssis']},
            'chorale': {'phoneme': [('k', 'ch'),
                                    ('o_ouvert', 'o'),
                                    ('r', 'r'),
                                    ('a', 'a'),
                                    ('l', 'l'),
                                    ('q_caduc', 'e')],
                        'syllabe': ['cho', 'ra', 'le']},
            'examen': {'phoneme': [('e^', 'e'),
                                   ('gz', 'x'),
                                   ('a', 'a'),
                                   ('m', 'm'),
                                   ('e~', 'en')],
                       'syllabe': ['e', 'xa', 'men']},
            'faisan': {'phoneme': [('f', 'f'),
                                   ('e^_comp', 'ai'),
                                   ('z_s', 's'),
                                   ('a~', 'an')],
                       'syllabe': ['fai', 'san']},
            'femme': {'phoneme': [('f', 'f'), ('a', 'e'), ('m', 'mm'), ('q_caduc', 'e')],
                      'syllabe': ['fe', 'mme']},
            'fusil': {'phoneme': [('f', 'f'),
                                  ('y', 'u'),
                                  ('z_s', 's'),
                                  ('i', 'i'),
                                  ('#', 'l')],
                      'syllabe': ['fu', 'sil']},
            'hiver': {'phoneme': [('#', 'h'), ('i', 'i'), ('v', 'v'), ('e_comp', 'er')],
                      'syllabe': ['hi', 'ver']},
            'mille': {'phoneme': [('m', 'm'), ('i', 'i'), ('l', 'll'), ('q_caduc', 'e')],
                      'syllabe': ['mi', 'lle']},
            'moelle': {'phoneme': [('m', 'm'),
                                   ('wa', 'oe'),
                                   ('l', 'll'),
                                   ('q_caduc', 'e')],
                       'syllabe': ['moe', 'lle']},
            'monsieur': {'phoneme': [('m', 'm'),
                                     ('q', 'on'),
                                     ('s', 's'),
                                     ('j_x^', 'ieu'),
                                     ('#', 'r')],
                         'syllabe': ['mon', 'sieur']},
            'net': {'phoneme': [('n', 'n'), ('e^_comp', 'et')], 'syllabe': ['net']},
            'oignon': {'phoneme': [('o', 'oi'), ('n~', 'gn'), ('o~', 'on')],
                       'syllabe': ['oi', 'gnon']},
            'orchestre': {'phoneme': [('o_ouvert', 'o'),
                                      ('r', 'r'),
                                      ('k', 'ch'),
                                      ('e^_comp', 'e'),
                                      ('s', 's'),
                                      ('t', 't'),
                                      ('r', 'r'),
                                      ('q_caduc', 'e')],
                          'syllabe': ['or', 'ches', 'tre']},
            'ours': {'phoneme': [('u', 'ou'), ('r', 'r'), ('s', 's')],
                     'syllabe': ['ours']},
            'parasol': {'phoneme': [('p', 'p'),
                                    ('a', 'a'),
                                    ('r', 'r'),
                                    ('a', 'a'),
                                    ('s', 's'),
                                    ('o', 'o'),
                                    ('l', 'l')],
                        'syllabe': ['pa', 'ra', 'sol']},
            'porc': {'phoneme': [('p', 'p'), ('o_ouvert', 'o'), ('r', 'r'), ('#', 'c')],
                     'syllabe': ['porc']},
            'révolver': {'phoneme': [('r', 'r'),
                                     ('e', 'é'),
                                     ('v', 'v'),
                                     ('o_ouvert', 'o'),
                                     ('l', 'l'),
                                     ('v', 'v'),
                                     ('e^_comp', 'e'),
                                     ('r', 'r')],
                         'syllabe': ['ré', 'vol', 'ver']},
            'second': {'phoneme': [('s', 's'),
                                   ('q', 'e'),
                                   ('k', 'c'),
                                   ('o~', 'on'),
                                   ('#', 'd')],
                       'syllabe': ['se', 'cond']},
            'septième': {'phoneme': [('s', 's'),
                                     ('e^_comp', 'e'),
                                     ('p', 'p'),
                                     ('t', 't'),
                                     ('j_e^', 'iè'),
                                     ('m', 'm'),
                                     ('q_caduc', 'e')],
                         'syllabe': ['sep', 'tiè', 'me']},
            'tabac': {'phoneme': [('t', 't'),
                                  ('a', 'a'),
                                  ('b', 'b'),
                                  ('a', 'a'),
                                  ('#', 'c')],
                      'syllabe': ['ta', 'bac']},
            'écho': {'phoneme': [('e', 'é'), ('s^', 'ch'), ('o', 'o')],
                     'syllabe': ['é', 'cho']}}

        self.assert_syllabes_ok(mots)


if __name__ == "__main__":
    unittest.main()
