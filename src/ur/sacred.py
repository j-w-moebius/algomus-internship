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


class Structure(ur.Items):
    ITEMS = ['AABC', 'ABA']

class FuncMajor(ur.Markov):

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


class FuncMinor(ur.Markov):

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


class Melody(ur.Sequence):
    ITEMS = 'cdefgab'

class ScoreHarmMelody(ur.seqScorer):

    CHORDS = {
        'I': 'ceg',
        'ii': 'dfa',
        'iii': 'egb',
        'IV': 'fac',
        'V': 'gbc',
        'vi': 'ace',
        'vii': 'bdf',

        'i': 'ac',
        'iim': 'bdf',
        'III': 'ceg',
        'iv': 'dfa',
        'v': 'eb',
        'VI': 'fac',
        'VII': 'gcb',
    }

    def score_one(self, harm, mel):
        # print (mel, harm, self.CHORDS[harm])
        if mel in self.CHORDS[harm]:
            return 1.0
        else:
            return 0.0



print('[yellow]### Init')
sh = ur.model()

sh.add(Structure('struct'))
sh.add(ur.Or('func', [FuncMajor('Major'),
                      FuncMinor('minor')]))
sh.structurer('struct', 'Major')
sh.structurer('struct', 'minor')

sh.add(Melody('mel'))
sh.scorer(ScoreHarmMelody, 'func', 'mel')

sh.add(Melody('melB'))
sh.scorer(ScoreHarmMelody, 'func', 'melB')

print(sh)

print('[yellow]### Gen 1, independent')
sh.generate()
sh.score()
print(sh)


print('[yellow]### Gen 2')
sh.reset()
sh['struct'].gen()
# sh.set_structure()

d0 = sh['func'].gen()
print(d0)

sh['mel'].set_filter(lambda x: sh.scorers[0].score(d0.data, x.data))
m0 = sh['mel'].gen(d0)

sh['melB'].set_filter(lambda x: sh.scorers[0].score(d0.data, x.data))
m0 = sh['melB'].gen(d0)

sh.scorers[0].score(d0.data, m0.data, verbose=True)
print(sh)