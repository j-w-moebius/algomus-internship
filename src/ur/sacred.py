#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  This file is part of "Ur" <http://www.algomus.fr>,
#  Co-creative generic music generation
#  Copyright (C) 2024 by Algomus team at CRIStAL 
#  (UMR CNRS 9189, Université Lille)
#
#  "Ur" is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  "Ur" is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with "Ur". If not, see <http://www.gnu.org/licenses/>


import ur
import gabuzomeu
import random
from rich import print


class Structure(ur.ItemChoice):
    CHOICES = ['AABC', 'ABA']

class FuncMajor(ur.ItemMarkov):

    SOURCE = '(Kelley 2016)'

    STATES = ['i', 'T', 'S', 'D']
    INITIAL = ['i']
    FINAL = ['i']

    TRANSITIONS = {
        'i': { 'i': 0.62, 'T': 0.10, 'S': 0.09, 'D': 0.18 },
        'T': { 'i': 0.62, 'T': 0.10, 'S': 0.09, 'D': 0.18 },
        'S': { 'i': 0.43, 'T': 0.10, 'S': 0.18, 'D': 0.28 },
        'D': { 'i': 0.57, 'T': 0.10, 'S': 0.09, 'D': 0.25 },
    }

    EMISSIONS = {
        'i': {'I': 1.00},
        'T': {'vi': 0.22, 'I': 0.78},
        'S': {'ii': 0.54, 'IV': 0.46},
        'D': {'iii': 0.21, 'V': 0.72, 'vii': 0.07},
    }


class FuncMinor(ur.ItemMarkov):

    SOURCE = '(Kelley 2016)'

    STATES = ['T', 'S', 'D']
    INITIAL = ['T']
    FINAL = ['T']

    TRANSITIONS = {
        'T': { 'T': 0.53, 'S': 0.08, 'D': 0.39 },
        'S': { 'T': 0.31, 'S': 0.14, 'D': 0.55 },
        'D': { 'T': 0.49, 'S': 0.08, 'D': 0.43 },
    }

    EMISSIONS = {
        'T': {'i': 1.00},
        'S': {'iim': 0.19, 'iv': 0.53, 'VI': 0.28},
        'D': {'III': 0.35, 'v': 0.32, 'VII': 0.33},
    }


class Rhythm(ur.ItemSequence):
    ITEMS_LAST = [
        ('2', 0.5),
        ('4', 0.5),
    ]
    ITEMS = [
                ('4', 0.7),
                ('8 8', 0.25),
                ('4. 8', 0.05),
            ]

class Melody0(ur.ItemSequence):
    ITEMS = 'cdefgab'

class MelodyMajorUp(ur.ItemMarkov):

    SOURCE = ''

    STATES = [ 'e', 'f', 'g', 'a', 'b', "c'", "d'", "e'", "g'"]
    INITIAL = [ 'e', 'g', "c'"]
    FINAL = STATES

    TRANSITIONS = {
        'e':  { 'e': 0.20, 'f': 0.10, 'g': 0.30,  "a": 0.20  },
        'f':  { 'e': 0.30, 'f': 0.00, 'g': 0.00, "c'": 0.00, "d'": 0.00},
        'g':  { 'f': 0.10, 'g': 0.20, 'a': 0.30, "c'": 0.10,  "d'": 0.10 },
        'a':  { 'e': 0.30, 'f': 0.00, 'g': 0.30, 'a': 0.20, 'b': 0.10, "c'": 0.10, "d'": 0.10 },
        'b':  { 'g': 0.10, 'a': 0.30, 'b': 0.00, "c'": 0.30, "d'": 0.10 },
        "c'": { 'g': 0.30, 'a': 0.10, 'b': 0.10, "c'": 0.20, "d'": 0.30, "e'" :0.20 , "g'": 0.10 },
        "d'": { 'a': 0.10, "c'": 0.30, "d'": 0.20, "e'": 0.20 },
        "e'": { "c'": 0.20, "d'": 0.20, "e'": 0.20, "g'": 0.10 },
        "g'": { "e'": 0.20 },
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }


class MelodyMajorDown(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['c', 'd', 'e', 'f', 'g', 'a', 'b', "c'"]
    INITIAL = ['c', 'e', 'g']
    FINAL = STATES

    TRANSITIONS = {
        'c':  {                       'c': 0.20, 'd': 0.30, 'e': 0.30, 'g': 0.30 },
        'd':  {            'c': 0.30, 'd': 0.20, 'e': 0.10, 'g': 0.10,  'a': 0.20 },
        'e':  { 'c': 0.10, 'd': 0.30, 'e': 0.20, 'f': 0.10, 'g': 0.30,  "a": 0.20  },
        'f':  { 'c': 0.00, 'd': 0.00, 'e': 0.30, 'f': 0.00, 'g': 0.00, "c'": 0.00 },
        'g':  { 'c': 0.10, 'd': 0.20, 'f': 0.10, 'g': 0.20, 'a': 0.30, "c'": 0.10,  },
        'a':  { 'e': 0.30, 'f': 0.00, 'g': 0.30, 'a': 0.20, 'b': 0.10, "c'": 0.10 },
        'b':  { 'g': 0.10, 'a': 0.30, 'b': 0.00, "c'": 0.30 },
        "c'": { 'g': 0.30, 'a': 0.10, 'b': 0.10, "c'": 0.20  },
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }


class MelodyMinorUp(ur.ItemMarkov):

    SOURCE = ''

    STATES = [ 'e', 'f', 'g', 'a', 'b', "c'", "d'", "e'"]
    INITIAL = [ 'e', 'a', "c'"]
    FINAL = STATES

    TRANSITIONS = {
        'e':  {         'e': 0.20, 'f': 0.10, 'g': 0.30,  "a": 0.20  },
        'f':  {         'e': 0.30, 'f': 0.00, 'g': 0.30, "c'": 0.00 },
        'g':  {            'e': 0.30, 'f': 0.10, 'g': 0.20, 'a': 0.30, "b": 0.30   },
        'a':  { 'e': 0.30, 'f': 0.00, 'g': 0.30, 'a': 0.20, 'b': 0.30, "c'": 0.10, "e'": 0.20  },
        'b':  { 'g': 0.30, 'a': 0.30, 'b': 0.30, "c'": 0.10, "e'": 0.20  },
        "c'": { 'g': 0.30, 'a': 0.30, 'b': 0.30, "c'": 0.10, "d'": 0.10  },
        "d'": { 'a': 0.10, 'b': 0.20, "c'": 0.30, "d'": 0.10,  "e'": 0.20 },        
        "e'": { "c'": 0.20, "d'": 0.20, "e'": 0.20 },
    }
    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }



class MelodyMinorDown(ur.ItemMarkov):

    SOURCE = ''

    STATES = ["a,", "b,", 'c', 'd', 'e', 'f', 'g', 'a', 'b', "c'"]
    INITIAL = ['a,', 'c', 'e', 'a']
    FINAL = STATES

    TRANSITIONS = {
        'a,':  {                      'a,': 0.20, 'b,': 0.30, 'e': 0.30 },
        'b,':  {                      'a,': 0.20, 'b,': 0.30, 'c': 0.10, 'd': 0.20  },
        'c':  {              'b': 0.20,   'c': 0.20, 'd': 0.30 },
        'd':  { 'b': 0.10,   'c': 0.10, 'd': 0.10, 'e': 0.30, 'g': 0.10,  'a': 0.20 },
        'e':  { 'a,': 0.30, 'd': 0.30, 'e': 0.20, 'f': 0.10, 'g': 0.30,  "a": 0.20  },
        'f':  { 'c': 0.00, 'd': 0.00, 'e': 0.30, 'f': 0.00, 'g': 0.30, "c'": 0.00 },
        'g':  {            'e': 0.30, 'f': 0.10, 'g': 0.20, 'a': 0.30, "b": 0.30   },
        'a':  { 'a,': 0.30, 'e': 0.30, 'f': 0.00, 'g': 0.30, 'a': 0.20, 'b': 0.30, 'c': 0.10  },
        'b':  { 'g': 0.30, 'a': 0.30, 'b': 0.30, "c'": 0.10  },
        "c'": { 'g': 0.30, 'a': 0.30, 'b': 0.30, "c'": 0.10 },
    }
    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }



class ScorerHarmMelody(ur.ScorerSequence):

    CHORDS = {
        'I': 'ceg',
        'ii': 'dfa',
        'iii': 'egb',
        'IV': 'fac',
        'V': 'gd',
        'vi': 'ace',
        'vii': 'bdf',

        'i': 'ae',
        'iim': 'bdf',
        'III': 'ceg',
        'iv': 'dfa',
        'v': 'egb',
        'VI': 'fac',
        'VII': 'gd',
    }

    def score_element(self, harm, mel):
        # print (mel, harm, self.CHORDS[harm])
        if mel[0] in self.CHORDS[harm]:
            return 1.0
        else:
            return 0.0

    def score_first_last_element(self, harm, mel):
        if mel[0] in self.CHORDS[harm]:
            return 1.0
        else:
            return -20


class ScorerHarmMelodyRoot(ScorerHarmMelody):

    SCORES = {
        None: -5.0,
        0: 1.0,
        1: 0.5,
        2: 0.2,
    }

    '''Favors 5, '''
    def score_element(self, harm, mel):
        if mel[0] in self.CHORDS[harm]:
            i = self.CHORDS[harm].index(mel[0])
            return self.SCORES[i]
        else:
            return self.SCORES[None]

    def score_first_last_element(self, harm, mel):
        if mel[0] == self.CHORDS[harm][0]:
            return 0.0
        else:
            return -20.0


print('[yellow]### Init')
sh = ur.Model()

sh.add(Structure('struct'))

mode = random.choice(['Major', 'minor'])

# sh.add(ur.Or('func', [FuncMajor('Major'),
#                       FuncMinor('minor')]))

if mode == 'Major':
    Func = FuncMajor
    MelodyUp = MelodyMajorUp
    MelodyDown = MelodyMajorDown
else:
    Func = FuncMinor
    MelodyUp = MelodyMinorUp
    MelodyDown = MelodyMinorDown
    
sh.add(Func('func'))
sh.structurer('struct', 'func')

sh.add(MelodyUp('mel'))
score = sh.scorer(ScorerHarmMelody, 'func', 'mel')

sh.add(MelodyUp('melS'))
scoreS = sh.scorer(ScorerHarmMelody, 'func', 'melS')

sh.add(MelodyDown('melA'))
scoreA = sh.scorer(ScorerHarmMelody, 'func', 'melA')

sh.add(MelodyDown('melB'))
scoreB = sh.scorer(ScorerHarmMelodyRoot, 'func', 'melB')

sh.add(Rhythm('rhy'))

print(sh)

# -------------------------------------------------------

print('[yellow]### Gen 1, independent')
sh.generate()
sh.score()
print(sh)

# -------------------------------------------------------

print('[yellow]### Gen 2')
sh.reset()
sh['struct'].gen()
sh.set_structure()

d0 = sh['func'].gen()
print("d0", d0)

sh['mel'].set_filter(score)
m0 = sh['mel'].gen(d0)


sh['melS'].set_filter(scoreS)
m0 = sh['melS'].gen(d0)
sh['melA'].set_filter(scoreA)
m0 = sh['melA'].gen(d0)

sh['melB'].set_filter(scoreB)
m0 = sh['melB'].gen(d0)

sh['rhy'].gen(d0)

sh.score()
print(sh)


sh.export(
    gabuzomeu.sentence(),
    sh['struct'].structure,
    sh['rhy'],
    ['melS', 'melA', 'mel', 'melB'],
    ['func']
    )