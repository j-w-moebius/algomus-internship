

import random
import bisect, itertools


def dict_to_list2(d):
    return list(d.items())

def weighted_choice(choices, weights):
    # From Python doc
    cumdist = list(itertools.accumulate(weights))
    x = random.random() * cumdist[-1]
    return choices[bisect.bisect(cumdist, x)]

def possibly_weighted_choice(l):
    if type(l) == type({}):
        l = dict_to_list2(l)    
    if type(l[0]) == type((0,0)):
        choices, weights = zip(*l)
        c = weighted_choice(choices, weights)
    else:
        c = random.choice(l)
    return c

pwchoice = possibly_weighted_choice

# ---------------------------------------------------------------------------------

def some_choices_int(choices, nb):
    if nb == 0:
        return []
    i = random.choice(choices)
    choices.remove(i)
    return [i] + some_choices_int(choices, nb-1)

def some_choices(choices, nb):
    """Randomly select 'nb' elements from the list choices
    """
    return [choices[i] for i in some_choices_int(list(range(len(choices))), nb)]


# ---------------------------------------------------------------------------------

def distance_to_interval(x, bot, top):
    if x < bot:
        return bot-x
    if x > top:
        return x-top
    return 0

# ---------------------------------------------------------------------------------


def ellipsis_list(l, start=5, end=0):
    if len(l) <= start + end:
        return l
    ll = []
    if start:
        ll += l[:start]
    ll += ['...']
    if end:
        ll += l[-end:]
    return ll

def ellipsis_str(l, start=5, end=0, lines=False, f=str, indent=''):
    s = indent + '(%d): ' % len(l)
    sep = '\n  ' + indent if lines else ', '
    if lines:
        s += sep
    s += sep.join(map(f, ellipsis_list(l, start, end)))
    if lines:
        s += '\n'
    return s


def pretty_dict(d):
    for k in self.data.keys():
        s += str(k) + ': [%s]' % ' '.join(map(str, self.data))        