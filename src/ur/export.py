

import os
import music21 as m21
import datetime
import random

from rich import print

DIR_OUT = '../../data/gen/'

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
def m21duration(dur):
    return m21.duration.Duration(DURATIONS[dur])

def export(code, title, melodies, annotations, key, meter, svg):

    score = m21.stream.Score()
    score.insert(0, m21.metadata.Metadata())
    score.metadata.title = title
    score.metadata.composer = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tempo = random.choice(['72', '80', '92'])
    
    n = 0
    for (name, (mel, lyrics)) in melodies:
        n += 1
        data = ''.join([f'{note:3s}' for note in mel])
        print(f'🎵 {name:5s}', data)

        part = m21.stream.Part()
        part.partName = name
        part.partAbbreviation = name
        part.insert(0, m21.meter.TimeSignature(meter))
        part.insert(0, m21.tempo.MetronomeMark(number=tempo))
        part.insert(0, m21.key.KeySignature(0))
        if name in INSTRUMENTS:
            part.insert(0, INSTRUMENTS[name][0])
            part.insert(0, INSTRUMENTS[name][1])

        if name == 'mel':
            part.insert(0, m21.clef.Treble8vbClef())
        elif name == 'melB':
            part.insert(0, m21.clef.BassClef())
        else:
            part.insert(0, m21.clef.TrebleClef())

        for tnotes in mel:
            for tnote in tnotes.strip().split():
                pitch, dur = tnote.split('$')
                note = m21.note.Note(pitch) if pitch != 'r' else m21.note.Rest()
                note.duration = m21duration(dur)
                part.append(note)

        part = part.transpose(key)
        part.makeMeasures(inPlace = True, innerBarline = m21.bar.Barline())
        part.makeBeams(inPlace = True)
        # part.show('txt')

        if lyrics:
            print(f"📁 {' '.join(lyrics)}")
            for i, note in enumerate(part.flatten().getElementsByClass('Note')):
                try:
                    note.lyric = lyrics[i]
                except:
                    pass

        score.append(part)

    for (name, (lyr, _)) in annotations:
        part = m21.stream.Part()
        part.insert(0, m21.clef.PercussionClef())
        part.insert(0, m21.layout.StaffLayout(staffLines=1))
        data = ''.join([f'{note:3s}' for note in lyr])
        print(f'🏷️ {name:5s}', data)

        for (i, ly) in enumerate(lyr):
            if 'r' in ly:
                continue
            ew = m21.expressions.TextExpression(ly)
            part.insert(i, ew)
        # score.append(part)

    # score.show('txt')
    dir = os.path.dirname(os.path.join(DIR_OUT, f'{code}'))
    os.makedirs(dir, exist_ok=True)
    f = f'{DIR_OUT}/{code}.mxl'

    print(f'[green]==> {f}')
    score.write('musicxml', f)

    if svg:
        ff = f.replace('.mxl', '.svg')
        print(f'[green]==> {ff}')
        os.system(f'verovio {f}')
        os.system(f'firefox {ff}')

    print()