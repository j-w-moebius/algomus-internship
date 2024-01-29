from music21 import *
import os

# run this script to analyze horizontal (unconditioned) interval frequencies in "The Scared Harp" collection


def compute_interval_freqs(s: stream.base.Score, freqs_list: list[dict[str, int]]):
    start = 0
    if len(s.parts) == 3: # we have: (alto, tenor, bass)
        start = 1   
    for (p_ind, p) in enumerate(s.parts, start):
        for n in p.flatten().notes:
            succ = n.next("Note")
            if succ == None:
                continue
            pitch_list = analysis.enharmonics.EnharmonicSimplifier(
                [n.pitches[0], succ.pitches[0]] #if n or succ are chords (i.e., divisi [found rarely and only in octaves], just take the first)
                ).bestPitches()
            i = interval.Interval(pitch_list[0], pitch_list[1]).directedSimpleName
            if i not in freqs_list[p_ind].keys():
                freqs_list[p_ind][i] = 1
            else:
                freqs_list[p_ind][i] = freqs_list[p_ind][i] + 1


def analyze_corpus(corpus_path: str) -> dict[list[str], float]:
    freqs_list = [{}, {}, {}, {}]

    print(corpus_path)
    for filename in os.listdir(corpus_path):
        f = os.path.join(corpus_path, filename)
        print('<==', filename)
        if os.path.isfile(f):
            s = converter.parse(f)
            compute_interval_freqs(s, freqs_list)

    # normalize absolute frequencies to get probabilites
    for freqs in freqs_list:
        s = sum(freqs.values())
        for (i, f) in freqs.items():
            freqs[i] = f / s
    
    return freqs_list

def pretty(freqs_list, nb=15):
    freqs_sorted = [sorted(list(freqs.items()), key=lambda f:-f[1]) for freqs in freqs_list]
    s = ''
    for i, freqs in enumerate(freqs_sorted):
        s += f'Voice {i + 1}:\n' 
        for (data, freq) in freqs[:nb]:
            s += f'{freq:.3f} {data}\n'

    return s

dir_path = os.path.join(os.path.dirname(__file__), '../../data/the-scared-harp')
freqs = analyze_corpus(dir_path)
print(pretty(freqs))
