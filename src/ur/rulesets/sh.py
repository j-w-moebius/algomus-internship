'''
A simple homophonic model, inspired by Sacred Harp corpus
and by (Kelley 2016) models.
'''

import ur
import glob
import music as m
import math
import tools
from typing import Optional, List, Dict, Tuple
from collections import defaultdict
import random
from trees import StructureNode

import nonchord

VOICE_POSITIONS: Dict[str, int] = {
    'B': 0,
    'T': 1,
    'A': 2,
    'S': 3
}

STRESS_WORDS: List[str] = ['Lord', 'God', 'Christ', 'Son']

# structure tree for 'Villulia'
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

STRUCTURE_LEVELS: Dict[str, int] = {
    'piece': 0,
    'section': 1,
    'phrase': 2,
    'motif': 3
}

class Key:
    """
    Possible key choices, expressed as transposition interval w.r.t. C
    """
    CHOICES = ['P-4', 'm-3', 'M-2', 'P1', 'M2', 'm3', 'P4']

class ChordsMinor(ur.HiddenMarkov[m.Chord]):

    SOURCE = '(Kelley 2016)'

    STATES = ['T', 'S', 'D']
    INITIAL = ['T']

    TRANSITIONS = {
        'T': { 'T': 0.53, 'S': 0.08, 'D': 0.39 },
        'S': { 'T': 0.31, 'S': 0.14, 'D': 0.55 },
        'D': { 'T': 0.49, 'S': 0.08, 'D': 0.43 },
    }

    EMISSIONS: Dict[str, defaultdict[m.Chord, float]] = {
        'T': defaultdict(float,{'i': 1.00}),
        'S': defaultdict(float, {'iim': 0.19, 'iv': 0.53, 'VI': 0.28}),
        'D': defaultdict(float, {'III': 0.35, 'v': 0.32, 'VII': 0.33}),
    }

class MelodyMinorS(ur.PitchMarkov):
    AMBITUS = ('C4', 'A5')
    AMBITUS_INITIAL = ('E4', 'E5')
    STATES = ['E4', 'A4', 'B4', 'C5', 'G4', 'F4', 'D5', 'E5', 'G5', 'F5', 'A5', 'F#5', 'E-5', 'B-4', 'B-5', 'D4', 'C4']
    INITIAL = ['E4', 'A4', 'C5', 'E5']
    FINAL = STATES

    TRANSITIONS = defaultdict(lambda: defaultdict(float), {
        'E4': defaultdict(float, {'A4': 0.214, 'B4': 0.190, 'C5': 0.095, 'D4': 0.238, 'E4': 0.119, 'E5': 0.048, 'F4': 0.071, 'G4': 0.024}),
        'A4': defaultdict(float, {'A4': 0.129, 'B-4': 0.059, 'B4': 0.294, 'C5': 0.094, 'D5': 0.024, 'E4': 0.059, 'E5': 0.035, 'F4': 0.024, 'G4': 0.282}),
        'B4': defaultdict(float, {'A4': 0.329, 'B4': 0.106, 'C5': 0.412, 'D5': 0.024, 'E4': 0.059, 'G4': 0.071}),
        'C5': defaultdict(float, {'A4': 0.079, 'B-4': 0.108, 'B4': 0.259, 'C5': 0.158, 'D5': 0.295, 'E-5': 0.007, 'E5': 0.022, 'F5': 0.029, 'G4': 0.036, 'G5': 0.007}),
        'G4': defaultdict(float, {'A4': 0.333, 'B-4': 0.033, 'B4': 0.067, 'C5': 0.017, 'D5': 0.033, 'E4': 0.067, 'F4': 0.200, 'G4': 0.250}),
        'F4': defaultdict(float, {'E4': 0.714, 'F4': 0.190, 'G4': 0.095}),
        'D5': defaultdict(float, {'B-4': 0.070, 'B4': 0.008, 'C5': 0.295, 'D5': 0.318, 'E-5': 0.093, 'E5': 0.124, 'F#5': 0.016, 'F5': 0.031, 'G4': 0.016, 'G5': 0.031}),
        'E5': defaultdict(float, {'A4': 0.028, 'A5': 0.042, 'C5': 0.167, 'D5': 0.125, 'E4': 0.014, 'E5': 0.458, 'F5': 0.083, 'G5': 0.083}),
        'G5': defaultdict(float, {'A5': 0.087, 'B-5': 0.043, 'C5': 0.043, 'E5': 0.174, 'F#5': 0.087, 'F5': 0.391, 'G5': 0.174}),
        'F5': defaultdict(float, {'B-4': 0.061, 'C5': 0.030, 'D5': 0.242, 'E-5': 0.061, 'E5': 0.273, 'F5': 0.242, 'G5': 0.091}),
        'A5': defaultdict(float, {'D5': 0.167, 'E5': 0.333, 'G5': 0.500}),
        'F#5': defaultdict(float, {'D5': 0.500, 'G5': 0.500}),
        'E-5': defaultdict(float, {'C5': 0.190, 'D5': 0.571, 'E-5': 0.143, 'F5': 0.095}),
        'B-4': defaultdict(float, {'A4': 0.106, 'B-4': 0.277, 'C5': 0.234, 'D5': 0.298, 'E-5': 0.064, 'G4': 0.021}),
        'B-5': defaultdict(float, {'A5': 1.000}),
        'D4': defaultdict(float, {'C4': 0.100, 'E4': 0.500, 'G4': 0.400}),
        'C4': defaultdict(float, {'C4': 1.000}),
    })

class MelodyMinorA(ur.PitchMarkov):
    AMBITUS = ('G3', 'D5')
    AMBITUS_INITIAL = ('A3', 'C5')
    STATES = ['E4', 'A4', 'F4', 'G4', 'D4', 'B4', 'C5', 'D5', 'A-4', 'F#4', 'E5', 'B-4', 'E-4', 'G#4', 'G5', 'F5', 'C4', 'B3', 'C#4']
    INITIAL = ['C4', 'E4', 'A4', 'C5']
    FINAL = STATES

    TRANSITIONS = defaultdict(lambda: defaultdict(float), {
        'E4': defaultdict(float, {'A-4': 0.010, 'A4': 0.060, 'C5': 0.010, 'D4': 0.150, 'E4': 0.570, 'F#4': 0.020, 'F4': 0.060, 'G#4': 0.070, 'G4': 0.050}),
        'A4': defaultdict(float, {'A-4': 0.033, 'A4': 0.346, 'B-4': 0.052, 'B4': 0.105, 'C5': 0.085, 'E4': 0.111, 'F4': 0.046, 'G4': 0.222}),
        'F4': defaultdict(float, {'A4': 0.071, 'C5': 0.018, 'D4': 0.089, 'E-4': 0.036, 'E4': 0.161, 'F4': 0.411, 'G4': 0.214}),
        'G4': defaultdict(float, {'A4': 0.185, 'B-4': 0.036, 'B4': 0.012, 'C5': 0.012, 'D4': 0.012, 'D5': 0.006, 'E-4': 0.012, 'E4': 0.065, 'F#4': 0.071, 'F4': 0.083, 'G4': 0.506}),
        'D4': defaultdict(float, {'C#4': 0.032, 'C4': 0.161, 'D4': 0.468, 'E4': 0.242, 'F#4': 0.016, 'G4': 0.081}),
        'B4': defaultdict(float, {'A4': 0.357, 'B4': 0.262, 'C5': 0.262, 'D5': 0.024, 'G4': 0.095}),
        'C5': defaultdict(float, {'A4': 0.164, 'B-4': 0.127, 'B4': 0.236, 'C5': 0.236, 'D5': 0.055, 'E5': 0.036, 'G4': 0.145}),
        'D5': defaultdict(float, {'A4': 0.154, 'C5': 0.462, 'D5': 0.231, 'E4': 0.154}),
        'A-4': defaultdict(float, {'A-4': 0.364, 'A4': 0.455, 'E4': 0.182}),
        'F#4': defaultdict(float, {'A-4': 0.048, 'D4': 0.048, 'F#4': 0.238, 'F4': 0.048, 'G4': 0.619}),
        'E5': defaultdict(float, {'D5': 0.125, 'E4': 0.500, 'G#4': 0.375}),
        'B-4': defaultdict(float, {'A4': 0.353, 'B-4': 0.353, 'C5': 0.088, 'D5': 0.029, 'F#4': 0.029, 'G4': 0.147}),
        'E-4': defaultdict(float, {'D4': 0.143, 'E-4': 0.429, 'E4': 0.143, 'F4': 0.286}),
        'G#4': defaultdict(float, {'A4': 0.133, 'D4': 0.133, 'E4': 0.200, 'G#4': 0.533}),
        'G5': defaultdict(float, {'B4': 0.667, 'G4': 0.333}),
        'F5': defaultdict(float, {'D4': 1.000}),
        'C4': defaultdict(float, {'A4': 0.069, 'B3': 0.207, 'C4': 0.448, 'D4': 0.207, 'F4': 0.069}),
        'B3': defaultdict(float, {'B3': 0.143, 'C4': 0.714, 'F4': 0.143}),
        'C#4': defaultdict(float, {'D4': 1.000}),
    })

class MelodyMinorB(ur.PitchMarkov):
    AMBITUS = ('E2', 'D4')
    AMBITUS_INITIAL = ('A2', 'C4')
    STATES = ['E4', 'A3', 'F3', 'D3', 'E3', 'A-3', 'G3', 'C4', 'D4', 'B3', 'C3', 'F#3', 'B-3', 'C#3', 'E-3', 'E-4', 'A2', 'B2', 'G2', 'F2', 'E2']
    INITIAL = ['A2', 'A3']
    FINAL = STATES

    TRANSITIONS = defaultdict(lambda: defaultdict(float), {
        'E4': defaultdict(float, {'A3': 0.444, 'E3': 0.333, 'E4': 0.222}),
        'A3': defaultdict(float, {'A3': 0.423, 'B-3': 0.046, 'B3': 0.054, 'C4': 0.046, 'D3': 0.031, 'E3': 0.085, 'E4': 0.008, 'F3': 0.038, 'G3': 0.269}),
        'F3': defaultdict(float, {'A3': 0.017, 'B-3': 0.052, 'C3': 0.052, 'D3': 0.121, 'E-3': 0.017, 'E3': 0.259, 'F#3': 0.017, 'F3': 0.241, 'G3': 0.224}),
        'D3': defaultdict(float, {'A3': 0.026, 'B-3': 0.039, 'C3': 0.039, 'D3': 0.299, 'E-3': 0.026, 'E3': 0.208, 'F3': 0.065, 'G2': 0.026, 'G3': 0.273}),
        'E3': defaultdict(float, {'A-3': 0.020, 'A2': 0.184, 'A3': 0.245, 'D3': 0.031, 'E3': 0.378, 'E4': 0.020, 'F#3': 0.020, 'F3': 0.102}),
        'A-3': defaultdict(float, {'A-3': 0.429, 'A3': 0.429, 'F#3': 0.143}),
        'G3': defaultdict(float, {'A-3': 0.011, 'A2': 0.011, 'A3': 0.119, 'B-3': 0.040, 'B2': 0.011, 'B3': 0.011, 'C3': 0.034, 'C4': 0.028, 'D3': 0.114, 'E-3': 0.006, 'E3': 0.011, 'F3': 0.085, 'G2': 0.011, 'G3': 0.506}),
        'C4': defaultdict(float, {'A3': 0.061, 'B-3': 0.020, 'B3': 0.102, 'C3': 0.020, 'C4': 0.388, 'D4': 0.204, 'E-4': 0.020, 'E3': 0.020, 'F3': 0.020, 'G3': 0.143}),
        'D4': defaultdict(float, {'B-3': 0.111, 'C4': 0.167, 'D3': 0.167, 'D4': 0.389, 'E4': 0.167}),
        'B3': defaultdict(float, {'A3': 0.353, 'B3': 0.176, 'C4': 0.412, 'G3': 0.059}),
        'C3': defaultdict(float, {'A3': 0.019, 'B2': 0.074, 'C#3': 0.019, 'C3': 0.333, 'C4': 0.019, 'D3': 0.259, 'E3': 0.148, 'F2': 0.037, 'F3': 0.093}),
        'F#3': defaultdict(float, {'E3': 0.200, 'G3': 0.800}),
        'B-3': defaultdict(float, {'A3': 0.237, 'B-3': 0.421, 'C4': 0.184, 'G3': 0.158}),
        'C#3': defaultdict(float, {'C#3': 0.500, 'D3': 0.500}),
        'E-3': defaultdict(float, {'D3': 0.400, 'E-3': 0.200, 'F3': 0.400}),
        'E-4': defaultdict(float, {'D4': 1.000}),
        'A2': defaultdict(float, {'A2': 0.188, 'A3': 0.094, 'B2': 0.219, 'C3': 0.344, 'E3': 0.031, 'F#3': 0.031, 'F3': 0.031, 'G2': 0.062}),
        'B2': defaultdict(float, {'A2': 0.308, 'C3': 0.538, 'E3': 0.154}),
        'G2': defaultdict(float, {'A2': 0.231, 'C3': 0.385, 'F2': 0.231, 'G2': 0.154}),
        'F2': defaultdict(float, {'G2': 1.000}),
        'E2': defaultdict(float, {'A2': 0.667, 'F2': 0.333}),
    })


class ScorerChords(ur.Scorer):
    ARGS = [(m.Chord, ur.Interval(1))]

    def score(self, chords: List[m.Chord]):

        defined: List[m.Chord] = list(filter(lambda c: not c.is_undefined(), chords))

        different = len(set(defined))
        stars = len(list(filter(lambda x: '*' in x, defined)))

        score = different/len(defined)
        if stars in [1, 2, 3]:
            score += 0.5
        return score


class MelodyHarm(ur.Constraint):

    ARGS = [(m.Pitch, ur.Interval(1,1)),
            (m.Chord, ur.Interval(1,1))]

    CHORDS: Dict[m.Chord, str]= {
        'I': 'ceg',
        'ii': 'dfa',
        'iii': 'egb',
        'IV': 'fac',
        'V': 'gd',
        'vi': 'ace',
        'vii': 'bdf',

        'i': 'ae',
        'iim': 'bdf',
        'III': 'ceg',
        'iv': 'dfa',
        'v': 'egb',
        'VI': 'fac',
        'VII': 'gd',

        'i3': 'ace',
        'v3': 'egb',

        'i8': 'a',

        '*i9': 'aaeb',
        '*III7': 'cegb',
        '*iv9': 'daeb',
        'v8': 'e',
    }

    def valid(self, mel: List[m.Pitch], chords: List[m.Chord]) -> float:

        # print (mel, harm, self.CHORDS[harm])
        pc: m.Pitch = mel[0].pc()
        chord: m.Chord = chords[0]
        return pc in self.CHORDS[chord]


class CadencePitches(ur.Enumerator):

    OUT_COUNT = ur.Interval(2,2)

    SOURCE = '(Kelley 2009)'

    MODE: str
    POSITION: int
    CADENCES: Dict[str, [Dict[int, List[List[m.Pitch]]]]] = {
        'major': {
            0: [[m.Pitch('G3'), m.Pitch('C3')],
                [m.Pitch('G3'), m.Pitch('C4')]],
            1: [[m.Pitch('D4'), m.Pitch('C4')]],
            2: [[m.Pitch('G4'), m.Pitch('G4')]],
            3: [[m.Pitch('D5'), m.Pitch('E5')],
                [m.Pitch('D5'), m.Pitch('C5')]],
        },
        'minor': {
            0: [[m.Pitch('E3'), m.Pitch('A3')],
                [m.Pitch('E3'), m.Pitch('A2')],
                [m.Pitch('G3'), m.Pitch('A3')]],
            1: [[m.Pitch('B3'), m.Pitch('A3')],
                [m.Pitch('D4'), m.Pitch('E4')]],
            2: [[m.Pitch('E4'), m.Pitch('E4')],
                [m.Pitch('G4'), m.Pitch('E4')]],
            3: [[m.Pitch('G5'), m.Pitch('E5')],
                [m.Pitch('D5'), m.Pitch('E5')]],
        }
    }

    def __init__(self, mode: str, voice: str):
        self.MODE = mode
        if voice not in VOICE_POSITIONS.keys():
            raise RuntimeError(f"Voice must be one of {' ,'.join(VOICE_POSITIONS.keys())}!")
        self.POSITION = VOICE_POSITIONS[voice]


    def guard(self, start: ur.Index) -> bool:
        return start.maps_to(-2, STRUCTURE_LEVELS['section'])

    def enumerate(self) -> List[List[m.Pitch]]:
        return self.CADENCES[self.MODE][self.POSITION]

class CadenceChords(ur.Enumerator):

    SOURCE = '(Kelley 2009)'

    OUT_COUNT = ur.Interval(2,2)

    CADENCES = {
        'major': [[m.Chord('V'), m.Chord('I')]],
        'minor': [[m.Chord('v'), m.Chord('i')],
                  [m.Chord('VII'), m.Chord('i')]],
    }

    def __init__(self, mode: str):
        self.MODE = mode

    def guard(self, start: ur.Index) -> bool:
        return start.maps_to(-2, STRUCTURE_LEVELS['section'])

    def enumerate(self) -> List[List[m.Chord]]:
        return self.CADENCES[self.MODE]

class Flourisher(ur.RandomizedProducer[m.Note]):

    DISPATCH_BY_NODE = True
    ARGS = [(m.Duration, ur.Interval(1)),
            (m.Pitch, ur.Interval(1))]
    OUT_COUNT = ur.Interval(1)

    FIGURES = {
        'third-passing': 0.4
    }

    def guard(self, node: ur.RefinementNode) -> bool:
        return node.depth == STRUCTURE_LEVELS['section']

    def flourish(self, p1: m.Pitch, d1: m.Duration, p2: m.Pitch, d2: m.Duration) -> List[m.Note]:

        rhy: List[float] = []
        pitches: List[str] = []

        # Some passing notes between thirds
        if nonchord.interval_third(p1, p2):
            if random.random() < self.FIGURES['third-passing']:
                rhy = [d1.quarter_length() / 2] * 2# if self.model.ternary else '8 8'
                pitches = [p1, nonchord.note_nonchord(p1, p2)]

        if pitches == [] and rhy == []:
            return [m.Note(d1, p1)]
        
        return [m.Note(m.Duration(d), m.Pitch(p)) for d, p in zip(rhy, pitches)]

    def produce(self, rhy: List[m.Duration], mel: List[m.Pitch]) -> List[m.Note]:
        
        if len(rhy) != len(mel):
            raise RuntimeError("Rhythm and Pitch lists must be of same length for flourishing")

        out: List[m.Note] = []
        
        for ((p1, d1), (p2, d2)) in zip(list(zip(mel, rhy))[:-2], list(zip(mel, rhy))[1:-1]):
            out += self.flourish(p1, d1, p2, d2)

        out += [m.Note(rhy[-2], mel[-2]), m.Note(rhy[-1], mel[-1])]

        return out
    