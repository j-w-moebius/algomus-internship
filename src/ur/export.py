

import os
import music21 as m21
import datetime

DIR_OUT = '../../data/gen/'
TINY = "tinyNotation: 4/4 "

def export(code, title, melodies, annotations):

    score = m21.stream.Score()
    score.insert(0, m21.metadata.Metadata())
    score.metadata.title = title
    score.metadata.composer = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    n = 0
    for (name, (mel, lyrics)) in melodies:
        n += 1
        data = ''.join([f'{note:3s}' for note in mel])
        data = data.replace("a,", "A").replace("b,", "B")
        print(f'🎵 {name:5s}', data)
        part = m21.stream.Part()
        part = m21.converter.parse(TINY + data)
        if name == 'mel':
            for cl in part.measure(1).getElementsByClass('Clef'):
                part.measure(1).remove(cl)
            part.measure(1).insert(0, m21.clef.Treble8vbClef())
            part = part.transpose(-12)
        if name == 'melB':
            for cl in part.measure(1).getElementsByClass('Clef'):
                part.measure(1).remove(cl)
            part.measure(1).insert(0, m21.clef.BassClef())
            part = part.transpose(-12)
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
        score.append(part)

    # score.show('txt')
    os.system(f'mkdir -p {DIR_OUT}')
    f = f'{DIR_OUT}/{code}.mxl'
    print('==>', f)
    score.write('musicxml', f)
    os.system(f'verovio {f}')
    ff = f.replace('.mxl', '.svg')
    os.system(f'firefox {ff}')
    