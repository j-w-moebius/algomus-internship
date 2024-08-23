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


import glob
import random
import music
from music import Note, Pitch, Duration, Chord, Syllable
import music21 as m21
from music21.stream import Part, Score
from rich import print
import argparse
from typing import cast, Tuple, List
import os

import ur
from trees import *
from rulesets.harp import *
from load import *

def gen_sacred() -> ur.Model:
    print('[yellow]### Init')

    key = random.choice(Key.CHOICES)
    mode = random.choice(['minor', 'major'])

    print(f'Key: [blue]{key}')
    print(f'Mode: [blue]{mode}')

    meter = random.choice(['6/4', '4/4', '6/8'])

    print(f'Meter: [blue]{meter}')

    struc: StructureNode = random.choice([struc1, struc2, struc3, struc4])

    print(f'Structure: \n[blue]{struc}')

    sh: ur.Model = ur.Model(key, mode, meter)

    if mode == 'major':
        chords_prod: type = ChordsMajor
        melody_t_prod: type = MelodyMajorT
        melody_s_prod: type = MelodyMajorS
        melody_a_prod: type = MelodyMajorA
        melody_b_prod: type = MelodyMajorB
    else:
        chords_prod = ChordsMinorExtended
        melody_t_prod = MelodyMajorT
        melody_s_prod = MelodyMinorS
        melody_a_prod = MelodyMinorA
        melody_b_prod = MelodyMinorB

    if music.ternary(meter):
        rhythm_prod: type = TernaryRhythm
        scorer_rhythm_met: type = ScorerRhythmMetricsTernary
        min_lyrics: int = 7
    else:
        rhythm_prod = BinaryRhythm
        scorer_rhythm_met = ScorerRhythmMetricsFour
        min_lyrics = 5

    # ------------------------------------------------------
    # viewpoints

    sh.add_vp('rhy', Duration)
    sh.add_vp('lyr', Syllable, before=['rhy'], lead_name='rhy')
    sh.add_vp('chords', Chord, lead_name='rhy', use_copy=False)
    sh.add_vp('pitchGridT', Pitch, lead_name='rhy', use_copy=False)
    sh.add_vp('pitchGridB', Pitch, lead_name='rhy', use_copy=False)
    sh.add_vp('pitchGridS', Pitch, lead_name='rhy', use_copy=False)
    sh.add_vp('pitchGridA', Pitch, lead_name='rhy', use_copy=False)
    sh.add_vp('fillInT', Note, use_copy=False)
    sh.add_vp('fillInB', Note, use_copy=False)
    sh.add_vp('fillInS', Note, use_copy=False)
    sh.add_vp('fillInA', Note, use_copy=False)

    sh.setup()

    # content generation: add producers to viewpoints
    sh.set_structure(struc)

    sh.add_producer(Lyrics(min_lyrics), 'lyr', default=True) 
    sh.add_producer(rhythm_prod(), 'rhy', default=True)
    sh.add_producer(chords_prod(), 'chords', default=True)
    sh.add_producer(melody_t_prod(key), 'pitchGridT', default=True)
    sh.add_producer(melody_b_prod(key), 'pitchGridB', default=True)
    sh.add_producer(melody_s_prod(key), 'pitchGridS', default=True)
    sh.add_producer(melody_a_prod(key), 'pitchGridA', default=True)
    sh.add_producer(FlourisherT(meter), 'fillInT', 'rhy', 'pitchGridT', default=True)
    sh.add_producer(FlourisherB(meter), 'fillInB', 'rhy', 'pitchGridB', default=True)
    sh.add_producer(Flourisher(meter), 'fillInS', 'rhy', 'pitchGridS', default=True)
    sh.add_producer(Flourisher(meter), 'fillInA', 'rhy', 'pitchGridA', default=True)

    # equip viewpoints with evaluators
    sh.add_evaluator(ScorerChords(), 'chords')

    sh.add_evaluator(ScorerMelodyHarm('T'), 'pitchGridT', 'chords', weight=2)
    sh.add_evaluator(ScorerMelody(), 'pitchGridT')

    sh.add_evaluator(ScorerMelodyHarmRoot(), 'pitchGridB', 'chords', weight=4)
    sh.add_evaluator(ScorerMelodyMelody(), 'pitchGridT', 'pitchGridB')
    sh.add_evaluator(ScorerMelodyMelodyBelow(), 'pitchGridT', 'pitchGridB')

    sh.add_evaluator(ScorerMelodyHarm('S'), 'pitchGridS', 'chords', weight=4)
    sh.add_evaluator(ScorerMelodySA(), 'pitchGridS', weight=2)
    sh.add_evaluator(ScorerMelodyMelody(), 'pitchGridS', 'pitchGridT')
    sh.add_evaluator(ScorerMelodyMelody(), 'pitchGridS', 'pitchGridB')

    sh.add_evaluator(ScorerMelodyHarm('A'), 'pitchGridA', 'chords', weight=8)
    sh.add_evaluator(ScorerMelodySA(), 'pitchGridA', weight=4)
    sh.add_evaluator(ScorerMelodyMelody(), 'pitchGridA', 'pitchGridT')
    sh.add_evaluator(ScorerMelodyMelody(), 'pitchGridA', 'pitchGridB')
    sh.add_evaluator(ScorerMelodyMelody(), 'pitchGridS', 'pitchGridA')
    sh.add_evaluator(ScorerMelodyMelodyCross(), 'pitchGridA', 'pitchGridS', weight=10)
    sh.add_evaluator(ScorerMelodyMelodyCross(), 'pitchGridA', 'pitchGridT', weight=10)

    sh.add_evaluator(ScorerRhythmLyrics(), 'rhy', 'lyr')
    sh.add_evaluator(scorer_rhythm_met(), 'rhy')
    
    print()

    # ------------------------------------------------------------
    # generation

    print('[yellow]### Generating ')

    sh.generate()

    return sh


if __name__ == '__main__':

    sh: ur.Model = gen_sacred()
    sh.export('gen', 'SH meets HH', 'lyr', ['fillInS', 'fillInA', 'fillInT', 'fillInB'], ['chords'], False)