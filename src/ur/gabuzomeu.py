

from tools import *

SYLLABES = ['ga', 'bu', 'zo', 'meu']

def word():
    l = pwchoice([(1, .20), (2, .40), (3, .30), (4, .10)])
    return ''.join([pwchoice(SYLLABES) for i in range(l)])

def sentence(woo):
    l = pwchoice([(2, .30), (3, .30), (4, .20), (5, .10), (6, .05   )])            
    s = ' '.join([word() for i in range(l)])
    if woo:
        s = 'woo ' + s
    return s.capitalize()
