'''
A random experiment, now quite non-sense
'''

import ur
import models.harp
import glob

class WStructure(ur.ItemChoice):
    CHOICES = ['A-A-C', 'A-B-A', 'Q-A-A' ]

class WLyrics(ur.ItemLyricsChoiceFiles):
    FILES = glob.glob('data/lyrics-w/*.txt')
    MIN_LENGTH = 9

class WRhythm(ur.ItemSpanSequence):
    ITEMS_LAST = [
        ('2', 0.8),
        ('4', 0.5),
    ]
    ITEMS = [
                ('1 2', 0.1),
                ('8 8 1 4', 0.2),
                ('4 1 4', 0.2),
                ('1 4', 0.6),
                ('1 8 8 2', 0.20),
                ('1 16 16 16 16', 0.05),
                ('1 4. 8', 0.05),
            ]
    
class WFunc(ur.ItemMarkov):

    SOURCE = ''

    STATES = '1235yvVYZ'
    INITIAL = ['1', '1']
    FINAL = ['y', 'v', '5', 'V']

    TRANSITIONS = {
        '1': { '1': 0.62, '2': 0.10 },
        '2': { '1': 0.30, '2': 0.30, '3': 0.30 },
        '3': { '1': 0.13, '2': 0.10, '3': 0.18, '5': 0.38 },
        '5': { '1': 0.07, '2': 0.10, '3': 0.29, '5': 0.35, 'V': 0.30 },
        'v': { 'v': 0.80, 'y': 0.20 },
        'y': { 'y': 0.20 },

        'Z': { 'Z': 0.60, 'Y': 0.20 },
        'Y': { 'Z': 0.30, 'Y': 0.80, 'V': 0.20 },
        'V': { 'Y': 0.30, 'V': 0.30 },
    }

    EMISSIONS = {
            x: {x.upper(): 1.00} for x in STATES
    }

class WScorerRhythmMetrics(ur.ScorerOne):

    def score_item(self, gen, _):
        return 0

class WScorerMelodyHarm(models.harp.ScorerMelodyHarm):

    CHORDS = {
        '1': 'c',
        '2': 'cd',
        '3': 'cde',
        '5': 'cdeg',
        'V': 'dgac',
        'Y': 'eb',
        'Z': 'fcd',
    }
