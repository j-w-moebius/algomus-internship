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
parser.add_argument('--hh', action='store_true', help="Holly's lyrics")

def harm_sacred(mel: music21.stream.Part):
    print('[yellow]### Init')

    # determine key of melody
    ks = mel.keySignature
    if mel.notes[0] != ks.tonic: # first note is always tonic
        ks = ks.relative

    origin = music21.pitch.Pitch('C')
    key = music21.interval.Interval(origin, ks.tonic).simpleName # or: random choice

    print(f'Key: [blue]{key}')
    mode = ks.mode

    sh = ur.Model()

    # determine time signature of melody 
    sh.meter = mel.timeSignature.ratioString # or: random choice
    print(f'Meter: [blue]{sh.meter}')

    if mode == 'major':
        chords_gen = ChordsMajor
        melody_s_gen = MelodyMajorS
        melody_a_gen = MelodyMajorA
        melody_t_gen = MelodyMajorT
        melody_b_gen = MelodyMajorB
    else:
        chords_gen = ChordsMinor
        melody_s_gen = MelodyMinorS
        melody_a_gen = MelodyMinorA
        melody_t_gen = MelodyMinorT
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
    sh['pitchGridT'].set_key(key) # replace by central call on sh
    
    sh.add(ViewPoint('fillInT'))

    sh.add(ViewPoint('chords'))
    # sh.scorer(ScorerFunc, 'func')
    # sh.structurer('struct', 'func')

    #sh.scorer(zScorerMelodyHarmT, 'mel', 'func', 2)
    #sh.scorer(ScorerMelody, 'mel')

    #sh.scorer(RelativeScorerSectionMelody, 'mel', weight=10)

    sh.add(ViewPoint('pitchGridB', melody_b_gen))

    #sh.scorer(zScorerMelodyHarmB, 'pitchGridB', 'func', 4)

    #sh.scorer(ScorerMelodyMelody, 'pitchGridB', 'pitchGridT')
    #sh.scorer(ScorerMelodyMelodyBelow, 'pitchGridB', 'pitchGridT')

    sh.add(ViewPoint('pitchGridS'), melody_s_gen)
    # sh.scorer(zScorerMelodyHarmS, 'pitchGridS', 'func', 4)
    # sh.scorer(ScorerMelodySA, 'pitchGridS', weight=2)
    # sh.scorer(ScorerMelodyMelody, 'pitchGridS', 'pitchGrid')
    # sh.scorer(ScorerMelodyMelody, 'pitchGridS', 'pitchGridB')
    # sh.scorer(RelativeScorerSectionMelody, 'pitchGridS', weight=10)

    sh.add(ViewPoint('pitchGridA'), melody_a_gen)
    # sh.scorer(zScorerMelodyHarmA, 'pitchGridA', 'func', 8)
    # sh.scorer(ScorerMelodySA, 'pitchGridA', weight=4)
    # sh.scorer(ScorerMelodyMelody, 'pitchGridA', 'pitchGrid')
    # sh.scorer(ScorerMelodyMelody, 'pitchGridA', 'pitchGridB')
    # sh.scorer(ScorerMelodyMelody, 'pitchGridA', 'pitchGridS')
    # sh.scorer(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGridS', 10)
    # sh.scorer(ScorerMelodyMelodyCross, 'pitchGridA', 'pitchGrid', 10)
    # sh.scorer(RelativeScorerSectionMelody, 'pitchGridA', weight=10)

    sh.add(ViewPoint('fillInB'))
    sh.add(ViewPoint('fillInS'))
    sh.add(ViewPoint('fillInA'))

    # sh.structurer('struct', 'lyr')
    #sh['lyr'].load()
    #sh.scorer(ScorerRhythmLyrics, 'rhy', 'lyr')
    #sh.scorer(zScorerRhythmMetrics, 'rhy')
    sh.set_key(key)

    # define tatums and which VPs share them
    # beat, measure
    # [pitchGridX, rhy, lyr]

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
    sh['struct'].set()
    # sh.set_structure()

    r0 = sh['rhy'].gen(common=True)
    print(r0)

    d0 = sh['func'].gen(r0)
    print("d0", d0)

    m0 = sh['pitchGrid'].gen(d0)
    m0 = sh['pitchGridB'].gen(d0)
    m0 = sh['pitchGridS'].gen(d0)
    m0 = sh['pitchGridA'].gen(d0)

    print()
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
        ['func'],
        svg
        )

import music21
import os

def extract_grid(mel: music21.stream.Part, cutoff: music21, struc: StrucTree) -> StrucTree((Rhythm, Pitch)):
    return (null, null)
    

def load_melody(filename: str) -> music21.stream.Part:
    c = music21.converter.parse(filename)

    mel = c.parts['tenor'].flatten()

    text = music21.text.assembleLyrics(mel)

    return mel

if __name__ == '__main__':

    #sacred("", "", False, False, True)
    path = os.path.join(os.getcwd(), "data/1991-denson/56bd.mxl")
    mel = load_melody(path)
    harm_sacred(mel)