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
import glob
import gabuzomeu
import random
from rich import print



import argparse

parser = argparse.ArgumentParser(description = 'Fake Sacred Harp')
parser.add_argument('--save', '-s', type=int, default=0, help='starting number to save generation, otherwise draft generations')
parser.add_argument('--nb', '-n', type=int, default=0, help='number of generations with --save')

class Structure(ur.ItemChoice):
    CHOICES = ['AABC', 'ABA', 'ACBA' ]

class Lyrics(ur.ItemLyricsChoiceFiles):
    FILES = glob.glob('../../data/lyrics-s/*.txt')
    STRESS_WORDS = ['Lord', 'God', 'Christ', 'Son']

class FuncMajor(ur.ItemMarkov):

    SOURCE = '(Kelley 2016)'

    STATES = ['i', 'T', 'S', 'D']
    INITIAL = ['i']
    FINAL = ['i']

    TRANSITIONS = {
        'i': { 'i': 0.62, 'T': 0.10, 'S': 0.09, 'D': 0.18 },
        'T': { 'i': 0.62, 'T': 0.10, 'S': 0.09, 'D': 0.18 },
        'S': { 'i': 0.43, 'T': 0.10, 'S': 0.18, 'D': 0.28 },
        'D': { 'i': 0.57, 'T': 0.10, 'S': 0.09, 'D': 0.25 },
    }

    EMISSIONS = {
        'i': {'I': 1.00},
        'T': {'vi': 0.22, 'I': 0.78},
        'S': {'ii': 0.54, 'IV': 0.46},
        'D': {'iii': 0.21, 'V': 0.72, 'vii': 0.07},
    }


class FuncMinor(ur.ItemMarkov):

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


class Rhythm(ur.ItemSpanSequence):
    ITEMS_LAST = [
        ('2', 0.5),
        ('4', 0.5),
    ]
    ITEMS = [
                ('2', 0.03),
                ('4', 0.7),
                ('8 8', 0.25),
                ('4. 8', 0.05),
            ]

class Melody0(ur.ItemSequence):
    ITEMS = 'cdefgab'

class MelodyMajorS(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['C4', 'D4', 'E4', 'F4', 'B3', 'G4', 'A4', 'A3', 'C5', 'B4', 'G3', 'A-4', 'F#4', 'D3', 'C3', 'G2', 'A2', 'F3', 'E3', 'D2', 'B2']
    INITIAL = [...]
    FINAL = STATES

    TRANSITIONS = {
        'C4': {'A3': 0.047, 'A4': 0.004, 'B3': 0.182, 'C3': 0.004, 'C4': 0.171, 'D4': 0.310, 'E3': 0.004, 'E4': 0.136, 'F4': 0.058, 'G2': 0.004, 'G3': 0.047, 'G4': 0.035},
        'D4': {'A2': 0.004, 'A3': 0.016, 'B3': 0.040, 'C3': 0.004, 'C4': 0.292, 'D4': 0.212, 'E3': 0.004, 'E4': 0.332, 'F4': 0.024, 'G2': 0.012, 'G3': 0.020, 'G4': 0.040},
        'E4': {'A4': 0.029, 'C3': 0.004, 'C4': 0.192, 'D2': 0.004, 'D4': 0.341, 'E4': 0.141, 'F#4': 0.004, 'F4': 0.199, 'G4': 0.087},
        'F4': {'A4': 0.032, 'C4': 0.008, 'D2': 0.008, 'D4': 0.064, 'E4': 0.528, 'F4': 0.048, 'G4': 0.312},
        'B3': {'A3': 0.280, 'B3': 0.339, 'C4': 0.250, 'D4': 0.012, 'E4': 0.006, 'G3': 0.113},
        'G4': {'A4': 0.166, 'C4': 0.023, 'C5': 0.023, 'D4': 0.017, 'E3': 0.006, 'E4': 0.269, 'F4': 0.234, 'G3': 0.011, 'G4': 0.251},
        'A4': {'A-4': 0.015, 'A4': 0.227, 'B4': 0.061, 'C5': 0.015, 'F4': 0.015, 'G4': 0.667},
        'A3': {'A3': 0.321, 'B3': 0.343, 'C4': 0.060, 'D4': 0.045, 'E4': 0.015, 'F3': 0.007, 'G3': 0.209},
        'C5': {'A4': 0.154, 'B4': 0.462, 'C5': 0.231, 'G4': 0.154},
        'B4': {'A4': 0.500, 'B4': 0.167, 'C5': 0.333},
        'G3': {'A3': 0.194, 'B3': 0.052, 'C4': 0.269, 'D4': 0.015, 'E3': 0.037, 'E4': 0.015, 'G3': 0.410, 'G4': 0.007},
        'A-4': {'E4': 1.000},
        'F#4': {'A4': 1.000},
        'D3': {'B3': 0.250, 'D2': 0.750},
        'C3': {'A2': 0.143, 'C4': 0.286, 'D2': 0.429, 'E3': 0.143},
        'G2': {'C3': 0.500, 'D4': 0.500},
        'A2': {'A2': 0.333, 'B2': 0.333, 'D2': 0.333},
        'F3': {'D2': 0.500, 'G3': 0.500},
        'E3': {'D2': 0.111, 'D3': 0.111, 'E3': 0.222, 'G3': 0.556},
        'D2': {'G2': 1.000},
        'B2': {'E4': 1.000},
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }

class MelodyMajorA(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['G3', 'B3', 'C4', 'D4', 'A3', 'E3', 'F3', 'F#3', 'E4', 'F4', 'D3', 'A-3', 'G4']
    INITIAL = [...]
    FINAL = STATES

    TRANSITIONS = {
        'G3': {'A3': 0.132, 'B3': 0.026, 'C4': 0.060, 'D3': 0.011, 'D4': 0.002, 'E3': 0.060, 'F#3': 0.069, 'F3': 0.093, 'G3': 0.546},
        'B3': {'A-3': 0.007, 'A3': 0.129, 'B3': 0.171, 'C4': 0.479, 'D4': 0.043, 'G3': 0.171},
        'C4': {'A3': 0.049, 'B3': 0.217, 'C4': 0.618, 'D4': 0.035, 'E4': 0.017, 'F4': 0.006, 'G3': 0.058},
        'D4': {'A3': 0.023, 'B3': 0.045, 'C4': 0.386, 'D4': 0.341, 'E4': 0.159, 'F4': 0.023, 'G4': 0.023},
        'A3': {'A-3': 0.031, 'A3': 0.269, 'B3': 0.169, 'C4': 0.081, 'D4': 0.019, 'F#3': 0.013, 'F3': 0.031, 'G3': 0.388},
        'E3': {'A3': 0.029, 'D3': 0.019, 'E3': 0.538, 'F#3': 0.029, 'F3': 0.154, 'G3': 0.231},
        'F3': {'A3': 0.062, 'D3': 0.010, 'E3': 0.188, 'F3': 0.302, 'G3': 0.438},
        'F#3': {'A3': 0.091, 'D3': 0.015, 'E3': 0.091, 'F#3': 0.439, 'G3': 0.364},
        'E4': {'C4': 0.417, 'D4': 0.292, 'E4': 0.125, 'F4': 0.125, 'G4': 0.042},
        'F4': {'C4': 0.091, 'E4': 0.545, 'F4': 0.364},
        'D3': {'E3': 0.125, 'F3': 0.375, 'G3': 0.500},
        'A-3': {'A3': 0.833, 'E3': 0.167},
        'G4': {'E4': 0.500, 'F4': 0.250, 'G4': 0.250},
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }

class MelodyMajorT(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['E3', 'G3', 'A3', 'F3', 'D3', 'B3', 'C3', 'B2', 'A2', 'C#3', 'G2', 'E2', 'B-3', 'F#3', 'E-3', 'C4', 'G#3', 'F2']
    INITIAL = [...]
    FINAL = STATES

    TRANSITIONS = {
        'E3': {'A3': 0.009, 'B2': 0.009, 'C3': 0.088, 'D3': 0.248, 'E-3': 0.004, 'E3': 0.239, 'F3': 0.190, 'G3': 0.212},
        'G3': {'A3': 0.087, 'B-3': 0.003, 'B3': 0.003, 'C3': 0.026, 'C4': 0.023, 'D3': 0.013, 'E3': 0.084, 'F#3': 0.016, 'F3': 0.248, 'G#3': 0.006, 'G2': 0.006, 'G3': 0.486},
        'A3': {'A3': 0.204, 'B3': 0.041, 'C4': 0.061, 'F#3': 0.020, 'F3': 0.041, 'G#3': 0.020, 'G3': 0.612},
        'F3': {'A3': 0.012, 'C3': 0.023, 'D3': 0.012, 'E3': 0.439, 'F3': 0.193, 'G3': 0.322},
        'D3': {'B2': 0.023, 'C#3': 0.023, 'C3': 0.216, 'D3': 0.532, 'E3': 0.169, 'F#3': 0.010, 'F3': 0.003, 'G2': 0.003, 'G3': 0.020},
        'B3': {'A3': 0.286, 'B3': 0.286, 'C4': 0.143, 'G3': 0.286},
        'C3': {'A2': 0.028, 'B2': 0.113, 'C3': 0.544, 'D3': 0.194, 'E3': 0.059, 'F3': 0.047, 'G2': 0.009, 'G3': 0.006},
        'B2': {'B2': 0.222, 'C3': 0.698, 'D3': 0.048, 'G2': 0.016, 'G3': 0.016},
        'A2': {'B2': 0.500, 'C3': 0.200, 'D3': 0.300},
        'C#3': {'D3': 1.000},
        'G2': {'A2': 0.083, 'C3': 0.750, 'D3': 0.083, 'F2': 0.083},
        'E2': {'A2': 0.500, 'G2': 0.500},
        'B-3': {'A3': 0.500, 'B-3': 0.500},
        'F#3': {'E3': 0.333, 'F#3': 0.250, 'G3': 0.417},
        'E-3': {'E3': 1.000},
        'C4': {'A3': 0.087, 'B3': 0.087, 'C4': 0.522, 'G3': 0.304},
        'G#3': {'A3': 0.600, 'G#3': 0.400},
        'F2': {'E2': 1.000},
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }

class MelodyMajorB(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['C3', 'G2', 'F3', 'B2', 'D3', 'E3', 'A2', 'G3', 'F2', 'E2', 'D2', 'C2', 'F#2', 'G1', 'B1', 'E-3', 'B-2', 'C#2']
    INITIAL = [...]
    FINAL = STATES

    TRANSITIONS = {
        'C3': {'A2': 0.070, 'B-2': 0.008, 'B2': 0.054, 'C3': 0.477, 'D3': 0.105, 'E2': 0.012, 'E3': 0.039, 'F2': 0.093, 'F3': 0.035, 'G2': 0.105, 'G3': 0.004},
        'G2': {'A2': 0.065, 'B2': 0.015, 'C2': 0.127, 'C3': 0.151, 'D2': 0.050, 'E2': 0.030, 'F2': 0.065, 'G2': 0.494, 'G3': 0.003},
        'F3': {'A2': 0.024, 'C3': 0.167, 'E3': 0.357, 'F3': 0.310, 'G3': 0.143},
        'B2': {'A2': 0.234, 'B2': 0.064, 'C3': 0.702},
        'D3': {'A2': 0.106, 'C3': 0.303, 'D2': 0.030, 'D3': 0.212, 'E-3': 0.015, 'E3': 0.288, 'G2': 0.030, 'G3': 0.015},
        'E3': {'A2': 0.036, 'B2': 0.018, 'C3': 0.036, 'D3': 0.357, 'E2': 0.018, 'E3': 0.179, 'F3': 0.339, 'G3': 0.018},
        'A2': {'A2': 0.149, 'B2': 0.241, 'C3': 0.046, 'D2': 0.103, 'D3': 0.057, 'E2': 0.034, 'F#2': 0.023, 'F2': 0.011, 'G2': 0.333},
        'G3': {'C3': 0.238, 'E3': 0.048, 'F3': 0.048, 'G2': 0.238, 'G3': 0.429},
        'F2': {'A2': 0.024, 'C2': 0.065, 'C3': 0.083, 'D2': 0.054, 'E2': 0.149, 'F#2': 0.042, 'F2': 0.369, 'G2': 0.214},
        'E2': {'A2': 0.056, 'C2': 0.120, 'D2': 0.148, 'E2': 0.185, 'F2': 0.417, 'G2': 0.074},
        'D2': {'C#2': 0.008, 'C2': 0.127, 'D2': 0.397, 'E2': 0.246, 'F#2': 0.024, 'F2': 0.040, 'G2': 0.159},
        'C2': {'A2': 0.007, 'B1': 0.015, 'C2': 0.419, 'C3': 0.022, 'D2': 0.147, 'E2': 0.103, 'F2': 0.051, 'G2': 0.235},
        'F#2': {'D2': 0.167, 'G2': 0.833},
        'G1': {'C2': 1.000},
        'B1': {'C2': 1.000},
        'E-3': {'E-3': 0.500, 'E3': 0.500},
        'B-2': {'A2': 1.000},
        'C#2': {'D2': 1.000},
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }

class MelodyMinorS(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['E4', 'A4', 'B4', 'C5', 'G4', 'F4', 'D5', 'E5', 'G5', 'F5', 'A5', 'F#5', 'G#5', 'C6', 'B5', 'D4', 'C4']
    INITIAL = [...]
    FINAL = STATES

    TRANSITIONS = {
        'E4': {'A4': 0.214, 'B4': 0.190, 'C5': 0.095, 'D4': 0.238, 'E4': 0.119, 'E5': 0.048, 'F4': 0.071, 'G4': 0.024},
        'A4': {'A4': 0.176, 'B4': 0.341, 'C5': 0.118, 'D5': 0.012, 'E4': 0.059, 'E5': 0.059, 'G4': 0.235},
        'B4': {'A4': 0.330, 'B4': 0.093, 'C5': 0.412, 'D5': 0.021, 'E4': 0.052, 'E5': 0.010, 'G4': 0.082},
        'C5': {'A4': 0.063, 'B4': 0.287, 'C5': 0.203, 'D5': 0.266, 'E5': 0.119, 'F5': 0.021, 'G4': 0.035, 'G5': 0.007},
        'G4': {'A4': 0.360, 'B4': 0.080, 'C5': 0.020, 'E4': 0.080, 'F4': 0.240, 'G4': 0.220},
        'F4': {'E4': 0.789, 'F4': 0.211},
        'D5': {'B4': 0.047, 'C5': 0.372, 'D5': 0.128, 'E5': 0.349, 'F5': 0.023, 'G4': 0.012, 'G5': 0.070},
        'E5': {'A4': 0.019, 'A5': 0.032, 'C5': 0.133, 'D5': 0.190, 'E4': 0.006, 'E5': 0.437, 'F5': 0.114, 'G#5': 0.013, 'G5': 0.057},
        'G5': {'A5': 0.143, 'C5': 0.086, 'D5': 0.029, 'E5': 0.343, 'F#5': 0.057, 'F5': 0.114, 'G5': 0.229},
        'F5': {'D5': 0.125, 'E5': 0.656, 'F5': 0.156, 'G5': 0.062},
        'A5': {'A5': 0.133, 'C6': 0.067, 'D5': 0.067, 'E5': 0.133, 'G5': 0.600},
        'F#5': {'D5': 1.000},
        'G#5': {'A5': 1.000},
        'C6': {'B5': 1.000},
        'B5': {'A5': 1.000},
        'D4': {'C4': 0.100, 'E4': 0.500, 'G4': 0.400},
        'C4': {'C4': 1.000},
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }

class MelodyMinorA(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['E4', 'A4', 'F4', 'G4', 'D4', 'B4', 'C5', 'D5', 'A-4', 'F#4', 'E5', 'G#4', 'G5', 'F5', 'C4', 'B3', 'C#4']
    INITIAL = [...]
    FINAL = STATES

    TRANSITIONS = {
        'E4': {'A-4': 0.009, 'A4': 0.084, 'C5': 0.009, 'D4': 0.140, 'E4': 0.570, 'F#4': 0.009, 'F4': 0.056, 'G#4': 0.075, 'G4': 0.047},
        'A4': {'A-4': 0.023, 'A4': 0.472, 'B4': 0.115, 'C5': 0.083, 'D5': 0.005, 'E4': 0.078, 'E5': 0.005, 'F4': 0.028, 'G#4': 0.055, 'G4': 0.138},
        'F4': {'D4': 0.062, 'E4': 0.312, 'F#4': 0.031, 'F4': 0.312, 'G4': 0.281},
        'G4': {'A4': 0.262, 'B4': 0.058, 'C5': 0.010, 'D4': 0.019, 'D5': 0.010, 'E4': 0.136, 'F4': 0.068, 'G4': 0.437},
        'D4': {'C#4': 0.038, 'C4': 0.189, 'D4': 0.453, 'E4': 0.283, 'G4': 0.038},
        'B4': {'A4': 0.384, 'B4': 0.233, 'C5': 0.260, 'D5': 0.027, 'G4': 0.096},
        'C5': {'A4': 0.189, 'B4': 0.338, 'C5': 0.270, 'D5': 0.054, 'E5': 0.041, 'G#4': 0.014, 'G4': 0.095},
        'D5': {'A4': 0.136, 'C5': 0.409, 'D5': 0.273, 'E4': 0.091, 'E5': 0.091},
        'A-4': {'A-4': 0.364, 'A4': 0.455, 'E4': 0.182},
        'F#4': {'A-4': 0.333, 'F#4': 0.333, 'G#4': 0.333},
        'E5': {'D5': 0.273, 'E4': 0.364, 'E5': 0.091, 'G#4': 0.273},
        'G#4': {'A4': 0.429, 'D4': 0.057, 'E4': 0.114, 'G#4': 0.371, 'G4': 0.029},
        'G5': {'B4': 0.667, 'G4': 0.333},
        'F5': {'D4': 1.000},
        'C4': {'A4': 0.069, 'B3': 0.207, 'C4': 0.448, 'D4': 0.207, 'F4': 0.069},
        'B3': {'B3': 0.143, 'C4': 0.714, 'F4': 0.143},
        'C#4': {'D4': 1.000},
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }

class MelodyMinorT(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['E4', 'C4', 'D4', 'B3', 'A3', 'A-3', 'G4', 'A-4', 'A4', 'G3', 'F3', 'E3', 'F#4', 'F4', 'C5', 'B4', 'G#3', 'G#4', 'C#4', 'F#3', 'D3']
    INITIAL = [...]
    FINAL = STATES

    TRANSITIONS = {
        'E4': {'A3': 0.006, 'A4': 0.013, 'B3': 0.019, 'C4': 0.152, 'D4': 0.266, 'E4': 0.405, 'F4': 0.070, 'G4': 0.070},
        'C4': {'A3': 0.041, 'B3': 0.324, 'C4': 0.257, 'D4': 0.209, 'E4': 0.149, 'F4': 0.014, 'G4': 0.007},
        'D4': {'A3': 0.018, 'B3': 0.053, 'C#4': 0.009, 'C4': 0.345, 'D4': 0.257, 'E4': 0.257, 'F4': 0.035, 'G4': 0.027},
        'B3': {'A3': 0.386, 'B3': 0.218, 'C4': 0.248, 'D4': 0.010, 'E3': 0.020, 'E4': 0.079, 'G#3': 0.010, 'G3': 0.030},
        'A3': {'A-3': 0.047, 'A3': 0.283, 'B3': 0.179, 'C4': 0.113, 'D3': 0.019, 'D4': 0.038, 'E3': 0.019, 'E4': 0.057, 'F#3': 0.019, 'F3': 0.009, 'G#3': 0.075, 'G3': 0.142},
        'A-3': {'A3': 0.375, 'B3': 0.375, 'E3': 0.250},
        'G4': {'A-4': 0.043, 'A4': 0.109, 'C4': 0.043, 'D4': 0.087, 'E4': 0.217, 'F4': 0.087, 'G#4': 0.022, 'G4': 0.391},
        'A-4': {'A-4': 0.600, 'A4': 0.400},
        'A4': {'A4': 0.360, 'B4': 0.080, 'C5': 0.040, 'E4': 0.240, 'F#4': 0.080, 'G4': 0.200},
        'G3': {'A-3': 0.068, 'A3': 0.295, 'C4': 0.068, 'E3': 0.068, 'E4': 0.023, 'F#3': 0.045, 'F3': 0.205, 'G3': 0.227},
        'F3': {'G3': 1.000},
        'E3': {'A3': 0.476, 'C4': 0.190, 'E3': 0.333},
        'F#4': {'G4': 1.000},
        'F4': {'A4': 0.111, 'D4': 0.037, 'E4': 0.407, 'F4': 0.222, 'G4': 0.222},
        'C5': {'B4': 1.000},
        'B4': {'A4': 1.000},
        'G#3': {'A3': 0.500, 'E3': 0.400, 'G#3': 0.100},
        'G#4': {'A4': 0.500, 'G#4': 0.500},
        'C#4': {'D4': 1.000},
        'F#3': {'G3': 1.000},
        'D3': {'G3': 1.000},
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }

class MelodyMinorB(ur.ItemMarkov):

    SOURCE = ''

    STATES = ['E4', 'A3', 'F3', 'D3', 'E3', 'A-3', 'G3', 'C4', 'D4', 'B3', 'C3', 'F#3', 'E-3', 'F4', 'G#3', 'A2', 'B2', 'G2', 'F2', 'E2']
    INITIAL = [...]
    FINAL = STATES

    TRANSITIONS = {
        'E4': {'A3': 0.200, 'C4': 0.100, 'D4': 0.050, 'E3': 0.300, 'E4': 0.350},
        'A3': {'A3': 0.507, 'B3': 0.063, 'C4': 0.063, 'D3': 0.029, 'E3': 0.146, 'E4': 0.005, 'F3': 0.029, 'G3': 0.156},
        'F3': {'C3': 0.045, 'D3': 0.068, 'E3': 0.386, 'F3': 0.205, 'G3': 0.295},
        'D3': {'A3': 0.043, 'C3': 0.043, 'D3': 0.426, 'D4': 0.021, 'E-3': 0.021, 'E3': 0.383, 'F3': 0.021, 'G2': 0.043},
        'E3': {'A-3': 0.014, 'A2': 0.130, 'A3': 0.326, 'C4': 0.022, 'D3': 0.029, 'E3': 0.333, 'E4': 0.014, 'F#3': 0.014, 'F3': 0.087, 'G3': 0.029},
        'A-3': {'A-3': 0.429, 'A3': 0.429, 'F#3': 0.143},
        'G3': {'A-3': 0.020, 'A2': 0.020, 'A3': 0.170, 'B2': 0.020, 'B3': 0.030, 'C3': 0.040, 'C4': 0.080, 'D3': 0.020, 'E3': 0.060, 'F3': 0.090, 'G#3': 0.010, 'G2': 0.020, 'G3': 0.420},
        'C4': {'A3': 0.127, 'B3': 0.197, 'C3': 0.014, 'C4': 0.394, 'D4': 0.169, 'E3': 0.014, 'F3': 0.014, 'G3': 0.070},
        'D4': {'A3': 0.087, 'C4': 0.130, 'D4': 0.391, 'E4': 0.348, 'F4': 0.043},
        'B3': {'A3': 0.432, 'B3': 0.189, 'C4': 0.351, 'G3': 0.027},
        'C3': {'A3': 0.023, 'B2': 0.091, 'C3': 0.273, 'D3': 0.273, 'E3': 0.182, 'F2': 0.045, 'F3': 0.114},
        'F#3': {'E3': 0.250, 'G3': 0.750},
        'E-3': {'E-3': 0.500, 'E3': 0.500},
        'F4': {'E4': 1.000},
        'G#3': {'A3': 1.000},
        'A2': {'A2': 0.188, 'A3': 0.094, 'B2': 0.219, 'C3': 0.344, 'E3': 0.031, 'F#3': 0.031, 'F3': 0.031, 'G2': 0.062},
        'B2': {'A2': 0.308, 'C3': 0.538, 'E3': 0.154},
        'G2': {'A2': 0.231, 'C3': 0.385, 'F2': 0.231, 'G2': 0.154},
        'F2': {'G2': 1.000},
        'E2': {'A2': 0.667, 'F2': 0.333},
    }

    EMISSIONS = {
        x: {x: 1.00} for x in STATES
    }



S2 = { '2': 2, '4.': 2, '4': 1, '8': 0, '4. 8': 2, '8 8': 2 }
S1 = { '2': 1, '4.': 1, '4': 1, '8': 0, '4. 8': 1, '8 8': 1 }
S0 = { '2': 0, '4.': 0, '4': 1, '8': 1, '4. 8': 0, '8 8': 0 }

class ScorerLyricsRhythm(ur.ScorerSpanSequence):


    STRESSES = [
        ('!', S2),
        ('>>', S1),
        ('>',  S1),

        ('/', S2),
        ('.', S1),

        (';', S1),
        (',', S1),

        ('',  S0),
    ]


    def score_element(self, lyr, rhy):
        for (symbol, scores) in self.STRESSES:
            if symbol in lyr:
                if rhy in scores:
                    return scores[rhy]
                # return 0
        print('!', lyr, rhy)
        return 0

class ScorerHarmMelody(ur.ScorerSequence):

    CHORDS = {
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
    }

    def score_element(self, harm, mel):
        # print (mel, harm, self.CHORDS[harm])
        if mel[0] in self.CHORDS[harm]:
            return 1.0
        else:
            return 0.0

    def score_first_last_element(self, harm, mel):
        if mel[0] in self.CHORDS[harm]:
            return 1.0
        else:
            return -20


class ScorerHarmMelodyRoot(ScorerHarmMelody):

    SCORES = {
        None: -5.0,
        0: 1.0,
        1: 0.5,
        2: 0.2,
    }

    '''Favors 5, '''
    def score_element(self, harm, mel):
        if mel[0] in self.CHORDS[harm]:
            i = self.CHORDS[harm].index(mel[0])
            return self.SCORES[i]
        else:
            return self.SCORES[None]

    def score_first_last_element(self, harm, mel):
        if mel[0] == self.CHORDS[harm][0]:
            return 0.0
        else:
            return -20.0


def gen_sacred():
    print('[yellow]### Init')
    sh = ur.Model()

    sh.add(Structure('struct'))

    mode = random.choice(['Major', 'minor'])

    # sh.add(ur.Or('func', [FuncMajor('Major'),
    #                       FuncMinor('minor')]))

    if mode == 'Major':
        Func = FuncMajor
        MelodyUp = MelodyMajorUp
        MelodyDown = MelodyMajorDown
    else:
        Func = FuncMinor
        MelodyUp = MelodyMinorUp
        MelodyDown = MelodyMinorDown

    sh.add(Func('func'))
    sh.structurer('struct', 'func')

    sh.add(MelodyUp('mel'))
    score = sh.scorer(ScorerHarmMelody, 'func', 'mel')

    sh.add(MelodyUp('melS'))
    scoreS = sh.scorer(ScorerHarmMelody, 'func', 'melS')

    sh.add(MelodyDown('melA'))
    scoreA = sh.scorer(ScorerHarmMelody, 'func', 'melA')

    sh.add(MelodyDown('melB'))
    scoreB = sh.scorer(ScorerHarmMelodyRoot, 'func', 'melB')

    sh.add(Lyrics('lyr'))
    sh.structurer('struct', 'lyr')
    sh['lyr'].load()
    sh.add(Rhythm('rhy'))
    scoreL = sh.scorer(ScorerLyricsRhythm, 'lyr', 'rhy')

    print(sh)

    # -------------------------------------------------------

    print('[yellow]### Gen 1, independent')
    sh.generate()
    sh.score()
    print(sh)

    # -------------------------------------------------------

    print('[yellow]### Gen 2')
    sh.reset()
    sh['struct'].gen()
    sh.set_structure()

    l0 = sh['lyr'].gen()
    sh['rhy'].set_filter(scoreL)
    r0 = sh['rhy'].gen(l0)
    print(r0)

    d0 = sh['func'].gen(r0)
    print("d0", d0)

    sh['mel'].set_filter(score)
    m0 = sh['mel'].gen(d0)


    sh['melS'].set_filter(scoreS)
    m0 = sh['melS'].gen(d0)
    sh['melA'].set_filter(scoreA)
    m0 = sh['melA'].gen(d0)

    sh['melB'].set_filter(scoreB)
    m0 = sh['melB'].gen(d0)



    sh.score()
    return sh


def sacred(code, f):
    sh = gen_sacred()    
    print(sh)

    sh.export(
        f,
        code + '. ' + gabuzomeu.sentence(),
        sh['struct'].structure,
        sh['rhy'],
        sh['lyr'],
        ['melS', 'melA', 'mel', 'melB'],
        ['func']
        )

if __name__ == '__main__':

    args = parser.parse_args()

    if args.nb:
        nb = args.nb
    else:
        nb = 20 if args.save else 5

    for i in range(nb):
        if args.save:
            n = args.save + i
            code = '%03d' % n
            f = 'sacred-' + code
        else:
            code = 'draft-%02d' % i
            f = code

        sacred(code, f)