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
from rich import print


class Structure(ur.ItemChoice):
    CHOICES = ['AABC', 'ABA']

class FuncMajor(ur.ItemMarkov):

    SOURCE = '(Kelley 2016)'

    STATES = ['T', 'S', 'D']
    INITIAL = ['T']
    FINAL = ['T']

    TRANSITIONS = {
        'T': { 'T': 0.72, 'S': 0.09, 'D': 0.18 },
        'S': { 'T': 0.53, 'S': 0.18, 'D': 0.28 },
        'D': { 'T': 0.67, 'S': 0.09, 'D': 0.25 },
    }

    EMISSIONS = {
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


class Melody0(ur.ItemSequence):
    ITEMS = 'cdefgab'

class Melody1(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['c', 'd', 'e', 'f', 'g', 'a', 'b', "c'", "d'"]
    INITIAL = ['c', 'e', 'g']
    FINAL = STATES

    TRANSITIONS = {
        'c':  {                       'c': 0.20, 'd': 0.30, 'g': 0.10 },
        'd':  {            'c': 0.30, 'd': 0.20, 'e': 0.10, 'g': 0.10,  "c'": 0.10 },
        'e':  { 'c': 0.10, 'd': 0.30, 'e': 0.20, 'f': 0.30, 'g': 0.10,  "b": 0.10  },
        'f':  { 'd': 0.10, 'e': 0.30, 'f': 0.20, 'g': 0.30, "c'": 0.10, "d'": 0.10},
        'g':  { 'c': 0.10, 'f': 0.30, 'g': 0.20, 'a': 0.30, 'c': 0.10,  "d'": 0.10 },
        'a':  { 'f': 0.10, 'g': 0.30, 'a': 0.20, 'b': 0.30, "d'": 0.10 },
        'b':  { 'g': 0.10, 'a': 0.30, 'b': 0.20, "c'": 0.30, "d'": 0.10 },
        "c'": { 'a': 0.10, 'b': 0.30, "c'": 0.20, "d'": 0.30,  },
        "d'": { 'b': 0.10, "c'": 0.30, "d'": 0.20,  },
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
        'V': 'gbc',
        'vi': 'ace',
        'vii': 'bdf',

        'i': 'ae',
        'iim': 'bdf',
        'III': 'ceg',
        'iv': 'dfa',
        'v': 'eb',
        'VI': 'fac',
        'VII': 'gcb',
    }

    def score_element(self, harm, mel):
        # print (mel, harm, self.CHORDS[harm])
        if mel in self.CHORDS[harm]:
            return 1.0
        else:
            return 0.0



print('[yellow]### Init')
sh = ur.Model()

sh.add(Structure('struct'))
sh.add(ur.Or('func', [FuncMajor('Major'),
                      FuncMinor('minor')]))
sh.structurer('struct', 'Major')
sh.structurer('struct', 'minor')

sh.add(Melody1('mel'))
sh.scorer(ScorerHarmMelody, 'func', 'mel')

sh.add(Melody0('melB'))
sh.scorer(ScorerHarmMelody, 'func', 'melB')

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

sh['mel'].set_filter(sh.scorers[0])
m0 = sh['mel'].gen(d0)

sh['melB'].set_filter(sh.scorers[0])
m0 = sh['melB'].gen(d0)

sh.score()
print(sh)

sh.export(sh['struct'].structure, ['mel', 'melB'], ['func'])