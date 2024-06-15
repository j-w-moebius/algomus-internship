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

from trees import RefinementNode

parser = argparse.ArgumentParser(description = 'Fake Sacred Harp')
parser.add_argument('--save', '-s', type=int, default=0, help='starting number to save generation, otherwise draft generations')
parser.add_argument('--nb', '-n', type=int, default=0, help='number of generations with --save')
parser.add_argument('--svg', action='store_true', help='generate and opens .svg (requires Verovio and Firefox)')
parser.add_argument('--woo', action='store_true', help='experiment')
parser.add_argument('--hh', action='store_true', help="Holly's lyrics")

def key_from_part(p: Part) -> (str, str):
    '''Return key (in interval to C) and mode of a part
    '''
    ks = p.keySignature
    if p.notes[0] != ks.tonic: # first note is always tonic in SH
        ks = ks.relative

    origin = music21.pitch.Pitch('C')
    key = music21.interval.Interval(origin, ks.tonic).simpleName

    return (key, ks.mode)

def harm_sacred(mel: Part, structure: RefinementNode):
    print('[yellow]### Init')
    
    sh = ur.Model()

    sh.key, sh.mode = key_from_part(mel) # or: random choices
    print(f'Key: [blue]{key}')

    # determine time signature of melody 
    sh.meter = mel.timeSignature.ratioString # or: random choice
    print(f'Meter: [blue]{sh.meter}')

    if mode == 'major':
        chords_gen = ChordsMajor
        melody_s_gen = MelodyMajorS
        melody_a_gen = MelodyMajorA
        melody_b_gen = MelodyMajorB
    else:
        chords_gen = ChordsMinor
        melody_s_gen = MelodyMinorS
        melody_a_gen = MelodyMinorA
        melody_b_gen = MelodyMinorB

    if sh.ternary():
        rhythm_gen = TernaryRhythm
        scorer_rhythm_met = ScorerRhythmMetricsTernary
    else:
        rhythm_gen = Rhythm
        scorer_rhythm_met = ScorerRhythmMetricsFour

    if sh.ternary():
        Lyrics.MIN_LENGTH = 7 # changes class attribute
    else:
        Lyrics.MIN_LENGTH = 5

    # ------------------------------------------------------
    # block scheduling (done implicitly by addition order)

    sh.add(StructureVP('struct'))
    sh.add(ViewPoint('lyr'))
    sh.add(ViewPoint('rhy'))
    sh.add(ViewPoint('pitchGridT'))
    sh.add(ViewPoint('fillInT'))
    sh.add(ViewPoint('chords'), chords_gen)
    sh.add(ViewPoint('pitchGridB', melody_b_gen))
    sh.add(ViewPoint('pitchGridS', melody_s_gen))
    sh.add(ViewPoint('pitchGridA', melody_a_gen))
    sh.add(ViewPoint('fillInB'))
    sh.add(ViewPoint('fillInS'))
    sh.add(ViewPoint('fillInA'))

    sh.set_key(key)

    # equip viewpoints with rules
    sh.add_rule(ScorerFunc, 'chords')

    sh.add_rule(ScorerMelodyHarmT, 'pitchGridT', 'chords', 2)
    sh.add_rule(ScorerMelody, 'pitchGridT')
    sh.add_rule(RelativeScorerSectionMelody, 'pitchGridT', weight=10)
    
    sh.add_rule(ScorerMelodyHarmB, 'pitchGridB', 'chords', 4)
    sh.add_rule(ScorerMelodyMelody, 'pitchGridB', 'pitchGridT')
    sh.add_rule(ScorerMelodyMelodyBelow, 'pitchGridB', 'pitchGridT')

    sh.add_rule(ScorerMelodyHarmS, 'pitchGridS', 'chords', 4)
    sh.add_rule(ScorerMelodySA, 'pitchGridS', weight=2)
    sh.add_rule(ScorerMelodyMelody, 'pitchGridS', 'pitchGrid')
    sh.add_rule(ScorerMelodyMelody, 'pitchGridS', 'pitchGridB')
    sh.add_rule(RelativeScorerSectionMelody, 'pitchGridS', weight=10)

    sh.add_rule(ScorerMelodyHarmA, 'pitchGridA', 'chords', 8)
    sh.add_rule(ScorerMelodySA, 'pitchGridA', weight=4)
    sh.add_rule(ScorerMelodyMelody, 'pitchGridA', 'pitchGrid')
    sh.add_rule(ScorerMelodyMelody, 'pitchGridA', 'pitchGridB')
    sh.add_rule(ScorerMelodyMelody, 'pitchGridA', 'pitchGridS')
    sh.add_rule(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGridS', 10)
    sh.add_rule(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGrid', 10)
    sh.add_rule(RelativeScorerSectionMelody, 'pitchGridA', weight=10)

    sh.add_rule(ScorerRhythmLyrics, 'rhy', 'lyr')
    sh.add_rule(scorer_rhythm_met, 'rhy')

    # define tatums and which VPs share them
    # beat, measure
    # [pitchGridX, rhy, lyr?] (maybe one rhy atom can have several lyr atoms, with at most one stressed ?)

    # define structure inheritance
    sh.add_link('struct', 'lyr')
    sh.add_link('lyr', 'rhy')
    sh.add_link('rhy', 'pitchGridT')
    sh.add_link('rhy', 'pitchGridS')
    sh.add_link('rhy', 'pitchGridB')
    sh.add_link('rhy', 'pitchGridA')
    sh.add_link('rhy', 'chords')
    
    print()

    # ------------------------------------------------------------
    # generation

    print('[yellow]### Generating ')
    sh.reset()
    sh['struct'].set(structure)

    sh['lyr'].set(lyrics, fixedness=1)
    sh['rhy'].set(rhythm, fixedness=1)
    sh['pitchGridT'].set(melGrid, fixedness=1)
    sh['fillInT'].set(mel, fixedness=1)
    
    sh.generate(start_at='chords')

    return sh


def sacred(code, f, woo, hh, svg):
    sh = gen_sacred(woo, hh)

    print('[yellow]### Generated ')
    print(sh)

    if hh:
        title = sh['lyr'].gens['Z'][0].one
        title = ' '.join(title).replace(' -', '').replace('>', '').replace('/', '').replace('.', '').replace(',', '').replace(';','')
    else:
        title = gabuzomeu.sentence(woo)

    sh.export(
        f,
        f"{code}. {title} ({sh['struct'].structure})",
        sh['struct'].structure_full,
        sh['rhy'],
        sh['lyr'],
        ['pitchGridS', 'pitchGridA', 'pitchGrid', 'pitchGridB'],
        ['chords'],
        svg
        )
 
import music21
from music21.stream import Part, Score
import os
from typing import cast
from vp import ViewPoint

def grid_from_part(mel: Part) -> (list[str], list[str]):

    resolution: music21.duration.Duration
    meter_denom: str = mel.timeSignature.denominator
    rhythm = []
    pitches = []
    for n in mel.notes:
        if n.beatStrength >= 0.5:
            rhythm.append(n.duration rounded to cutoff)

def fillin_from_part(mel: Part, cutoff: music21) -> list[Note]:
    

def load_melody(filename: str) -> Part:
    c: Score = cast(Score, music21.converter.parse(filename))
    mel: Part = c.parts.get('tenor').flatten()

    return mel

if __name__ == '__main__':

    #sacred("", "", False, False, True)
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
            RefinementNode(8, 12, "B.1",
              RefinementNode(8, 10, "e"),
              RefinementNode(10, 12, "b\'")),
            RefinementNode(12, 16, "B.2",
              RefinementNode(12, 14, "a\'"),
              RefinementNode(14, 16, "f"))))
    struc.export_to_dot("test.dot")
    harm_sacred(mel, struc)