
import music21

def in_range(note, ambitus, key=None):
    n = music21.pitch.Pitch(note)
    if key:
        n = n.transpose(key)
    return (n.midi >= music21.pitch.Pitch(ambitus[0]).midi) and (n.midi <= music21.pitch.Pitch(ambitus[1]).midi)

def abc_from_m21(note):
    note = note.replace('#', '').replace('-', '')
    n = note[0].lower()
    oct = int(note[1])
    if oct < 4:
        n += ("," * (4-oct))
    if oct > 4:
        n += ("'" * (oct-4))
    return n

def ambitus(mel):
    mnotes = [music21.pitch.Pitch(n) for n in mel]
    return(max(mnotes).midi - min(mnotes).midi)

def interval(n1, n2):
    return music21.pitch.Pitch(n2).midi - music21.pitch.Pitch(n1).midi

DURATION = {
  '2.': 3,
  '4.': 1.5,
  '8.': .75,
  '2': 2,
  '4': 1,
  '8': .5,
  '16': .25
}

def duration(r):
    return sum([DURATION[x] for x in r.split()])