from music21 import *
import os

# run this script to analyze horizontal (unconditioned) interval frequencies in "The Scared Harp" collection


def compute_interval_freqs(s: stream.base.Score, freqs_list: list[dict[str, dict[str, int]]]):
    start = 0
    if len(s.parts) == 3: # we have: (alto, tenor, bass)
        start = 1   
    for (p_ind, p) in enumerate(s.parts, start):
        for n in p.flatten().notes:
            succ = n.next("Note")
            if succ == None:
                continue
            this_pitch = n.pitches[0]
            next_pitch = succ.pitches[0] #if n or succ are chords (i.e., divisi [found rarely and only in octaves], just take the first)
            
            if this_pitch not in freqs_list[p_ind].keys():
                freqs_list[p_ind][this_pitch] = {}
            successors = freqs_list[p_ind][this_pitch]
            if next_pitch not in successors.keys():
                successors[next_pitch] = 1
            else:
                successors[next_pitch] = successors[next_pitch] + 1

def normalize_key(s):
    k = s.analyze('key')
    if k.mode == 'major':
        i = interval.Interval(k.tonic, pitch.Pitch('C'))
    elif k.mode == 'minor':
        i = interval.Interval(k.tonic, pitch.Pitch('A'))
    return s.transpose(i)

def analyze_corpus(corpus_path: str) -> list[dict[str, dict[str, float]]]:
    freqs_list = [{}, {}, {}, {}]

    print(corpus_path)
    for filename in os.listdir(corpus_path):
        f = os.path.join(corpus_path, filename)
        print('<==', filename)
        if os.path.isfile(f):
            s = converter.parse(f)
            normalized_s = normalize_key(s)
            compute_interval_freqs(normalized_s, freqs_list)


    # normalize absolute frequencies to get probabilites
    for freqs in freqs_list:
        for (_, p_successors) in freqs.items():
            s = sum(p_successors.values())
            for (n, f) in p_successors.items():
                p_successors[n] = f / s
    
    return freqs_list

def pretty(freqs_list, nb=15):
    freqs_sorted = [[(n, sorted(list(succ.items()), key=lambda f:-f[1])) for (n, succ) in freqs.items()] for freqs in freqs_list]
    s = ''
    for i, freqs in enumerate(freqs_sorted):
        s += f'Voice {i + 1}:\n' 
        for (n, succs) in freqs:
            s += f'\tSuccessors of {n}:\n'
            for (data, freq) in succs[:nb]:
                s += f'\t\t{freq:.3f} {data}\n'

    return s



dir_path = os.path.join(os.path.dirname(__file__), '../../data/the-scared-harp')
freqs = analyze_corpus(dir_path)
print(pretty(freqs))