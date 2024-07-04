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
import gabuzomeu
import random
import music
from music import Note, Pitch, Duration, Chord, Syllable, Schema
import music21 as m21
from music21.stream import Part, Score
from rich import print
import argparse
from typing import cast, Tuple, List
import os

import ur
from trees import *
from models.harp import *
from load import *

from anytree import LevelOrderIter

def set_lyrics(vp: ViewPoint, lyr: List[List[Syllable]]) -> None:
    vp.generated = True
    verse_iter = iter(lyr)
    verse: List[Syllable] = next(verse_iter)
    verse_len: int = len(verse)

    # divide syllables in verse approximately unifmorly among motifs
    # for now: assume that level(motif) = level(phrase)+ 1
    for n in LevelOrderIter(vp.root, lambda n: n.is_leaf):

        motifs: int = len(n.siblings) + 1

        if len(verse) == 0:
            verse = next(verse_iter)
            verse_len = len(verse)
        
        new_syls: int = min(math.ceil(verse_len / motifs), len(verse))
        n.set_to(verse[:new_syls], 1.0)
        verse = verse[new_syls:]


def gen_sacred(lyr_path: str, struct: StructureNode) -> ur.Model:
    print('[yellow]### Init')

    key = random.choice(Key.CHOICES)
    mode = random.choice(['minor', 'major'])

    print(f'Key: [blue]{key}')

    meter = random.choice(['3/4'])

    print(f'Meter: [blue]{meter}')

    sh: ur.Model = ur.Model(key, mode, meter)

    # lyr_path = random.choice(...) # (among suitable songs)
    lyr = load_lyrics(lyr_path, STRESS_WORDS)

    # TODO simplify
    if mode == 'major':
        chords_prod: type = ChordsMajor
        melody_s_prod: type = MelodyMajorS
        melody_a_prod: type = MelodyMajorA
        melody_t_prod: type = MelodyMajorT
        melody_b_prod: type = MelodyMajorB
    else:
        chords_prod = ChordsMinor
        melody_s_prod = MelodyMinorS
        melody_a_prod = MelodyMinorA
        melody_t_prod = MelodyMinorT
        melody_b_prod = MelodyMinorB

    # if sh.ternary():
        # rhythm_prod: type = TernaryRhythm
        # scorer_rhythm_met: type = ScorerRhythmMetricsTernary
    # else:
        # rhythm_prod = Rhythm
        # scorer_rhythm_met = ScorerRhythmMetricsFour

    # if sh.ternary():
    #     Lyrics.MIN_LENGTH = 7 # changes class attribute
    # else:
    #     Lyrics.MIN_LENGTH = 5

    # ------------------------------------------------------
    # block scheduling

    sh.add_vp('rhy', Duration)
    sh.add_vp('lyr', Syllable, before=['rhy'], lead_name='rhy', use_copy=False)
    sh.add_vp('schemata', Schema, lead_name='rhy', gapless=False)
    sh.add_vp('chords', Chord, lead_name='rhy')
    sh.add_vp('pitchGridT', Pitch, lead_name='rhy')
    sh.add_vp('fillInT', Pitch, use_copy=False)
    sh.add_vp('pitchGridB', Pitch, lead_name='rhy')
    sh.add_vp('pitchGridS', Pitch, lead_name='rhy')
    sh.add_vp('pitchGridA', Pitch, lead_name='rhy')
    sh.add_vp('fillInB', Note, use_copy=False)
    sh.add_vp('fillInS', Note, use_copy=False)
    sh.add_vp('fillInA', Note, use_copy=False)

    sh.setup()

    # content generation: add producers to viewpoints
    sh.set_structure(struct)
    set_lyrics(sh['lyr'], lyr)

    sh.add_producer(Rhythm(meter), 'rhy', default=True)
    sh.add_producer(chords_prod(), 'chords', default=True)
    sh.add_producer(melody_t_prod(key), 'pitchGridT', default=True)
    sh.add_producer(melody_b_prod(key), 'pitchGridB', default=True)
    sh.add_producer(melody_s_prod(key), 'pitchGridS', default=True)
    sh.add_producer(melody_a_prod(key), 'pitchGridA', default=True)
    sh.add_producer(Cadences(), 'schemata', fixedness=1.0)
    sh.add_producer(CadenceChords(mode), 'chords', 'schemata', fixedness=0.9)
    sh.add_producer(CadencePitches(mode, 'T'), 'pitchGridT', 'schemata', fixedness=0.9)
    sh.add_producer(CadencePitches(mode, 'B'), 'pitchGridB', 'schemata', fixedness=0.9)
    sh.add_producer(CadencePitches(mode, 'S'), 'pitchGridS', 'schemata', fixedness=0.9) 
    sh.add_producer(CadencePitches(mode, 'A'), 'pitchGridA', 'schemata', fixedness=0.9)
    sh.add_producer(Flourisher(), 'fillInT', 'rhy', 'pitchGridT', 'schemata', default=True)
    sh.add_producer(Flourisher(), 'fillInB', 'rhy', 'pitchGridB', 'schemata', default=True)
    sh.add_producer(Flourisher(), 'fillInS', 'rhy', 'pitchGridS', 'schemata', default=True)
    sh.add_producer(Flourisher(), 'fillInA', 'rhy', 'pitchGridA', 'schemata', default=True)

    # equip viewpoints with evaluators
    sh.add_evaluator(ScorerFunc(), 'chords')

    sh.add_evaluator(MelodyHarm('T'), 'pitchGridT', 'chords')

    sh.add_evaluator(MelodyHarm('B'), 'pitchGridB', 'chords')
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridB', 'pitchGridT')
    # sh.add_evaluator(ScorerMelodyMelodyBelow, 'pitchGridB', 'pitchGridT')

    sh.add_evaluator(MelodyHarm('S'), 'pitchGridS', 'chords')
    # sh.add_evaluator(ScorerMelodySA, 'pitchGridS', weight=2)
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridS', 'pitchGrid')
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridS', 'pitchGridB')
    # sh.add_evaluator(RelativeScorerSectionMelody, 'pitchGridS', weight=10)

    sh.add_evaluator(MelodyHarm('A'), 'pitchGridA', 'chords')
    # sh.add_evaluator(ScorerMelodySA, 'pitchGridA', weight=4)
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridA', 'pitchGrid')
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridA', 'pitchGridB')
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridA', 'pitchGridS')
    # sh.add_evaluator(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGridS', 10)
    # sh.add_evaluator(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGrid', 10)
    # sh.add_evaluator(RelativeScorerSectionMelody, 'pitchGridA', weight=10)

    sh.add_evaluator(ScorerRhythmLyrics(meter), 'rhy', 'lyr')
    # sh.add_evaluator(scorer_rhythm_met, 'rhy')
    
    print()

    # ------------------------------------------------------------
    # generation

    print('[yellow]### Generating ')

    sh.generate()

    return sh


if __name__ == '__main__':

    lyr_path: str = os.path.join(os.getcwd(), "data/lyrics/56b_Villulia.txt")

    struc: StructureNode = \
        StructureNode(0.0, 48.0, "ALL", [
            StructureNode(0.0, 24.0, "A", [
                StructureNode(0.0, 12.0, "A.1", [
                    StructureNode(0.0, 6.0, "a"),
                    StructureNode(6.0, 12.0, "b")
                ]),
                StructureNode(12.0, 24.0, "A.2", [
                    StructureNode(0.0, 6.0, "c"),
                    StructureNode(6.0, 12.0, "d")
                ])
            ]),
            StructureNode(24.0, 48.0, "B", [
                StructureNode(0.0, 12.0, "B.1", [
                    StructureNode(0.0, 6.0, "e"),
                    StructureNode(6.0, 12.0, "b\'")
                ]),
                StructureNode(12.0, 24.0, "B.2", [
                    StructureNode(0.0, 6.0, "a\'"),
                    StructureNode(6.0, 12.0, "f")
                ])
            ])
        ])

    sh: ur.Model = gen_sacred(lyr_path, struc)

    sh.export('test','Villulia recomposed', 'lyr', ['fillInS', 'fillInA', 'fillInT', 'fillInB'], ['chords'], False)