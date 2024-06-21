

import os
import music21 as m21
import datetime
import random

from rich import print

from typing import List, Tuple
from music import Note

DIR_OUT = 'data/gen/'

INSTRUMENTS = {
    'melS': (m21.instrument.Vocalist(), m21.dynamics.Dynamic('mf')),
    'melA': (m21.instrument.Vocalist(), m21.dynamics.Dynamic('mf')),
    'mel': (m21.instrument.Vocalist(), m21.dynamics.Dynamic('f')),
    'melB': (m21.instrument.Vocalist(), m21.dynamics.Dynamic('mf')),
}

DURATIONS = {
    '1': 4, '2': 2, '4': 1, '8': .5, '16': 0.25,
    '1.': 6, '2.': 3, '4.': 1.5, '8.': .75
}
def m21duration(dur, dur_factor):
    return m21.duration.Duration(DURATIONS[dur] * dur_factor)

def export(filename: str, title: str, melodies: List[Tuple[str, List[Note]]], key: str, meter: str, svg: bool) -> None:

    score = m21.stream.Score()
    score.insert(0, m21.metadata.Metadata())
    score.metadata.title = title
    score.metadata.composer = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tempo: str = random.choice(['72', '80', '92'])
    
    # dur_factor: int = 2 if not '/8' in meter else 1
    
    for name, mel in melodies:

        # data = ''.join([f'{note:3s}' for note in mel])
        # print(f'🎵 {name:5s}', data)

        part = m21.stream.Part()
        part.partName = name
        part.partAbbreviation = name
        part.insert(0, m21.meter.TimeSignature(meter))
        part.insert(0, m21.tempo.MetronomeMark(number=tempo, referent=1.5 if '/8' in meter else 2))
        part.insert(0, m21.key.KeySignature(0))
        part.insert(0, m21.instrument.Vocalist())

        if name == 'fillinT':
            part.insert(0, m21.clef.Treble8vbClef())
        elif name == 'fillinB':
            part.insert(0, m21.clef.BassClef())
        else:
            part.insert(0, m21.clef.TrebleClef())

        for n in mel:
            note = m21.note.Note(n.pitch) if n.pitch != 'r' else m21.note.Rest()
            note.duration = m21.duration.Duration(n.duration)
            part.append(note)

        # part = part.transpose(key)
        part.makeMeasures(inPlace = True, innerBarline = m21.bar.Barline())
        part.makeBeams(inPlace = True)
        # part.show('txt')

        # if lyrics:
        #     print(f"📁 {' '.join(lyrics)}")
        #     for i, note in enumerate(part.flatten().getElementsByClass('Note')):
        #         try:
        #             note.lyric = lyrics[i]
        #         except:
        #             pass

        score.append(part)

    # for (name, (lyr, _)) in annotations:
    #     part = m21.stream.Part()
    #     part.insert(0, m21.clef.PercussionClef())
    #     part.insert(0, m21.layout.StaffLayout(staffLines=1))
    #     data = ''.join([f'{note:3s}' for note in lyr])
    #     print(f'🏷️ {name:5s}', data)

    #     for (i, ly) in enumerate(lyr):
    #         if 'r' in ly:
    #             continue
    #         ew = m21.expressions.TextExpression(ly)
    #         part.insert(i, ew)
    #     # score.append(part)

    # score.show('txt')
    dir = os.path.dirname(os.path.join(DIR_OUT, f'{filename}'))
    os.makedirs(dir, exist_ok=True)
    f: str = f'{DIR_OUT}/{filename}.mxl'

    print(f'[green]==> {f}')
    score.write('musicxml', f)

    if svg:
        ff = f.replace('.mxl', '.svg')
        print(f'[green]==> {ff}')
        os.system(f'verovio {f}')
        os.system(f'firefox {ff}')

    print()