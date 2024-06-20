from music21 import *
import os

# run this script to analyze horizontal interval frequencies in "The Scared Harp" collection


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

def normalize_key(s, mode, tonic):
    '''transpose the piece to C Major or a minor, depending on its mode
    '''
    target = pitch.Pitch('C')
    if mode == 'minor':
        target = pitch.Pitch('A')
    i = interval.Interval(tonic, target)
    if i.semitones >= 7:
        i = i.complement
    elif i.semitones <= -7:
        i = i.complement
    return s.transpose(i)


def analyze_corpus(corpus_path: str, mode: str) -> list[dict[str, dict[str, float]]]:
    '''analyze horizontal interval frequencies
    conditioned on one predecessor
    mode: restricts the pieces that contribute to frequencies ('Major' or 'Minor')
    '''
    freqs_list = [{}, {}, {}, {}]

    print(corpus_path)
    for filename in os.listdir(corpus_path):
        f = os.path.join(corpus_path, filename)
        print('<==', filename)
        if os.path.isfile(f):
            s = converter.parse(f)
            k = s.analyze('key')
            if mode == k.mode:
                normalized_s = normalize_key(s, k.mode, k.tonic)
                compute_interval_freqs(normalized_s, freqs_list)


    # normalize absolute frequencies to get probabilites
    for freqs in freqs_list:
        for (_, p_successors) in freqs.items():
            s = sum(p_successors.values())
            for (n, f) in p_successors.items():
                p_successors[n] = f / s
    
    return freqs_list

def pretty(class_name, freqs, nb=15):
    freqs_sorted = [(n, sorted(list(succ.items()), key=lambda f:str(f[0]))) for (n, succ) in freqs.items()]

    pitches = [n for (n, _) in freqs_sorted]
    s = f"class {class_name}(ur.ItemMarkov):\n"
    s += '\tSTATES = ['
    su = []
    for p in pitches:
        su += [f"'{p}'"]
    s += ', '. join(su) + ']\n'
    s += '\tINITIAL = [...]\n'
    s += '\tFINAL = STATES\n\n'

    s += '\tTRANSITIONS = {\n'
    for (n, succs) in freqs_sorted:
        s += f"\t\t'{n}': " + '{'
        su = []
        for (data, freq) in succs[:nb]:
            su += [f"'{data}': {freq:.3f}"]
        s += ', '. join(su) + '},\n'
    s += '\t}\n\n'
    s += '\tEMISSIONS = {\n\t\tx: {x: 1.00} for x in STATES\n\t}\n\n'
    return s

voice_names = ["S", "A", "T", "B"]

dir_path = os.path.join(os.getcwd(), 'data/1991-denson')
for mode in ["Major", "Minor"]:
    freqs_list = analyze_corpus(dir_path, mode.lower())
    for (i, freqs) in enumerate(freqs_list):
        print(pretty(f"Melody{mode}{voice_names[i]}", freqs))