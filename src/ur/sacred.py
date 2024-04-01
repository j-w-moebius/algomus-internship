#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  This file is part of "Ur" <http://www.algomus.fr>,
#  Co-creative generic music generation
#  Copyright (C) 2024 by Algomus team at CRIStAL 
#  (UMR CNRS 9189, Université Lille)
#
#  Contributors:
#   - Mathieu Giraud
#   - Ken Déguernel
#   - Romain Carl
#  in collaboration with Holly Herndon and Ian Berman
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
import glob
import gabuzomeu
import random
import music
import music21
from rich import print
import argparse

from models.harp import *
from models.woo import *

parser = argparse.ArgumentParser(description = 'Fake Sacred Harp')
parser.add_argument('--save', '-s', type=int, default=0, help='starting number to save generation, otherwise draft generations')
parser.add_argument('--nb', '-n', type=int, default=0, help='number of generations with --save')
parser.add_argument('--svg', action='store_true', help='generate and opens .svg (requires Verovio and Firefox)')
parser.add_argument('--woo', action='store_true', help='experiment')


def gen_sacred(woo):
    print('[yellow]### Init')

    key = random.choice(Key.CHOICES)
    print(f'Key: [blue]{key}')
    mode = 'minor'

    # sh.add(ur.Or('func', [FuncMajor('Major'),
    #                       FuncMinor('minor')]))

    if mode == 'Major':
        Func = FuncMajor
        # MelodyUp = MelodyMajorUp
        # MelodyDown = MelodyMajorDown
        MelodyS = MelodyMajorS
        MelodyA = MelodyMajorA
        MelodyT = MelodyMajorT
        MelodyB = MelodyMajorB
    else:
        Func = FuncMinor
        # MelodyUp = MelodyMinorUp
        # MelodyDown = MelodyMinorDown
        MelodyS = MelodyMinorS
        MelodyA = MelodyMinorA
        MelodyT = MelodyMinorT
        MelodyB = MelodyMinorB

    if woo:
        zFunc = WFunc
        zScorerMelodyHarm = WScorerMelodyHarm
        zScorerMelodyHarmRoot = WScorerMelodyHarm
        zLyrics = WLyrics
        zRhythm = WRhythm
        zScorerRhythmMetrics = WScorerRhythmMetrics
        zStructure = WStructure
    else:
        zFunc = Func
        zScorerMelodyHarm = ScorerMelodyHarm
        zScorerMelodyHarmRoot = ScorerMelodyHarm
        zLyrics = Lyrics
        zRhythm = Rhythm
        zScorerRhythmMetrics = ScorerRhythmMetrics
        zStructure = Structure

    sh = ur.Model()
    sh.add(zStructure('struct'))

    sh.add(zFunc('func'))
    sh.structurer('struct', 'func')

    sh.add(MelodyT('mel'))
    sh['mel'].set_key(key)
    sh['mel'].flourish = {
            'third-passing': 0.7,
            'third-16': 0.3,
            'same-neighbor': 0.5,
            'same-neighbor-16': 0.1,
            'second-jump': 0.4,
            'second-8-16-16': 0.2,
            'fourth-8-16-16': 0.3,
            'fifth-jump': 0.2,
            'fifth-16': 0.4,
        }
    sh.scorer(zScorerMelodyHarm, 'mel', 'func', 2)
    sh.scorer(ScorerMelody, 'mel')

    sh.add(MelodyB('melB'))
    sh['melB'].set_key(key)
    sh['melB'].flourish = {
            'third-passing': 0.7,
            'third-16': 0,
            'same-neighbor': 0,
            'same-neighbor-16': 0,
            'second-jump': 0,
            'second-8-16-16': 0,
            'fourth-8-16-16': 0.3,
            'fifth-jump': 0.7,
            'fifth-16': 0.2,
        }
    sh.scorer(zScorerMelodyHarmRoot, 'melB', 'func', 2)
    sh.scorer(ScorerMelodyMelody, 'melB', 'mel')
    sh.scorer(ScorerMelodyMelodyBelow, 'melB', 'mel')

    sh.add(MelodyS('melS'))
    sh['melS'].set_key(key)
    sh.scorer(zScorerMelodyHarm, 'melS', 'func', 4)
    sh.scorer(ScorerMelodySA, 'melS', weight=2)
    sh.scorer(ScorerMelodyMelody, 'melS', 'mel')
    sh.scorer(ScorerMelodyMelody, 'melS', 'melB')

    sh.add(MelodyA('melA'))
    sh['melA'].set_key(key)
    sh.scorer(zScorerMelodyHarm, 'melA', 'func', 8)
    sh.scorer(ScorerMelodySA, 'melA', weight=4)
    sh.scorer(ScorerMelodyMelody, 'melA', 'mel')
    sh.scorer(ScorerMelodyMelody, 'melA', 'melB')
    sh.scorer(ScorerMelodyMelody, 'melA', 'melS')
    sh.scorer(ScorerMelodyMelodyBelow, 'melA', 'melS')

    sh.add(zLyrics('lyr'))
    sh.structurer('struct', 'lyr')
    sh['lyr'].load()
    sh.add(zRhythm('rhy'))
    sh.scorer(ScorerRhythmLyrics, 'rhy', 'lyr')
    sh.scorer(zScorerRhythmMetrics, 'rhy')
    sh.set_key(key)

    print()
    # -------------------------------------------------------

    # print('[yellow]### Gen 1, independent')
    # sh.generate()
    # sh.score()
    # print(sh)

    # -------------------------------------------------------

    print('[yellow]### Generating ')
    sh.reset()
    sh['struct'].gen()
    sh.set_structure()

    l0 = sh['lyr'].gen()
    r0 = sh['rhy'].gen(l0)
    print(r0)

    d0 = sh['func'].gen(r0)
    print("d0", d0)

    m0 = sh['mel'].gen(d0)
    m0 = sh['melB'].gen(d0)
    m0 = sh['melS'].gen(d0)
    m0 = sh['melA'].gen(d0)

    if woo:
        sh.modes = [
            #[('e', 'e-')],
            #[('a', 'a-'), ('g', 'f')],
            #[('f', 'f#'), ('g', 'b-'), ('b', 'b-')],
            #[('f', 'f#'), ('g', 'a'), ('e', 'e-')],
            [],
            #[('a', 'a-'), ('g', 'f')],
            [('f', 'f#'),  ('b', 'b-')],
            [('f', 'f#')],
        ]

    # sh.score()
    print()
    return sh


def sacred(code, f, woo, svg):
    sh = gen_sacred(woo)    

    print('[yellow]### Generated ')
    print(sh)

    sh.export(
        f,
        code + '. ' + gabuzomeu.sentence(woo),
        sh['struct'].structure_full,
        sh['rhy'],
        sh['lyr'],
        ['melS', 'melA', 'mel', 'melB'],
        ['func'],
        random.choice(['3/4', '6/8']),
        svg
        )

if __name__ == '__main__':

    args = parser.parse_args()

    if args.nb:
        nb = args.nb
    else:
        nb = 20 if args.save else 5

    if args.save:
        span = '%03d-%03d/' % (args.save, args.save + nb - 1)

    for i in range(nb):

        if args.save:
            n = args.save + i
            code = '%03d' % n
            f = span + ('woo-' if args.woo else 'sacred-') + code
        else:
            code = 'draft-%02d' % i
            f = code

        print(f'[green]## Experiment {code}')
        sacred(code, f, args.woo, args.svg)