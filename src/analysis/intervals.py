from music21 import *
import os

# run this script to analyze interval frequencies in "The Scared Harp" collection

# takes score s as input and make it contribute to a dictionary of absolute interval frequencies, interval_freqs 
def compute_interval_freqs(s: stream.base.Score, interval_freqs: dict[list[str], int]):
    parts = [p.flatten() for p in s.parts]

    d = s.highestTime # get piece duration

    for b in range(int(d)):
        pitch_list = []
        num_voices = len(parts)
        
        for i in range(num_voices):
            n = parts[i].getElementAtOrBefore(b)
            if not n.isNote:
                continue
            pitch_list.append(n.pitch)
            if num_voices == 4 and i == 0:
                pitch_list.append(n.pitch.transpose('-P8')) # treble part is also sung by men
            elif num_voices == 4 and i == 2:
                pitch_list.append(n.pitch.transpose('P8')) # tenor part is also sung by women
            elif num_voices == 3 and i == 1:
                pitch_list.append(n.pitch.transpose('P8')) # tenor part is also sung by women
        if pitch_list == []:
            continue
        # find simplest enharmonic variant of the pitches
        # (otherwise, wrong intervals might be obtained, i.e., consider the chord D#, G#, C 
        # in an E flat major piece)
        pitch_list = analysis.enharmonics.EnharmonicSimplifier(pitch_list).bestPitches()
        c = chord.Chord(pitch_list)
        # identify and remove the lowest note
        bass = c.bass()
        c.remove(bass)
        # compute all intervals to bass, reduced to range P1-M7
        intervals = { interval.Interval(bass, n).simpleName for n in c.notes }
        intervals_immtbl = frozenset(intervals)
        if intervals_immtbl not in interval_freqs.keys():
            interval_freqs[intervals_immtbl] = 1
        else:
            interval_freqs[intervals_immtbl] = interval_freqs[intervals_immtbl] + 1


# compute dictionary of interval combinations and associated relative frequencies for a corpus 
# stored in corpus_path
def analyze_corpus(corpus_path: str) -> dict[list[str], float]:
    interval_freqs = {}

    print(corpus_path)
    for filename in os.listdir(corpus_path):
        f = os.path.join(corpus_path, filename)
        print('<==', filename)
        if os.path.isfile(f):
            s = converter.parse(f)
            compute_interval_freqs(s, interval_freqs)

    # normalize absolute frequencies to get probabilites
    s = sum(interval_freqs.values())
    for (i, f) in interval_freqs.items():
        interval_freqs[i] = f / s
    
    return interval_freqs

def pretty(freqs, nb=15):
    freqs_sorted = sorted(list(freqs.items()), key=lambda f:-f[1])
    s = ''
    for (data, freq) in freqs_sorted[:nb]:
        s += f'{freq:.3f} {data}\n'

    return s

dir_path = os.path.join(os.path.dirname(__file__), '../../data/the-scared-harp')
freqs = analyze_corpus(dir_path)
print(pretty(freqs))
