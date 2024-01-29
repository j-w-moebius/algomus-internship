

import os
import music21 as m21
import datetime

TINY = "tinyNotation: 4/4 "

def export(melodies):

    score = m21.stream.Score()
    score.insert(0, m21.metadata.Metadata())
    score.metadata.title = "Generation"
    score.metadata.composer = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    n = 0
    for (name, mel) in melodies:
        n += 1
        data = ' '.join([f'{note:2s}' for note in mel])
        print(f'🎵 {name:5s}', data)
        part = m21.stream.Part()
        part = m21.converter.parse(TINY + data)
        if n == 2:
            for cl in part.measure(1).getElementsByClass('Clef'):
                part.measure(1).remove(cl)
            part.measure(1).insert(0, m21.clef.BassClef())
            part = part.transpose(-12)
            # part.show('txt')

        part = m21.stream.tools.removeDuplicates(part)
        score.append(part)
        # part.show('txt')
        # print()


    # score.show('txt')
    f = 'score.mxl'
    print('==>', f)
    score.write('musicxml', f)
    os.system(f'verovio {f}')
    ff = f.replace('.mxl', '.svg')
    os.system(f'firefox {ff}')
    