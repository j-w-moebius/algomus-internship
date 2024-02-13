
import random

NOTES = ['c', 'd', 'e', 'f', 'g', 'a', 'b', "c'", "d'", "e'", "g'"]

def note_index(n):
    if n not in NOTES:
        return None
    return NOTES.index(n)

def note_from_index(i):
    return NOTES[i]

def note_neighbor(n):
    i = note_index(n)
    if i is None:
        return n
    choices = []
    if i > 0:
        choices += [i-1]
    if i < len(NOTES)-1:
        choices += [i+1]
    return note_from_index(random.choice(choices))

def interval_third(n1, n2):
    return abs(note_index(n2) - note_index(n1)) == 2

def note_passing(n1, n2):
    return note_from_index((note_index(n1) + note_index(n2))//2)

def note_nonchord(n1, n2):
    '''
    Returns a possible nonchord note between n1 and n2
    '''
    if n1 == n2:
        if random.choice([True, False]):
            return note_neighbor(n1)
    if interval_third(n1, n2):
        return note_passing(n1, n2)
    return n1

