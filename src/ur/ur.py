#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  This file is part of "Ur" <http://www.algomus.fr>,
#  Co-creative generic music generation
#  Copyright (C) 2024 by Algomus team at CRIStAL 
#  (UMR CNRS 9189, Université Lille)
#
#  "Ur" is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  "Ur" is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with "Ur". If not, see <http://www.gnu.org/licenses/>

from tools import *
from collections import defaultdict
from rich import print

ALL = '0'

class Data(object):
    def __init__(self, data, context=None):
        self.data = data
        self.context = context

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        s = ''
        if self.context:
            s += f'<{self.context}>'
        if type(self.data) == type([]):
            s += '[%s]' % ' '.join(map(str, self.data))
        else:
            s += str(self.data)

        return s

class Gen(object):

    def __init__(self, name = None, mods = None):
        self.gens = defaultdict(list)
        self.mods = mods if mods else []
        self.scorers = []
        self.structurers = []
        self.structure = [ ALL ]
        self.filter = None
        self.name = name if name else self.hash()
        pass

    def reset(self):
        self.gens = defaultdict(list)
        for m in self.mods:
            m.reset()
            
    def __iter__(self):
        yield self
        for m in self.mods:
            for mm in m:
                yield mm

    def iter_gens(self):
        for s in self.structure:
            for g in self.gens[s]:
                yield g

    def one(self, gens_in=None):
        return Data(42)

    def one_filtered(self, gens_in, n=50):
        if not self.filter:
            return self.one(gens_in)
        props = [self.one(gens_in) for i in range(n)]
        sp = [(self.filter(p), p) for p in props]
        sp.sort(key = lambda x:x[0])
        one = sp[-1][1]
        one.context += '=' + str(sp[-1][0])
        return one

    def gen(self, gens_in=None):
        for struct in self.structure:
            one = self.one_filtered(gens_in)
            self.gens[struct] += [one]
        return one

    def generate(self, n=20):
        for i in range(n):
            self.gen()

    def set_filter(self, scorer):
        self.filter = scorer

    def set_structure(self):
        for (s, mod) in self.structurers:
            mod.structure = s.gens[ALL][0].data
            print(f'{mod} <<< {s.gens[ALL][0].data}')

    def score(self):
        for s in self.scorers:
            print('Scoring', s)
            for (d1, d2) in zip(s.mod1.iter_gens(), s.mod2.iter_gens    ()):
                print("  ", s.score(d1.data, d2.data), d1, d2)

    def learn(self):
        raise NotImplemented

    def load(self):
        raise NotImplemented

    def save(self):
        raise NotImplemented

    def hash(self):
        return hex(hash(id(self)))[-3:]

    def id(self):
        return f'{self.__class__.__name__}-{self.name}'

    def str(self, indent=0):
        ind = '    ' * indent
        s = ind
        s += f'<{self.id()}>\n'
        if self.gens:
            for k in self.gens.keys():
                ind2 = ind + '>%s ' % k
                if len(self.gens[k]) <= 1:
                    s += ind2 + str(self.gens[k]) + '\n'
                else:
                    s += ellipsis_str(self.gens[k], lines=True, indent=ind2)
            s += '\n'
        for m in self.mods:
            if indent < 6:
                s += m.str(indent + 1)
            else:
                s += '<...>'

        for sc in self.scorers:
            s += ind + str(sc) + '\n'
        return s

    def __str__(self):
        return self.str()


class Or(Gen):

    # def __init__(self, mods):
    #    super().__init__()
    #    self.mods = mods

    def one(self, gens_in=None):
        m = pwchoice(self.mods)
        g = m.gen(gens_in)
        g.context = self.id() + '/' + g.context
        return g


class And(Gen):

    # def __init__(self, mods):
    #    super().__init__()
    #    self.mods = mods

    def one(self, gens_in=None):
        return Data([m.gen(gens_in) for m in self.mods])


class Items(Gen):

    def one(self, gens_in=None):
        return Data(pwchoice(self.ITEMS))

class Sequence(Gen):

    def one(self, gens_in=None):
        n = 10 if not gens_in else len(gens_in)
        seq = []
        for i in range(n):
            seq += [pwchoice(self.ITEMS)]
        return Data(seq, self.id() + ':' + str(n))

class Markov(Gen):

    def one(self, gens_in=None):

        i = 0
        n_min = 10
        state = pwchoice(self.INITIAL)
        emits = []

        while i < n_min or state not in self.FINAL:
            emit = pwchoice(self.EMISSIONS[state])
            emits += [emit]
            state = pwchoice(self.TRANSITIONS[state])
            i += 1

        return Data(emits, self.id() + ':' + str(i))



class scorer(object):

    def __init__(self, mod1, mod2):
        self.mod1 = mod1
        self.mod2 = mod2

    def __str__(self):
        return f'<<{self.mod1.id()} // {self.mod2.id()}>>'

class seqScorer(scorer):

    def score(self, d1, d2, verbose=False):
        scores = [self.score_one(e1, e2) for (e1, e2) in zip(d1, d2)]
        if verbose:
            print(scores)
        return sum(scores)

class model(And):

    def __getitem__(self, name):
        for m in self:
            if m.name == name:
                return m
        raise KeyError(name)

    def add(self, mod):
        self.mods += [mod]

    def scorer(self, scorer, mod1, mod2):
        self.scorers += [scorer(self[mod1], self[mod2])]

    def structurer(self, struct, mod):
        self.structurers += [(self[struct], self[mod])]
