
import random

NOTES = [
    "c,,", "d,,", "e,,", "f,,", "g,,", "a,,", "b,,",
    "c,", "d,", "e,", "f,", "g,", "a,", "b,",
    'c', 'd', 'e', 'f', 'g', 'a', 'b',
    "c'", "d'", "e'", "f'", "g'", "a'", "b'",
    "c''"
    ]

def note_index(n):
    if n not in NOTES:
        print('!', n)
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

def interval_second(n1, n2):
    return abs(note_index(n2) - note_index(n1)) == 1

def interval_third(n1, n2):
    return abs(note_index(n2) - note_index(n1)) == 2

def interval_fourth(n1, n2):
    return abs(note_index(n2) - note_index(n1)) == 3

def interval_fifth_up(n1, n2):
    return note_index(n2) - note_index(n1) == 4

def note_passing(n1, n2):
    return note_from_index((note_index(n1) + note_index(n2))//2)

def direction(n1, n2):
    if note_index(n2) > note_index(n1):
        return 1
    elif note_index(n2) < note_index(n1):
        return -1
    else:
        return random.choice([-1, 1])

def note_direction(n1, n2, nb):
    return note_projection(n1, direction(n1, n2), nb)
        
def note_projection(n1, dir, nb):
    return note_from_index(note_index(n1) + dir*nb)

def note_nonchord(n1, n2, always=False):
    '''
    Returns a possible nonchord note between n1 and n2
    '''
    if n1 == n2:
        if random.choice([True, False]) or always:
            return note_neighbor(n1)
    if interval_third(n1, n2):
        return note_passing(n1, n2)
    return n1

