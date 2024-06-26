

import os
import music21 as m21
import datetime
import random

from rich import print

from typing import List, Tuple
from music import Note

DIR_OUT = 'data/gen/'

def export(filename: str, title: str, melodies: List[Tuple[str, List[Tuple[Note, str]]]], annots: List[str], key: str, meter: str, svg: bool) -> None:

    score = m21.stream.Score()
    score.insert(0, m21.metadata.Metadata())
    score.metadata.title = title
    score.metadata.composer = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tempo: str = '80'
    score.insert(0, m21.tempo.MetronomeMark(number=tempo, referent=1.5 if '/8' in meter else 1.0))
    
    # dur_factor: int = 2 if not '/8' in meter else 1
    
    for name, mel_lyr in melodies:

        # data = ''.join([f'{note:3s}' for note in mel])
        # print(f'🎵 {name:5s}', data)

        part = m21.stream.Part()
        part.partName = name
        part.partAbbreviation = name
        part.insert(0, m21.meter.TimeSignature(meter))
        part.insert(0, m21.key.KeySignature(0))
        part.insert(0, m21.instrument.Vocalist())

        if name == 'fillInT':
            part.insert(0, m21.clef.Treble8vbClef())
        elif name == 'fillInB':
            part.insert(0, m21.clef.BassClef())
        else:
            part.insert(0, m21.clef.TrebleClef())

        for n, l in mel_lyr:
            note = m21.note.Note(n.pitch) if n.pitch != 'r' else m21.note.Rest()
            note.duration = m21.duration.Duration(n.duration)
            if l:
                note.lyric = l
            part.append(note)

        part.transpose(key, inPlace=True)
        part.makeMeasures(inPlace = True, innerBarline = m21.bar.Barline())
        part.makeBeams(inPlace = True)
        # part.show('txt')

        score.append(part)

    # # for (name, (lyr, _)) in annots:
    # part = m21.stream.Part()
    # part.insert(0, m21.clef.PercussionClef())
    # part.insert(0, m21.layout.StaffLayout(staffLines=1))
    # # data = ''.join([f'{note:3s}' for note in lyr])
    # # print(f'🏷️ {name:5s}', data)

    # for (i, ly) in enumerate(annots):
    #     if 'r' in ly:
    #         continue
    #     ew = m21.expressions.TextExpression(ly)
    #     part.insert(i, ew)
    # score.append(part)

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