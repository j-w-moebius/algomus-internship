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
from rulesets.sh import *

from load import *


def harm_sacred(mel: Part, lyr: List[str], struct: StructureNode) -> ur.Model:
    print('[yellow]### Init')

    key, mode = key_from_part(mel)
    mel.transpose(m21.interval.Interval(key).reverse(), inPlace=True)

    print(f'Key: [blue]{key}')

    # determine time signature of melody 
    meter = mel.timeSignature.ratioString
    print(f'Meter: [blue]{meter}')

    sh: ur.Model = ur.Model(key, mode, meter)

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

    sh.add_producer(ChordsMinor(), 'chords', default=True)
    sh.add_producer(MelodyMinorB(key), 'pitchGridB', default=True)
    sh.add_producer(MelodyMinorS(key), 'pitchGridS', default=True)
    sh.add_producer(MelodyMinorA(key), 'pitchGridA', default=True)
    sh.add_producer(CadenceChords(mode), 'chords', fixedness=0.9)
    sh.add_producer(CadencePitches(mode, 'B'), 'pitchGridB', fixedness=0.9)
    sh.add_producer(CadencePitches(mode, 'S'), 'pitchGridS', fixedness=0.9) 
    sh.add_producer(CadencePitches(mode, 'A'), 'pitchGridA', fixedness=0.9)
    sh.add_producer(Flourisher(), 'fillInB', 'rhy', 'pitchGridB', default=True)
    sh.add_producer(Flourisher(), 'fillInS', 'rhy', 'pitchGridS', default=True)
    sh.add_producer(Flourisher(), 'fillInA', 'rhy', 'pitchGridA', default=True)

    # equip viewpoints with evaluators
    sh.add_evaluator(ScorerChords(), 'chords')
    sh.add_evaluator(MelodyHarm(), 'pitchGridT', 'chords')
    sh.add_evaluator(MelodyHarm(), 'pitchGridB', 'chords')
    sh.add_evaluator(MelodyHarm(), 'pitchGridS', 'chords')
    sh.add_evaluator(MelodyHarm(), 'pitchGridA', 'chords')
    
    print()

    # ------------------------------------------------------------
    # generation

    print('[yellow]### Generating ')

    sh.generate()

    return sh


if __name__ == '__main__':

    mel_path: str = os.path.join(os.getcwd(), "data/1991-denson/56bd.mxl")
    lyr_path: str = os.path.join(os.getcwd(), "data/lyrics/56b_Villulia.txt")
    mel: Part = load_melody(mel_path)
    lyr: List[str] = [s for v in load_lyrics(lyr_path, STRESS_WORDS) for s in v] # flatten

    sh: ur.Model = harm_sacred(mel, lyr, struc)

    sh.export('test','Villulia reharmonized', 'lyr', ['fillInS', 'fillInA', 'fillInT', 'fillInB'], ['chords'], False)