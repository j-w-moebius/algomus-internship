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
from music import Note, Pitch, Duration, Chord, Syllable
import music21 as m21
from music21.stream import Part, Score
from rich import print
import argparse
from typing import cast, Tuple, List
import os

import ur
from trees import *
from models.harp import *

def key_from_part(p: Part) -> Tuple[str, str]:
    '''Return key (in interval to C) and mode of a part
    '''
    ks = p.keySignature
    origin = m21.pitch.Pitch('C')
    if p.notes[0] != ks.tonic: # first note is always tonic in SH
        ks = ks.relative # we're in minor mode
        origin = m21.pitch.Pitch('A')

    key = m21.interval.Interval(origin, ks.tonic).directedSimpleName

    return (key, ks.mode)

def grid_from_part(mel: Part) -> Tuple[List[Duration], List[Pitch]]:
    '''Extract a rhythm and a pitch grid from a part
    Returns lists of 1. durations and 2. pitches
    '''
    meter: str = mel.timeSignature.ratioString
    rhythm: List[Duration] = []
    pitches: List[Pitch] = []

    for n in mel.notes:
        if n.beatStrength >= 0.5:
            rhythm.append(Duration(music.quantize_above(n.duration.quarterLength, meter)))
            pitches.append(Pitch(n.pitch.nameWithOctave))

    return (rhythm, pitches)

def fill_in_from_part(mel: Part) -> List[Note]:
    '''Extract a sequence of Notes from a Part, grouped by bars
    ''' 
    notes: List[Note] = []

    for n in mel.notes:
        notes.append(Note(n.duration.quarterLength, n.pitch.nameWithOctave))
        
    return notes

def load_lyrics(file: str) -> List[str]:
    '''Load first stanza  from file
    '''
    syllables: List[str] = []
    for l in open(file, encoding='utf-8').readlines(): 
        if l == '\n':
            break # only load first stanza
        text: str = l.replace('-', ' -').strip() + '/'
        for s in text.split():
            # for ww in self.STRESS_WORDS:
            #     if ww in s:
            #         s = '!' + s
            syllables += [s]
    return syllables

def load_melody(filename: str) -> Part:
    c: Score = cast(Score, m21.converter.parse(filename))
    mel: Part = c.parts['tenor'].flatten()
    tonic_interval, _ = key_from_part(mel)

    if mel.clef == m21.clef.TrebleClef():
        mel = mel.transpose("P-8")

    return mel


def harm_sacred(mel: Part, lyr: List[str], struct: StructureNode) -> ur.Model:
    print('[yellow]### Init')

    key, mode = key_from_part(mel)
    mel.transpose(m21.interval.Interval(key).reverse(), inPlace=True)

    print(f'Key: [blue]{key}')

    # determine time signature of melody 
    meter = mel.timeSignature.ratioString
    print(f'Meter: [blue]{meter}')

    sh: ur.Model = ur.Model(key, mode, meter)

    if mode == 'major':
        chords_prod: type = ChordsMajor
        melody_s_prod: type = MelodyMajorS
        melody_a_prod: type = MelodyMajorA
        melody_b_prod: type = MelodyMajorB
    else:
        chords_prod = ChordsMinor
        melody_s_prod = MelodyMinorS
        melody_a_prod = MelodyMinorA
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
    sh.add_vp('lyr', Syllable, lead_name='rhy', use_copy=False)
    sh.add_vp('pitchGridT', Pitch, lead_name='rhy')
    sh.add_vp('fillInT', Pitch, use_copy=False)
    sh.add_vp('chords', Chord, lead_name='rhy')
    sh.add_vp('pitchGridB', Pitch, lead_name='rhy')
    sh.add_vp('pitchGridS', Pitch, lead_name='rhy')
    sh.add_vp('pitchGridA', Pitch, lead_name='rhy')
    sh.add_vp('fillInB', Note, use_copy=False)
    sh.add_vp('fillInS', Note, use_copy=False)
    sh.add_vp('fillInA', Note, use_copy=False)

    sh.setup()
    
    rhythm, pitches = grid_from_part(mel)
    fill_in = fill_in_from_part(mel)

    # content generation: fix some vps, add producers to others
    sh.set_structure(struc)
    sh['rhy'].initialize_to(rhythm)
    sh['lyr'].initialize_to(lyr)
    sh['pitchGridT'].initialize_to(pitches)
    sh['fillInT'].initialize_to(fill_in, fixedness=0.8)

    sh.add_producer(chords_prod, 'chords')
    sh.add_producer(melody_b_prod, 'pitchGridB')
    sh.add_producer(melody_s_prod, 'pitchGridS')
    sh.add_producer(melody_a_prod, 'pitchGridA')
    sh.add_producer(Flourisher, 'fillInB', 'rhy', 'pitchGridB')
    sh.add_producer(Flourisher, 'fillInS', 'rhy', 'pitchGridS')
    sh.add_producer(Flourisher, 'fillInA', 'rhy', 'pitchGridA')

    # equip viewpoints with evaluators
    sh.add_evaluator(ScorerFunc, 'chords')

    sh.add_evaluator(ScorerMelodyHarmT, 'pitchGridT', 'chords', weight=4)

    sh.add_evaluator(ScorerMelodyHarmB, 'pitchGridB', 'chords', weight=4)
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridB', 'pitchGridT')
    # sh.add_evaluator(ScorerMelodyMelodyBelow, 'pitchGridB', 'pitchGridT')

    sh.add_evaluator(ScorerMelodyHarmS, 'pitchGridS', 'chords', weight=4)
    # sh.add_evaluator(ScorerMelodySA, 'pitchGridS', weight=2)
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridS', 'pitchGrid')
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridS', 'pitchGridB')
    # sh.add_evaluator(RelativeScorerSectionMelody, 'pitchGridS', weight=10)

    sh.add_evaluator(ScorerMelodyHarmA, 'pitchGridA', 'chords', weight=8)
    # sh.add_evaluator(ScorerMelodySA, 'pitchGridA', weight=4)
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridA', 'pitchGrid')
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridA', 'pitchGridB')
    # sh.add_evaluator(ScorerMelodyMelody, 'pitchGridA', 'pitchGridS')
    # sh.add_evaluator(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGridS', 10)
    # sh.add_evaluator(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGrid', 10)
    # sh.add_evaluator(RelativeScorerSectionMelody, 'pitchGridA', weight=10)

    # sh.add_evaluator(ScorerRhythmLyrics, 'rhy', 'lyr')
    # sh.add_evaluator(scorer_rhythm_met, 'rhy')

    # test = sh['pitchGridT']['B'][0.0:4.0]

    
    print()

    # ------------------------------------------------------------
    # generation

    print('[yellow]### Generating ')
    # sh.reset()

    n = sh['pitchGridT'].root

    test = n.get_subrange(Index(4.0, 3, n), Index(8.0, 5, n))
    test2 = n.get_subrange(Index(44.0, 28, n), Index(48.0, 30, n))
    print(sh['pitchGridT'])

    sh.generate()

    return sh


if __name__ == '__main__':

    mel_path: str = os.path.join(os.getcwd(), "data/1991-denson/56bd.mxl")
    lyr_path: str = os.path.join(os.getcwd(), "data/lyrics/56b_Villulia.txt")
    mel: Part = load_melody(mel_path)
    lyr: List[str] = load_lyrics(lyr_path)

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

    sh: ur.Model = harm_sacred(mel, lyr, struc)

    sh.export('test','Villulia reharmonized', 'lyr', ['fillInS', 'fillInA', 'fillInT', 'fillInB'], ['chords'], False)