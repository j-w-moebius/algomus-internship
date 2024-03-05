
import music21

def in_range(note, ambitus):
    return (music21.pitch.Pitch(note) >= music21.pitch.Pitch(ambitus[0])) and (music21.pitch.Pitch(note) <= music21.pitch.Pitch(ambitus[1]))

def abc_from_m21(note):
    note = note.replace('#', '').replace('-', '')
    n = note[0].lower()
    oct = int(note[1])
    print(note)
    if oct < 4:
        n += ("," * (4-oct))
    if oct > 4:
        n += ("'" * (oct-4))
    return n