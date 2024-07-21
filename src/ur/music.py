
import music21

from typing import NewType, Protocol, Tuple, Optional, Self
from abc import ABC, abstractmethod

DURATIONS = {
    '1': 4, '2': 2, '4': 1, '8': .5, '16': 0.25,
    '1.': 6, '2.': 3, '4.': 1.5, '8.': .75
}

class Content(ABC):

    undefined: bool = False

    def is_undefined(self) -> bool:
        return self.undefined

    @classmethod
    @abstractmethod
    def create_undefined(cls, duration: float = 0.0) -> Self:
        pass


class Pitch(str, Content):
    def pc(self) -> str:
        ''' The Pitch class as English name in lower-case
        '''
        return self[0].lower()

    @classmethod
    def create_undefined(cls, duration: float = 0.0) -> Self:
        new = cls('~')
        new.undefined = True
        return new

class Schema(str, Content):
    @classmethod
    def create_undefined(cls, duration: float = 0.0) -> Self:
        new = cls('~')
        new.undefined = True
        return new

class Syllable(str, Content):
    @classmethod
    def create_undefined(cls, duration: float = 0.0) -> Self:
        new = cls('~')
        new.undefined = True
        return new

class Chord(str, Content):
    @classmethod
    def create_undefined(cls, duration: float = 0.0) -> Self:
        new = cls('~')
        new.undefined = True
        return new

class Temporal(Content):

    @abstractmethod
    def quarter_length(self) -> float:
        pass

class Duration(Temporal):

    def __init__(self, val: int | float | str):
        if isinstance(val, float | int):
            self.ql: float = val
        elif isinstance(val, str):
            self.notated: str = val
            self.ql = DURATIONS[val]

    def __str__(self):
        return str(self.ql)

    def quarter_length(self) -> float:
        return self.ql

    @classmethod
    def create_undefined(cls, duration: float = 0.0) -> Self:
        new = cls(duration)
        new.undefined = True
        return new

class Note(Temporal):

    def __init__(self, duration: Duration, pitch: Pitch):
        self.duration: Duration = duration
        self.pitch: Pitch = pitch

    def __str__(self):
        return u'(%s, %s)' % (self.duration, self.pitch)

    def quarter_length(self) -> float:
        return self.duration.quarter_length()

    @classmethod
    def create_undefined(cls, duration: float = 0.0) -> Self:
        new = cls(Duration(duration), Pitch.create_undefined())
        new.undefined = True
        return new


def quarters_per_bar(ts_str: str) -> float:
    ts: music21.meter.TimeSignature = music21.meter.TimeSignature(ts_str)
    return ts.beatDuration.quarterLength * ts.beatCount

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

def ternary(meter: str) -> bool:
    return meter == '6/8'

def beat(meter: str) -> float:
    if meter[-1] == '4':
        return 1.0
    elif meter == '6/8':
        return 1.5
    else: 
        raise NotImplementedError()    
    
def in_range(pitch: str, ambitus: Tuple[Pitch, Pitch], key: Optional[str] = None) -> bool:
    '''return true iff note is in ambitus (with inclusive bounds)
    '''
    n = music21.pitch.Pitch(pitch)
    if key:
        n = n.transpose(key)
    return (n.midi >= music21.pitch.Pitch(ambitus[0]).midi) and (n.midi <= music21.pitch.Pitch(ambitus[1]).midi)
    

def ambitus(mel):
    '''return ambitus as pitch difference
    '''
    mnotes = [music21.pitch.Pitch(n) for n in mel]
    return(max(mnotes).midi - min(mnotes).midi)

def pitch_mean(mel):
    minotes = [music21.pitch.Pitch(n).midi for n in mel]
    return(sum(minotes) / len(minotes))


def interval(n1, n2):
    ''' Interval in number of chromatic steps'''
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