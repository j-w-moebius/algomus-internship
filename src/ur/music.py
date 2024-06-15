
import music21

class Note:

    def __init__(self, duration: str, pitch: str):
        self.duration: str = duration
        self.pitch: str = pitch


def quantize_above(duration: float, meter: str) -> float:
    '''Snap duration to above or equal multiple of meter unit'''
    # metric unit in quarter notes
    metric_unit_quarters: float
    if meter[-1] == '4':
        metric_unit_quarters = 1
    elif meter [-1] == '8':
        metric_unit_quarters = 1.5
    
    multiple: float = metric_unit_quarters
    while multiple < duration:
        multiple += metric_unit_quarters

    return multiple

def in_range(note, ambitus, key=None):
    '''return true iff note is in ambitus (with inclusive bounds)
    '''
    n = music21.pitch.Pitch(note)
    if key:
        n = n.transpose(key)
    return (n.midi >= music21.pitch.Pitch(ambitus[0]).midi) and (n.midi <= music21.pitch.Pitch(ambitus[1]).midi)
    

def ambitus(mel):
    '''return ambitus as pitch difference
    '''
    mnotes = [music21.pitch.Pitch(n) for n in mel]
    return(max(mnotes).midi - min(mnotes).midi)

def mean(mel):
    minotes = [music21.pitch.Pitch(n).midi for n in mel]
    return(sum(minotes) / len(minotes))


def interval(n1, n2):
    return music21.pitch.Pitch(n2).midi - music21.pitch.Pitch(n1).midi

DURATION = {
  '1.': 6,
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