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
from music import Note
import music21
from music21.stream import Part, Score
from rich import print
import argparse
from typing import cast, Tuple, List
import os

# from models.harp import *

from trees import *

def key_from_part(p: Part) -> Tuple[str, str]:
    '''Return key (in interval to C) and mode of a part
    '''
    ks = p.keySignature
    if p.notes[0] != ks.tonic: # first note is always tonic in SH
        ks = ks.relative

    origin = music21.pitch.Pitch('C')
    key = music21.interval.Interval(origin, ks.tonic).simpleName

    return (key, ks.mode)

def grid_from_part(mel: Part) -> Tuple[List[List[str]], List[List[str]]]:
    '''Extract a rhythm and a pitch grid from a part
    Returns nested lists, grouped by bars, of 1. durations and 2. pitches
    '''
    meter: str = mel.timeSignature.ratioString
    rhythm: List[List[str]] = []
    pitches: List[List[str]] = []
    rh_buffer: List[str] = []
    p_buffer: List[str] = []

    for n in mel.notes:
        if n.beat == 1 and len(rh_buffer) > 0:
          rhythm.append(rh_buffer)
          pitches.append(p_buffer)
          rh_buffer = []
          p_buffer = []
        if n.beatStrength >= 0.5:
            rh_buffer.append(str(music.quantize_above(n.duration.quarterLength, meter)))
            p_buffer.append(n.pitch.nameWithOctave)

    if len(rh_buffer) > 0:
        rhythm.append(rh_buffer)
        pitches.append(p_buffer)

    return (rhythm, pitches)

def fill_in_from_part(mel: Part) -> List[List[Note]]:
    '''Extract a sequence of Notes from a Part, grouped by bars
    ''' 
    notes: List[List[Note]] = []
    buffer: List[Note] = []

    for n in mel.notes:
        if n.beat == 1 and len(buffer) > 0:
          notes.append(buffer)
          buffer = []
        buffer.append(Note(n.pitch.nameWithOctave, n.duration.quarterLength))
        
    if len(buffer) > 0:
        notes.append(buffer)

    return notes
    

def load_melody(filename: str) -> Part:
    c: Score = cast(Score, music21.converter.parse(filename))
    mel: Part = c.parts['tenor'].flatten()

    return mel


def harm_sacred(mel: Part, struct: RefinementNode):
    print('[yellow]### Init')

    key, mode = key_from_part(mel)
    print(f'Key: [blue]{key}')

    # determine time signature of melody 
    meter = mel.timeSignature.ratioString
    print(f'Meter: [blue]{meter}')

    sh = ur.Model(key, mode)

    # if mode == 'major':
    #     chords_gen: type = ChordsMajor
    #     melody_s_gen: type = MelodyMajorS
    #     melody_a_gen: type = MelodyMajorA
    #     melody_b_gen: type = MelodyMajorB
    # else:
    #     chords_gen = ChordsMinor
    #     melody_s_gen = MelodyMinorS
    #     melody_a_gen = MelodyMinorA
    #     melody_b_gen = MelodyMinorB

    # if sh.ternary():
    #     rhythm_gen: type = TernaryRhythm
    #     scorer_rhythm_met: type = ScorerRhythmMetricsTernary
    # else:
    #     rhythm_gen = Rhythm
    #     scorer_rhythm_met = ScorerRhythmMetricsFour

    # if sh.ternary():
    #     Lyrics.MIN_LENGTH = 7 # changes class attribute
    # else:
    #     Lyrics.MIN_LENGTH = 5

    # ------------------------------------------------------
    # block scheduling (done implicitly by addition order)

    sh.add(ViewPoint('struct'))
    # sh.add(ViewPoint('lyr'))
    sh.add(ViewPoint('rhy'))
    sh.add(ViewPoint('pitchGridT'))
    sh.add(ViewPoint('fillInT', use_copy=False))
    # sh.add(ViewPoint('chords'), chords_gen)
    # sh.add(ViewPoint('pitchGridB', melody_b_gen))
    # sh.add(ViewPoint('pitchGridS', melody_s_gen))
    # sh.add(ViewPoint('pitchGridA', melody_a_gen))
    # sh.add(ViewPoint('fillInB'))
    # sh.add(ViewPoint('fillInS'))
    # sh.add(ViewPoint('fillInA'))

    # sh.set_key(key)

    # # equip viewpoints with rules
    # sh.add_rule(ScorerFunc, 'chords')

    # sh.add_rule(ScorerMelodyHarmT, 'pitchGridT', 'chords', 2)
    # sh.add_rule(ScorerMelody, 'pitchGridT')
    # sh.add_rule(RelativeScorerSectionMelody, 'pitchGridT', weight=10)
    
    # sh.add_rule(ScorerMelodyHarmB, 'pitchGridB', 'chords', 4)
    # sh.add_rule(ScorerMelodyMelody, 'pitchGridB', 'pitchGridT')
    # sh.add_rule(ScorerMelodyMelodyBelow, 'pitchGridB', 'pitchGridT')

    # sh.add_rule(ScorerMelodyHarmS, 'pitchGridS', 'chords', 4)
    # sh.add_rule(ScorerMelodySA, 'pitchGridS', weight=2)
    # sh.add_rule(ScorerMelodyMelody, 'pitchGridS', 'pitchGrid')
    # sh.add_rule(ScorerMelodyMelody, 'pitchGridS', 'pitchGridB')
    # sh.add_rule(RelativeScorerSectionMelody, 'pitchGridS', weight=10)

    # sh.add_rule(ScorerMelodyHarmA, 'pitchGridA', 'chords', 8)
    # sh.add_rule(ScorerMelodySA, 'pitchGridA', weight=4)
    # sh.add_rule(ScorerMelodyMelody, 'pitchGridA', 'pitchGrid')
    # sh.add_rule(ScorerMelodyMelody, 'pitchGridA', 'pitchGridB')
    # sh.add_rule(ScorerMelodyMelody, 'pitchGridA', 'pitchGridS')
    # sh.add_rule(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGridS', 10)
    # sh.add_rule(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGrid', 10)
    # sh.add_rule(RelativeScorerSectionMelody, 'pitchGridA', weight=10)

    # sh.add_rule(ScorerRhythmLyrics, 'rhy', 'lyr')
    # sh.add_rule(scorer_rhythm_met, 'rhy')

    # # define tatums and which VPs share them
    # # beat, measure
    # # [pitchGridX, rhy, lyr?] (maybe one rhy atom can have several lyr atoms, with at most one stressed ?)

    # define structure inheritance
    # sh.add_link('struct', 'lyr')
    sh.add_link('struct', 'rhy')
    sh.add_link('struct', 'pitchGridT')
    # sh.add_link('rhy', 'pitchGridS')
    # sh.add_link('rhy', 'pitchGridB')
    # sh.add_link('rhy', 'pitchGridA')
    sh.add_link('struct', 'fillInT')
    # sh.add_link('rhy', 'pitchGridS')
    # sh.add_link('rhy', 'pitchGridB')
    # sh.add_link('rhy', 'pitchGridA')
    # sh.add_link('rhy', 'chords')

    # define 

    # fix some viewpoints
    rhythm, pitches = grid_from_part(mel)
    fill_in = fill_in_from_part(mel)
    sh['struct'].set_structure(struct)
    # sh['lyr'].set(lyrics, fixedness=1)
    sh['rhy'].set_to(rhythm)
    sh['pitchGridT'].set_to(pitches)
    sh['fillInT'].set_to(fill_in, fixedness=0.8)

    
    # print()

    # # ------------------------------------------------------------
    # # generation

    # print('[yellow]### Generating ')
    # sh.reset()

    # sh.generate()

    return sh


if __name__ == '__main__':

    path = os.path.join(os.getcwd(), "data/1991-denson/56bd.mxl")
    mel = load_melody(path)
    struc: RefinementNode = \
        RefinementNode(0, 16, "ALL", 
          RefinementNode(0, 8, "A", 
            RefinementNode(0, 4, "A.1",
              RefinementNode(0, 2, "a"),
              RefinementNode(2, 4, "b")),
            RefinementNode(4, 8, "A.2",
              RefinementNode(0, 2, "c"),
              RefinementNode(2, 4, "d"))),
          RefinementNode(8, 16, "B", 
            RefinementNode(0, 4, "B.1",
              RefinementNode(0, 2, "e"),
              RefinementNode(2, 4, "b\'")),
            RefinementNode(4, 8, "B.2",
              RefinementNode(0, 2, "a\'"),
              RefinementNode(0, 2, "f"))))

    harm_sacred(mel, struc)