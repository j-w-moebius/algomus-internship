'''
A simple homophonic model, inspired by Sacred Harp corpus
and by (Kelley 2016) models.
'''

import ur
import glob
import music
import math
import tools

class Structure(ur.ItemChoice):
    CHOICES = ['AB-aC', 'AB-bA', 'A-aB' ]
               # 'AQ-RA', 'AQ-AC', 'BA-QA' ]


class Lyrics(ur.ItemLyricsChoiceFiles):
    FILES = glob.glob('../../data/lyrics-s/*.txt')
    STRESS_WORDS = ['Lord', 'God', 'Christ', 'Son']


class HHLyrics(ur.ItemLyricsChoiceFiles):
    FILES = glob.glob('../../data/lyrics-hh/*.txt')


class Key(ur.ItemChoice):
    CHOICES = ['P-4', 'm-3', 'M-2', 'P1', 'M2', 'm3', 'P4']

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


class FuncMinorExtended(FuncMinor):

    STATES = ['i', 'j', 'T', 'S', 'D']
    INITIAL_S = { None: ['j'], 'b': ['D', 'S'], 'B': ['D', 'S'] }
    FINAL_S = { None: ['i'], 'b': ['i', 'D'], 'B': ['i', 'D'] }

    TRANSITIONS = {
        'j': { 'i': 0.30, 'T': 0.23, 'S': 0.08, 'D': 0.39 },
        'i': { 'i': 0.30, 'T': 0.23, 'S': 0.08, 'D': 0.39 },
        'T': { 'i': 0.30, 'T': 0.23, 'S': 0.08, 'D': 0.39 },
        'S': { 'i': 0.10, 'T': 0.21, 'S': 0.14, 'D': 0.55 },
        'D': { 'i': 0.20, 'T': 0.29, 'S': 0.08, 'D': 0.43 },
    }

    EMISSIONS = {
        'j': {'i': 0.50, 'i3': 0.20,  'i8': 0.15 },
        'i': {'i': 1.00 },
        'T': {'i': 0.30, 'i3': 0.20, '*i9': 0.25 },
        'S': {'iim': 0.19, 'iv': 0.33, '*iv9': 0.10, 'VI': 0.28},
        'D': {'III': 0.20, '*III7': 0.08, 'v': 0.15, 'v3': 0.7, 'v8': 0.05, 'VII': 0.33},
    }

class Rhythm(ur.ItemSpanSequence):
    ITEMS_LAST = [
        ('2', 0.8),
        ('4', 0.5),
    ]
    ITEMS = [
                ('2', 0.03),
                ('4', 0.7),
                ('8 8', 0.20),
                ('8. 16', 0.05),
                ('4. 8', 0.05),
            ]

class TernaryRhythm(ur.ItemSpanSequence):
    ITEMS_LAST = [
        ('2.', 0.8),
        ('4.', 0.5),
    ]
    ITEMS = [
                ('2.', 0.03),
                ('4.', 0.30),
                ('4 8', 0.20),
                ('8 8 8', 0.10),
                ('4 16 16', 0.05),
                ('8 8 16 16', 0.05),
                ('8 16 16 8', 0.02),
                ('8. 16 8', 0.10),
            ]


class Melody0(ur.ItemSequence):
    ITEMS = 'cdefgab'

class MelodyMajorS(ur.ItemPitchMarkov):
    AMBITUS = ['C4', 'A5']
    AMBITUS_INITIAL = ['E4', 'E5']
    STATES = ['C4', 'D4', 'E4', 'F4', 'B3', 'G4', 'A4', 'A3', 'C5', 'B4', 'G3', 'D5', 'E5', 'F5', 'A5', 'G5', 'A-5', 'F#5', 'D3', 'F3']
    INITIAL = ['C4', 'E4', 'G4', 'C5', 'E5']
    FINAL = STATES

    TRANSITIONS = {
        'C4': {'A3': 0.025, 'B3': 0.025, 'C4': 0.269, 'C5': 0.017, 'D3': 0.025, 'D4': 0.294, 'E4': 0.168, 'F4': 0.067, 'G3': 0.050, 'G4': 0.059},
        'D4': {'B3': 0.018, 'B4': 0.009, 'C4': 0.316, 'D3': 0.026, 'D4': 0.237, 'E4': 0.307, 'F4': 0.026, 'G3': 0.026, 'G4': 0.035},
        'E4': {'C4': 0.199, 'D3': 0.007, 'D4': 0.267, 'E4': 0.130, 'F4': 0.260, 'G4': 0.137},
        'F4': {'A4': 0.051, 'D3': 0.013, 'D4': 0.090, 'E4': 0.449, 'F4': 0.038, 'G4': 0.359},
        'B3': {'A3': 0.143, 'C4': 0.714, 'E5': 0.143},
        'G4': {'A4': 0.224, 'B4': 0.032, 'C4': 0.014, 'C5': 0.123, 'D4': 0.014, 'D5': 0.009, 'E4': 0.146, 'F4': 0.110, 'G3': 0.009, 'G4': 0.315, 'G5': 0.005},
        'A4': {'A4': 0.305, 'B4': 0.282, 'C5': 0.051, 'D5': 0.034, 'E5': 0.006, 'F4': 0.006, 'G4': 0.316},
        'A3': {'A3': 0.167, 'B3': 0.167, 'D3': 0.167, 'E4': 0.167, 'F3': 0.167, 'G3': 0.167},
        'C5': {'A4': 0.075, 'A5': 0.006, 'B4': 0.314, 'C4': 0.006, 'C5': 0.094, 'D5': 0.283, 'E4': 0.006, 'E5': 0.101, 'F5': 0.044, 'G3': 0.006, 'G4': 0.050, 'G5': 0.013},
        'B4': {'A4': 0.299, 'B4': 0.339, 'C5': 0.236, 'D5': 0.011, 'E5': 0.006, 'G4': 0.109},
        'G3': {'C4': 0.560, 'D5': 0.040, 'E4': 0.080, 'G3': 0.320},
        'D5': {'A3': 0.007, 'A4': 0.029, 'B4': 0.057, 'C4': 0.007, 'C5': 0.264, 'D5': 0.186, 'E4': 0.007, 'E5': 0.343, 'F5': 0.021, 'G3': 0.021, 'G4': 0.014, 'G5': 0.043},
        'E5': {'A5': 0.058, 'C4': 0.007, 'C5': 0.173, 'D3': 0.007, 'D5': 0.403, 'E5': 0.158, 'F#5': 0.007, 'F5': 0.122, 'G5': 0.065},
        'F5': {'C5': 0.021, 'D3': 0.021, 'D5': 0.021, 'E5': 0.646, 'F5': 0.062, 'G5': 0.229},
        'A5': {'A-5': 0.050, 'A5': 0.200, 'G5': 0.750},
        'G5': {'A5': 0.090, 'C5': 0.015, 'E4': 0.015, 'E5': 0.299, 'F5': 0.254, 'G5': 0.328},
        'A-5': {'E5': 1.000},
        'F#5': {'A5': 1.000},
        'D3': {'G3': 1.000},
        'F3': {'G3': 1.000},
    }

class MelodyMajorA(ur.ItemPitchMarkov):
    AMBITUS = ['G3', 'D5']
    AMBITUS_INITIAL = ['A3', 'C5']
    STATES = ['G3', 'B3', 'C4', 'D4', 'A3', 'E3', 'F3', 'G4', 'F4', 'A4', 'F#4', 'B4', 'C5', 'D5', 'E4', 'E5', 'F5', 'A-4', 'D3']
    INITIAL = ['G3', 'C4', 'E4', 'G4', 'C4']
    FINAL = STATES

    TRANSITIONS = {
        'G3': {'A3': 0.267, 'B3': 0.027, 'C4': 0.120, 'D4': 0.013, 'E3': 0.027, 'F3': 0.027, 'G3': 0.520},
        'B3': {'A3': 0.125, 'B3': 0.163, 'C4': 0.500, 'D4': 0.037, 'G3': 0.175},
        'C4': {'A3': 0.049, 'B3': 0.186, 'C4': 0.668, 'D4': 0.040, 'E4': 0.018, 'F4': 0.009, 'G3': 0.031},
        'D4': {'A3': 0.023, 'B3': 0.023, 'C4': 0.233, 'D4': 0.349, 'E4': 0.186, 'F4': 0.093, 'G4': 0.093},
        'A3': {'A3': 0.295, 'B3': 0.361, 'C4': 0.148, 'D4': 0.049, 'F3': 0.016, 'G3': 0.131},
        'E3': {'A3': 0.250, 'F3': 0.750},
        'F3': {'D3': 0.125, 'E3': 0.375, 'F3': 0.250, 'G3': 0.250},
        'G4': {'A4': 0.105, 'B4': 0.026, 'C5': 0.048, 'D4': 0.013, 'E4': 0.071, 'F#4': 0.082, 'F4': 0.107, 'G4': 0.548},
        'F4': {'A4': 0.062, 'C4': 0.010, 'E4': 0.196, 'F4': 0.320, 'G4': 0.412},
        'A4': {'A-4': 0.051, 'A4': 0.253, 'B4': 0.051, 'C5': 0.040, 'F#4': 0.020, 'F4': 0.040, 'G4': 0.545},
        'F#4': {'A4': 0.091, 'D4': 0.015, 'E4': 0.091, 'F#4': 0.439, 'G4': 0.364},
        'B4': {'A-4': 0.017, 'A4': 0.133, 'B4': 0.183, 'C5': 0.450, 'D5': 0.050, 'G4': 0.167},
        'C5': {'A4': 0.050, 'B4': 0.275, 'C5': 0.525, 'D5': 0.025, 'E5': 0.017, 'G4': 0.108},
        'D5': {'B4': 0.125, 'C5': 0.875},
        'E4': {'A4': 0.017, 'C4': 0.083, 'D4': 0.058, 'E4': 0.492, 'F#4': 0.025, 'F4': 0.117, 'G4': 0.208},
        'E5': {'D5': 0.500, 'F5': 0.500},
        'F5': {'E5': 1.000},
        'A-4': {'A4': 0.833, 'E4': 0.167},
        'D3': {'G3': 1.000},
    }

class MelodyMajorT(ur.ItemPitchMarkov):
    AMBITUS = ['B2', 'A4']
    AMBITUS_INITIAL = ['E3', 'E4']
    STATES = ['E3', 'G3', 'A3', 'F3', 'D3', 'B3', 'C3', 'B2', 'A2', 'E4', 'C4', 'D4', 'C#4', 'G4', 'F4', 'A4', 'B-4', 'F#4', 'E-4', 'G#3', 'F#3']
    INITIAL = ['C3', 'E3', 'G3', 'C4', 'E4']
    FINAL = STATES

    TRANSITIONS = {
        'E3': {'A3': 0.029, 'C3': 0.048, 'D3': 0.096, 'E3': 0.288, 'F3': 0.288, 'G3': 0.250},
        'G3': {'A3': 0.121, 'B3': 0.005, 'C3': 0.030, 'C4': 0.081, 'D3': 0.005, 'D4': 0.005, 'E3': 0.076, 'F3': 0.253, 'G#3': 0.010, 'G3': 0.414},
        'A3': {'A3': 0.192, 'B3': 0.096, 'C4': 0.096, 'D4': 0.058, 'F#3': 0.019, 'F3': 0.038, 'G#3': 0.019, 'G3': 0.481},
        'F3': {'A3': 0.018, 'D3': 0.009, 'E3': 0.423, 'F3': 0.198, 'G3': 0.351},
        'D3': {'B2': 0.062, 'C3': 0.406, 'D3': 0.125, 'E3': 0.375, 'F3': 0.031},
        'B3': {'A3': 0.033, 'B3': 0.262, 'C4': 0.623, 'D4': 0.016, 'G3': 0.049, 'G4': 0.016},
        'C3': {'A2': 0.053, 'B2': 0.132, 'C3': 0.211, 'D3': 0.316, 'E3': 0.079, 'F3': 0.158, 'G3': 0.053},
        'B2': {'C3': 0.778, 'D3': 0.222},
        'A2': {'B2': 1.000},
        'E4': {'B3': 0.016, 'C4': 0.121, 'D4': 0.371, 'E-4': 0.008, 'E4': 0.194, 'F4': 0.105, 'G4': 0.185},
        'C4': {'A3': 0.030, 'B3': 0.108, 'C4': 0.584, 'D4': 0.164, 'E4': 0.052, 'F4': 0.030, 'G3': 0.033},
        'D4': {'B3': 0.019, 'C#4': 0.026, 'C4': 0.193, 'D4': 0.580, 'E4': 0.145, 'F#4': 0.011, 'G3': 0.004, 'G4': 0.022},
        'C#4': {'D4': 1.000},
        'G4': {'A4': 0.032, 'B-4': 0.008, 'C4': 0.016, 'D4': 0.024, 'E4': 0.088, 'F#4': 0.040, 'F4': 0.224, 'G3': 0.016, 'G4': 0.552},
        'F4': {'C4': 0.066, 'D4': 0.016, 'E4': 0.475, 'F4': 0.180, 'G4': 0.262},
        'A4': {'G4': 1.000},
        'B-4': {'A4': 0.500, 'B-4': 0.500},
        'F#4': {'E4': 0.400, 'F#4': 0.200, 'G4': 0.400},
        'E-4': {'E4': 1.000},
        'G#3': {'A3': 0.600, 'G#3': 0.400},
        'F#3': {'F#3': 0.500, 'G3': 0.500},
    }

class MelodyMajorB(ur.ItemPitchMarkov):
    AMBITUS = ['E2', 'D4']
    AMBITUS_INITIAL = ['A2', 'C4']
    STATES = ['C3', 'G2', 'F3', 'B2', 'D3', 'E3', 'A2', 'G3', 'F2', 'E2', 'D2', 'C2', 'F#3', 'C4', 'E4', 'D4', 'F4', 'B3', 'A3', 'E-4', 'B-2', 'C#3']
    INITIAL = ['C3', 'C4']
    FINAL = STATES

    TRANSITIONS = {
        'C3': {'A2': 0.049, 'A3': 0.003, 'B-2': 0.007, 'B2': 0.026, 'C3': 0.497, 'C4': 0.010, 'D3': 0.098, 'E2': 0.007, 'E3': 0.065, 'F2': 0.042, 'F3': 0.039, 'G2': 0.049, 'G3': 0.108},
        'G2': {'A2': 0.153, 'B2': 0.020, 'C2': 0.020, 'C3': 0.439, 'F2': 0.071, 'G2': 0.286, 'G3': 0.010},
        'F3': {'A2': 0.006, 'A3': 0.006, 'C3': 0.114, 'C4': 0.019, 'D3': 0.057, 'E3': 0.196, 'F#3': 0.044, 'F3': 0.380, 'G3': 0.177},
        'B2': {'A2': 0.125, 'B2': 0.125, 'C3': 0.750},
        'D3': {'A2': 0.020, 'C#3': 0.007, 'C3': 0.150, 'D3': 0.405, 'E3': 0.222, 'F#3': 0.020, 'F3': 0.033, 'G2': 0.007, 'G3': 0.137},
        'E3': {'A2': 0.016, 'A3': 0.033, 'C3': 0.090, 'D3': 0.189, 'E3': 0.180, 'F3': 0.426, 'G3': 0.066},
        'A2': {'A2': 0.132, 'B2': 0.151, 'C3': 0.057, 'D2': 0.113, 'D3': 0.075, 'E2': 0.038, 'F2': 0.019, 'G2': 0.415},
        'G3': {'A3': 0.026, 'B3': 0.011, 'C3': 0.168, 'C4': 0.073, 'D3': 0.062, 'E3': 0.040, 'F3': 0.059, 'G2': 0.018, 'G3': 0.542},
        'F2': {'A2': 0.068, 'C3': 0.250, 'E2': 0.068, 'F2': 0.295, 'G2': 0.318},
        'E2': {'A2': 0.125, 'C2': 0.188, 'D2': 0.062, 'E2': 0.125, 'F2': 0.438, 'G2': 0.062},
        'D2': {'E2': 1.000},
        'C2': {'C2': 0.250, 'F2': 0.750},
        'F#3': {'D3': 0.167, 'G3': 0.833},
        'C4': {'A3': 0.036, 'B3': 0.095, 'C4': 0.321, 'D4': 0.202, 'E3': 0.012, 'E4': 0.048, 'F3': 0.131, 'F4': 0.012, 'G3': 0.143},
        'E4': {'B3': 0.038, 'C4': 0.038, 'D4': 0.462, 'E3': 0.038, 'E4': 0.231, 'F4': 0.192},
        'D4': {'A3': 0.125, 'C4': 0.406, 'D3': 0.062, 'D4': 0.062, 'E-4': 0.031, 'E4': 0.281, 'G3': 0.031},
        'F4': {'E4': 0.750, 'F4': 0.250},
        'B3': {'A3': 0.320, 'C4': 0.680},
        'A3': {'A3': 0.176, 'B3': 0.382, 'C4': 0.029, 'D3': 0.088, 'D4': 0.029, 'E3': 0.029, 'F#3': 0.059, 'G3': 0.206},
        'E-4': {'E-4': 0.500, 'E4': 0.500},
        'B-2': {'A2': 1.000},
        'C#3': {'D3': 1.000},
    }

class MelodyMinorS(ur.ItemPitchMarkov):
    AMBITUS = ['C4', 'A5']
    AMBITUS_INITIAL = ['E4', 'E5']
    STATES = ['E4', 'A4', 'B4', 'C5', 'G4', 'F4', 'D5', 'E5', 'G5', 'F5', 'A5', 'F#5', 'E-5', 'B-4', 'B-5', 'D4', 'C4']
    INITIAL = ['E4', 'A4', 'C5', 'E5']
    FINAL = STATES

    TRANSITIONS = {
        'E4': {'A4': 0.214, 'B4': 0.190, 'C5': 0.095, 'D4': 0.238, 'E4': 0.119, 'E5': 0.048, 'F4': 0.071, 'G4': 0.024},
        'A4': {'A4': 0.129, 'B-4': 0.059, 'B4': 0.294, 'C5': 0.094, 'D5': 0.024, 'E4': 0.059, 'E5': 0.035, 'F4': 0.024, 'G4': 0.282},
        'B4': {'A4': 0.329, 'B4': 0.106, 'C5': 0.412, 'D5': 0.024, 'E4': 0.059, 'G4': 0.071},
        'C5': {'A4': 0.079, 'B-4': 0.108, 'B4': 0.259, 'C5': 0.158, 'D5': 0.295, 'E-5': 0.007, 'E5': 0.022, 'F5': 0.029, 'G4': 0.036, 'G5': 0.007},
        'G4': {'A4': 0.333, 'B-4': 0.033, 'B4': 0.067, 'C5': 0.017, 'D5': 0.033, 'E4': 0.067, 'F4': 0.200, 'G4': 0.250},
        'F4': {'E4': 0.714, 'F4': 0.190, 'G4': 0.095},
        'D5': {'B-4': 0.070, 'B4': 0.008, 'C5': 0.295, 'D5': 0.318, 'E-5': 0.093, 'E5': 0.124, 'F#5': 0.016, 'F5': 0.031, 'G4': 0.016, 'G5': 0.031},
        'E5': {'A4': 0.028, 'A5': 0.042, 'C5': 0.167, 'D5': 0.125, 'E4': 0.014, 'E5': 0.458, 'F5': 0.083, 'G5': 0.083},
        'G5': {'A5': 0.087, 'B-5': 0.043, 'C5': 0.043, 'E5': 0.174, 'F#5': 0.087, 'F5': 0.391, 'G5': 0.174},
        'F5': {'B-4': 0.061, 'C5': 0.030, 'D5': 0.242, 'E-5': 0.061, 'E5': 0.273, 'F5': 0.242, 'G5': 0.091},
        'A5': {'D5': 0.167, 'E5': 0.333, 'G5': 0.500},
        'F#5': {'D5': 0.500, 'G5': 0.500},
        'E-5': {'C5': 0.190, 'D5': 0.571, 'E-5': 0.143, 'F5': 0.095},
        'B-4': {'A4': 0.106, 'B-4': 0.277, 'C5': 0.234, 'D5': 0.298, 'E-5': 0.064, 'G4': 0.021},
        'B-5': {'A5': 1.000},
        'D4': {'C4': 0.100, 'E4': 0.500, 'G4': 0.400},
        'C4': {'C4': 1.000},
    }

class MelodyMinorA(ur.ItemPitchMarkov):
    AMBITUS = ['G3', 'D5']
    AMBITUS_INITIAL = ['A3', 'C5']
    STATES = ['E4', 'A4', 'F4', 'G4', 'D4', 'B4', 'C5', 'D5', 'A-4', 'F#4', 'E5', 'B-4', 'E-4', 'G#4', 'G5', 'F5', 'C4', 'B3', 'C#4']
    INITIAL = ['C4', 'E4', 'A4', 'C5']
    FINAL = STATES

    TRANSITIONS = {
        'E4': {'A-4': 0.010, 'A4': 0.060, 'C5': 0.010, 'D4': 0.150, 'E4': 0.570, 'F#4': 0.020, 'F4': 0.060, 'G#4': 0.070, 'G4': 0.050},
        'A4': {'A-4': 0.033, 'A4': 0.346, 'B-4': 0.052, 'B4': 0.105, 'C5': 0.085, 'E4': 0.111, 'F4': 0.046, 'G4': 0.222},
        'F4': {'A4': 0.071, 'C5': 0.018, 'D4': 0.089, 'E-4': 0.036, 'E4': 0.161, 'F4': 0.411, 'G4': 0.214},
        'G4': {'A4': 0.185, 'B-4': 0.036, 'B4': 0.012, 'C5': 0.012, 'D4': 0.012, 'D5': 0.006, 'E-4': 0.012, 'E4': 0.065, 'F#4': 0.071, 'F4': 0.083, 'G4': 0.506},
        'D4': {'C#4': 0.032, 'C4': 0.161, 'D4': 0.468, 'E4': 0.242, 'F#4': 0.016, 'G4': 0.081},
        'B4': {'A4': 0.357, 'B4': 0.262, 'C5': 0.262, 'D5': 0.024, 'G4': 0.095},
        'C5': {'A4': 0.164, 'B-4': 0.127, 'B4': 0.236, 'C5': 0.236, 'D5': 0.055, 'E5': 0.036, 'G4': 0.145},
        'D5': {'A4': 0.154, 'C5': 0.462, 'D5': 0.231, 'E4': 0.154},
        'A-4': {'A-4': 0.364, 'A4': 0.455, 'E4': 0.182},
        'F#4': {'A-4': 0.048, 'D4': 0.048, 'F#4': 0.238, 'F4': 0.048, 'G4': 0.619},
        'E5': {'D5': 0.125, 'E4': 0.500, 'G#4': 0.375},
        'B-4': {'A4': 0.353, 'B-4': 0.353, 'C5': 0.088, 'D5': 0.029, 'F#4': 0.029, 'G4': 0.147},
        'E-4': {'D4': 0.143, 'E-4': 0.429, 'E4': 0.143, 'F4': 0.286},
        'G#4': {'A4': 0.133, 'D4': 0.133, 'E4': 0.200, 'G#4': 0.533},
        'G5': {'B4': 0.667, 'G4': 0.333},
        'F5': {'D4': 1.000},
        'C4': {'A4': 0.069, 'B3': 0.207, 'C4': 0.448, 'D4': 0.207, 'F4': 0.069},
        'B3': {'B3': 0.143, 'C4': 0.714, 'F4': 0.143},
        'C#4': {'D4': 1.000},
    }

class MelodyMinorT(ur.ItemPitchMarkov):
    AMBITUS = ['B2', 'A4']
    AMBITUS_INITIAL = ['C3', 'E4']
    STATES = ['E4', 'C4', 'D4', 'B3', 'A3', 'A-3', 'G4', 'A-4', 'A4', 'G3', 'F3', 'E3', 'F#4', 'B-3', 'E-4', 'F4', 'B-4', 'F#3', 'G#3', 'D3']
    INITIAL = ['E3', 'A3', 'C4', 'E4']
    FINAL = STATES

    TRANSITIONS = {
        'E4': {'A3': 0.011, 'A4': 0.022, 'B3': 0.022, 'C4': 0.140, 'D4': 0.301, 'E4': 0.409, 'F4': 0.022, 'G4': 0.075},
        'C4': {'A3': 0.057, 'B-3': 0.078, 'B3': 0.248, 'C4': 0.234, 'D4': 0.234, 'E-4': 0.014, 'E4': 0.113, 'F4': 0.014, 'G3': 0.007},
        'D4': {'A3': 0.015, 'B-3': 0.083, 'B3': 0.015, 'C4': 0.316, 'D4': 0.331, 'E-4': 0.068, 'E4': 0.113, 'F4': 0.045, 'G4': 0.015},
        'B3': {'A3': 0.351, 'B3': 0.247, 'C4': 0.234, 'E3': 0.026, 'E4': 0.091, 'G#3': 0.013, 'G3': 0.039},
        'A3': {'A-3': 0.045, 'A3': 0.259, 'B-3': 0.071, 'B3': 0.143, 'C4': 0.062, 'D3': 0.018, 'D4': 0.018, 'E3': 0.018, 'E4': 0.036, 'F#3': 0.018, 'F3': 0.009, 'G#3': 0.062, 'G3': 0.241},
        'A-3': {'A3': 0.375, 'B3': 0.375, 'E3': 0.250},
        'G4': {'A-4': 0.043, 'A4': 0.087, 'B-4': 0.022, 'C4': 0.043, 'D4': 0.087, 'E4': 0.130, 'F4': 0.087, 'G4': 0.500},
        'A-4': {'A-4': 0.600, 'A4': 0.400},
        'A4': {'A4': 0.167, 'E4': 0.250, 'F#4': 0.167, 'G4': 0.417},
        'G3': {'A-3': 0.048, 'A3': 0.254, 'B-3': 0.095, 'C4': 0.095, 'D4': 0.032, 'E3': 0.048, 'E4': 0.016, 'F#3': 0.048, 'F3': 0.143, 'G3': 0.222},
        'F3': {'G3': 1.000},
        'E3': {'A3': 0.476, 'C4': 0.190, 'E3': 0.333},
        'F#4': {'F#4': 0.250, 'G4': 0.750},
        'B-3': {'A3': 0.269, 'B-3': 0.308, 'C4': 0.231, 'D4': 0.115, 'E-4': 0.019, 'F4': 0.019, 'G3': 0.038},
        'E-4': {'D4': 0.471, 'E-4': 0.118, 'F4': 0.294, 'G4': 0.118},
        'F4': {'A4': 0.038, 'C4': 0.115, 'D4': 0.192, 'E-4': 0.115, 'E4': 0.115, 'F#4': 0.038, 'F4': 0.231, 'G4': 0.154},
        'B-4': {'A4': 1.000},
        'F#3': {'G3': 1.000},
        'G#3': {'A3': 0.444, 'E3': 0.444, 'G#3': 0.111},
        'D3': {'G3': 1.000},
    }

class MelodyMinorB(ur.ItemPitchMarkov):
    AMBITUS = ['E2', 'D4']
    AMBITUS_INITIAL = ['A2', 'C4']
    STATES = ['E4', 'A3', 'F3', 'D3', 'E3', 'A-3', 'G3', 'C4', 'D4', 'B3', 'C3', 'F#3', 'B-3', 'C#3', 'E-3', 'E-4', 'A2', 'B2', 'G2', 'F2', 'E2']
    INITIAL = ['A2', 'C3', 'E3', 'A3', 'C3']
    FINAL = STATES

    TRANSITIONS = {
        'E4': {'A3': 0.444, 'E3': 0.333, 'E4': 0.222},
        'A3': {'A3': 0.423, 'B-3': 0.046, 'B3': 0.054, 'C4': 0.046, 'D3': 0.031, 'E3': 0.085, 'E4': 0.008, 'F3': 0.038, 'G3': 0.269},
        'F3': {'A3': 0.017, 'B-3': 0.052, 'C3': 0.052, 'D3': 0.121, 'E-3': 0.017, 'E3': 0.259, 'F#3': 0.017, 'F3': 0.241, 'G3': 0.224},
        'D3': {'A3': 0.026, 'B-3': 0.039, 'C3': 0.039, 'D3': 0.299, 'E-3': 0.026, 'E3': 0.208, 'F3': 0.065, 'G2': 0.026, 'G3': 0.273},
        'E3': {'A-3': 0.020, 'A2': 0.184, 'A3': 0.245, 'D3': 0.031, 'E3': 0.378, 'E4': 0.020, 'F#3': 0.020, 'F3': 0.102},
        'A-3': {'A-3': 0.429, 'A3': 0.429, 'F#3': 0.143},
        'G3': {'A-3': 0.011, 'A2': 0.011, 'A3': 0.119, 'B-3': 0.040, 'B2': 0.011, 'B3': 0.011, 'C3': 0.034, 'C4': 0.028, 'D3': 0.114, 'E-3': 0.006, 'E3': 0.011, 'F3': 0.085, 'G2': 0.011, 'G3': 0.506},
        'C4': {'A3': 0.061, 'B-3': 0.020, 'B3': 0.102, 'C3': 0.020, 'C4': 0.388, 'D4': 0.204, 'E-4': 0.020, 'E3': 0.020, 'F3': 0.020, 'G3': 0.143},
        'D4': {'B-3': 0.111, 'C4': 0.167, 'D3': 0.167, 'D4': 0.389, 'E4': 0.167},
        'B3': {'A3': 0.353, 'B3': 0.176, 'C4': 0.412, 'G3': 0.059},
        'C3': {'A3': 0.019, 'B2': 0.074, 'C#3': 0.019, 'C3': 0.333, 'C4': 0.019, 'D3': 0.259, 'E3': 0.148, 'F2': 0.037, 'F3': 0.093},
        'F#3': {'E3': 0.200, 'G3': 0.800},
        'B-3': {'A3': 0.237, 'B-3': 0.421, 'C4': 0.184, 'G3': 0.158},
        'C#3': {'C#3': 0.500, 'D3': 0.500},
        'E-3': {'D3': 0.400, 'E-3': 0.200, 'F3': 0.400},
        'E-4': {'D4': 1.000},
        'A2': {'A2': 0.188, 'A3': 0.094, 'B2': 0.219, 'C3': 0.344, 'E3': 0.031, 'F#3': 0.031, 'F3': 0.031, 'G2': 0.062},
        'B2': {'A2': 0.308, 'C3': 0.538, 'E3': 0.154},
        'G2': {'A2': 0.231, 'C3': 0.385, 'F2': 0.231, 'G2': 0.154},
        'F2': {'G2': 1.000},
        'E2': {'A2': 0.667, 'F2': 0.333},
    }


class ScorerMelody(ur.ScorerOne):

    AMBITUS_LOW = 5
    AMBITUS_HIGH = 14
    AMBITUS_GOOD = 7

    def score_item(self, gen, _, __):
        score = 0

        # Ambitus
        ambitus = music.ambitus(gen.one)
        if ambitus < self.AMBITUS_LOW or ambitus > self.AMBITUS_HIGH:
            score -= 1
        elif ambitus > self.AMBITUS_GOOD:
            score += 0.5

        for i in range(len(gen.one)-2):
            a, b, c = gen.one[i:i+3]

            # Large intervals, then short contrary motion
            if music.interval(a, b) > 7 and music.interval(b, c) in [-1, -2]:
                score += 0.2
            if music.interval(a, b) < -7 and music.interval(b, c) in [1, 2]:
                score += 0.2

            # Too many repeated notes
            if a == b and b == c:
                score -= 0.2

        return score


class ScorerSectionsMelodyT(ur.ScorerOne):

    # Target some mean pitch, according to section
    # Not used now, RelativeScorerSectionMelody is better
    TARGET = {
        'A': (50, 57), 'a': (59, 70),
        'B': (59, 70), 'b': (50, 57),
        None: (50, 70),
    }

    def score_item(self, gen, _, struct):
        mean = music.mean(gen.one)
        tdown, tup = self.TARGET[struct] if struct in self.TARGET else self.TARGET[None]
        return -tools.distance_to_interval(mean, tdown, tup)

class RelativeScorerSectionMelody(ur.ScorerOne, ur.RelativeScorerSection):

    TARGET = {
        'A': (0.0, 0.4), 'a': (0.6, 1.0),
        'B': (0.6, 1.0), 'b': (0.0, 0.4),
        None: (0.0, 1.0),
    }

    def score_item(self, gen, _, struct):
        return music.mean(gen.one)

class ScorerFunc(ur.ScorerOne):

    def score_item(self, gen, _, __):

        different = len(set(gen.one))
        stars = len(list(filter(lambda x: '*' in x, gen.one)))

        score = different/len(gen.one)
        if stars in [1, 2, 3]:
            score += 0.5
        return score


class ScorerMelodySA(ScorerMelody):
    AMBITUS_LOW = 5
    AMBITUS_HIGH = 12
    AMBITUS_GOOD = 5


S2 = {
        '1': 2, '2': 2, '2.': 2, '4.': 2, '8.': 1, '4': 1, '8': 0, '16': 0, '4. 8': 2, '8 8': 0, '8. 16': 2,
        '2.': 2, '4.': 2, '8 8 8': 0, '8. 16 8': 0, '4 8': 0, '4 16 16': 0, '8 8 16 16': 0, '8 16 16 8': 0,
     }
S1 = {
        '1': 2, '2': 2, '2.': 2, '4.': 1, '8.': 1, '4': 1, '8': 0, '16': 0, '4. 8': 1, '8 8': 0, '8. 16': 1,
        '2.': 0, '4.': 2, '8 8 8': 0, '8. 16 8': 2, '4 8': 2, '4 16 16': 2, '8 8 16 16': 1, '8 16 16 8': 2,
     }
S0 = {
        '1': 0, '2': 0, '2.': 0, '4.': 0, '8.': 0, '4': 1, '8': 1, '16': 1, '4. 8': 0, '8 8': 1, '8. 16': 0,
        '2.': 0, '4.': 1, '8 8 8': 1, '8. 16 8': 0, '4 8': 1, '4 16 16': 0, '8 8 16 16': 1, '8 16 16 8': 1,
      }

class ScorerRhythmLyrics(ur.ScorerTwoSpanSequence):

    STRESSES = [
        ('!', S2),
        ('>>', S1),
        ('>',  S1),

        ('/', S1),
        ('.', S1),

        (';', S1),
        (',', S1),

        ('',  S0),
    ]


    def score_element(self, rhy, lyr):
        for (symbol, scores) in self.STRESSES:
            if symbol in lyr:
                if rhy in scores:
                    return scores[rhy]
                # return 0
        print('!', lyr, rhy)
        return 0


class ScorerRhythmMetrics(ur.ScorerOne):

    def score_item(self, gen, _, __):
        score = 0

        # music.duration(gen.one)
        pos = 0
        for r in gen.one:
            d = int(music.duration(r))
            if pos + d > 4:
                score -= .5
            if d > 1 and pos == 1:
                score -= .2
            if d == 1 and r != '4' and pos == 3:
                score += .2
            pos = (pos + d) % 4

        if pos in [0, 2]:
            score -= .5

        return score




class ScorerMelodyHarm(ur.ScorerTwoSequence):

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

        'i3': 'ace',
        'v3': 'egb',

        'i8': 'a',

        '*i9': 'aeb',
        '*III7': 'cegb',
        '*iv9': 'dae',
        'v8': 'e',
    }

    def score_element(self, mel, harm):
        # print (mel, harm, self.CHORDS[harm])
        if mel[0].lower() in self.CHORDS[harm]:
            return 1.0
        else:
            return 0.0

    def score_first_last_element(self, mel, harm):
        if mel[0].lower() in self.CHORDS[harm]:
            return 1.0
        else:
            return -20

class ScorerMelodyMelodyBelow(ur.ScorerTwoSequence):
    def score_element(self, mel1, mel2):
        if music.interval(mel1, mel2) < 0:
            return 0.0
        return 0.2

class ScorerMelodyMelodyAbove(ur.ScorerTwoSequence):
    def score_element(self, mel1, mel2):
        if music.interval(mel1, mel2) > 0:
            return 0.0
        return 0.2

class ScorerMelodyMelodyCross(ur.ScorerTwoSequenceAllPairs):

    CROSS = {
        0: 0.0,
        1: 0.5,
        2: 1.0,
        3: 1.0,
        4: 0.0,
        None: 0.0
    }

    LONGCROSS = {
        0: 0.0,
        1: 1.0,
        2: 1.0,
        3: 1.0,
        None: 0.0
    }

    def score_all_pairs(self, mel1mel2):
        crossings = 0
        long_crossings = 0 # at least three notes
        ss = 0
        ii = 0 # index of last crossing

        # Count the number of crossings
        for (i, (n1, n2)) in enumerate(mel1mel2):
            s = math.copysign(1, music.interval(n1, n2))
            if s:
                if ss and ss != s:
                    crossings += 1
                    if i >= ii + 3:
                        long_crossings += 1
                    ii = i
                ss = s

        # Score
        score = self.CROSS[crossings] if crossings in self.CROSS else self.CROSS[None]
        score += self.LONGCROSS[long_crossings] if long_crossings in self.LONGCROSS else self.LONGCROSS[None]

        return score


class ScorerMelodyMelody(ur.ScorerTwoSequenceIntervals):

    def score_element(self,
                      mel1a, mel1b,
                      mel2a, mel2b):


        # Detect doubling of voices
        if (music.interval(mel1a, mel2a) % 12) == 0:
            int1 = music.interval(mel1a, mel1b) % 12
            int2 = music.interval(mel2a, mel2b) % 12
            if int1 == int2:
                return -1.0

        return 1.0

class ScorerMelodyHarmRoot(ScorerMelodyHarm):

    SCORES = {
        None: -5.0,
        0: 1.0,
        1: 0.5,
        2: 0.5,
    }

    '''Favors 5, but still allows 6 and 64'''
    def score_element(self, mel, harm):
        if mel[0].lower() in self.CHORDS[harm]:
            i = self.CHORDS[harm].index(mel[0].lower())
            return self.SCORES[i]
        else:
            return self.SCORES[None]

    def score_last_element(self, mel, harm):
        if mel[0].lower() == self.CHORDS[harm][0]:
            return 0.0
        else:
            return -20.0

class ScorerFifthInBass(ScorerMelodyHarm):
    SCORES = {
        None: -5.0,
        0: 0.2,
        1: 0.2,
        2: 1.0,
    }

    def score_element(self, mel, harm):
        
        if mel[0].lower() in self.CHORDS[harm]:
            i = self.CHORDS[harm].index(mel[0].lower())
            return self.SCORES[i]
        else:
            return self.SCORES[None]