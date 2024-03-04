from music21 import *
import os

# run this script to analyze horizontal interval frequencies in "The Scared Harp" collection


def compute_interval_freqs(s: stream.base.Score, freqs: dict[str, dict[str, int]], direction: str):
   
    for p in s.parts:
        for n in p.flatten().notes:
            succ = n.next("Note")
            if succ == None:
                continue
            this_pitch = n.pitches[0]
            next_pitch = succ.pitches[0] #if n or succ are chords (i.e., divisi [found rarely and only in octaves], just take the first)

            contribute = False
            if direction == "up":
                if this_pitch <= next_pitch:
                    contribute = True
            elif direction == "down":
                if this_pitch >= next_pitch:
                    contribute = True

            if contribute: 
                if this_pitch not in freqs.keys():
                    freqs[this_pitch] = {}
                successors = freqs[this_pitch]
                if next_pitch not in successors.keys():
                    successors[next_pitch] = 1
                else:
                    successors[next_pitch] = successors[next_pitch] + 1

# transpose the piece to C Major or a minor, depending on its mode
def normalize_key(s, mode, tonic):
    if mode == 'major':
        i = interval.Interval(tonic, pitch.Pitch('C'))
    elif mode == 'minor':
        i = interval.Interval(tonic, pitch.Pitch('A'))
    return s.transpose(i)

# analyze horizontal interval frequencies
# conditioned on one predecessor
# direction: restricts the pitch pairs that contribute to frequencies ('up' or 'down')
# mode: restricts the pieces that contribute to frequencies ('major' or 'minor')
def analyze_corpus(corpus_path: str, mode: str, direction: str) -> dict[str, dict[str, float]]:
    freqs = {}

    print(corpus_path)
    for filename in os.listdir(corpus_path):
        f = os.path.join(corpus_path, filename)
        print('<==', filename)
        if os.path.isfile(f):
            s = converter.parse(f)
            k = s.analyze('key')
            if mode == k.mode:
                normalized_s = normalize_key(s, k.mode, k.tonic)
                compute_interval_freqs(normalized_s, freqs, direction)


    # normalize absolute frequencies to get probabilites
    for (_, p_successors) in freqs.items():
        s = sum(p_successors.values())
        for (n, f) in p_successors.items():
            p_successors[n] = f / s
    
    return freqs

def pretty(freqs, nb=15):
    freqs_sorted = [(n, sorted(list(succ.items()), key=lambda f:str(f[0]))) for (n, succ) in freqs.items()]
    s = 'TRANSITIONS = {\n'
    for (n, succs) in freqs_sorted:
        s += f"  '{n}': " + '{'
        su = []
        for (data, freq) in succs[:nb]:
            su += [f"'{data}': {freq:.3f}"]
        s += ', '. join(su) + '},\n'

    s += '}'
    return s



dir_path = os.path.join(os.path.dirname(__file__), '../../data/the-scared-harp')
freqs = analyze_corpus(dir_path, 'major', 'down')
print(pretty(freqs))