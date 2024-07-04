import glob
import gabuzomeu
import random
import music
from music import Note, Pitch, Duration, Syllable
import music21 as m21
from music21.stream import Part, Score
from rich import print
import argparse
from typing import cast, Tuple, List
import os


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

def load_melody(filename: str) -> Part:
    c: Score = cast(Score, m21.converter.parse(filename))
    mel: Part = c.parts['tenor'].flatten()
    tonic_interval, _ = key_from_part(mel)

    if mel.clef == m21.clef.TrebleClef():
        mel = mel.transpose("P-8")

    return mel

def load_lyrics(file: str, stress_words: List[str]) -> List[List[Syllable]]:
    '''Load first stanza  from file as list of syllables, grouped by verse
    '''
    stanza: List[List[Syllable]] = []
    for l in open(file, encoding='utf-8').readlines(): 
        verse: List[Syllable] = []
        if l == '\n':
            break # only load first stanza
        text: str = l.replace('-', ' -').strip()
        for s in text.split():
            for ww in stress_words:
                if ww in s:
                    s = '!' + s
            verse += [Syllable(s)]
        stanza.append(verse)
    return stanza