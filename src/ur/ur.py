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

from typing import Any
from tools import *
from collections import defaultdict
from rich import print
import music
import flourish
import nonchord
import export

ALL = '0'

class Item(object):
    '''
    One generation item
    '''
    def __init__(self, one, context=None):
        self.one = one
        self.context = context

    def __len__(self):
        return len(self.one)

    def __repr__(self):
        s = ''
        if self.context:
            s += f'<{self.context}>'
        if type(self.one) == type([]):
            s += '[%s]' % ' '.join(map(str, self.one))
        else:
            s += str(self.one)

        return s

class Data(object):
    '''
    A collection of generation items, indexed by structure
    '''

    def __init__(self, item: Item = None, struct=None, data=None):
        self.data = data if data is not None else defaultdict(list)
        if item:
            self.data[struct if struct else ALL] = [ item ]
        self.context = ''

    def __getitem__(self, struct: str) -> Item:
        return self.data[struct]

    def __setitem__(self, struct: str, one: Item):
        self.data[struct] = one

    def update(self, other):
        self.data.update(other.data)

    def str(self, indent=''):
        s = ''
        for k in sorted(self.data.keys()):
            ind2 = indent + '>%s ' % k + self.context
            if len(self.data[k]) <= 1:
                s += ind2 + str(self.data[k]) + '\n'
            else:
                s += ellipsis_str(self.data[k], lines=True, indent=ind2)
        return s

    def __repr__(self):
        return self.str()

class Gen(object):

    def __init__(self, name = None, mods = None):
        self.gens = Data()
        self.mods = mods if mods else []
        self.key = None
        self.scorers = []
        self.structurers = []
        self.structure = [ ALL ]
        self.filters = []
        self.name = name if name else self.hash()
        self.flourish = flourish.FLOURISH
        self.setup()

    def set_key(self, key):
        self.key = key

    def setup(self):
        pass

    def reset(self):
        self.gens = Data()
        for m in self.mods:
            m.reset()
            
    def __iter__(self):
        yield self
        for m in self.mods:
            for mm in m:
                yield mm

    def item(self, gens_in=None, struct=None) -> Item:
        return Item(42)

    def len_to_gen(self, n=8, gens_in=None, struct=None):
        if gens_in:
            s0 = gens_in[struct if struct else ALL]
            if s0:
                n = len(s0[0])
        return n

    def one(self, gens_in=None, struct=None) -> Data:
        item = self.item(gens_in, struct)
        return Data(item=item, struct=struct)

    def one_filtered(self, gens_in, struct, n=500) -> Data:
        if not self.filters:
            one = self.one(gens_in, struct)
            return one

        sp = []
        for i in range(n):
            one = self.one(gens_in, struct)
            score = 0

            for filter, weight in self.filters:
                v2 = filter.mod2.gens[struct][0] if filter.two() else None
                score += filter.score_item(one[struct][0], v2) * weight
            sp += [ (score, one) ]
        average = sum(map (lambda x:x[0], sp)) / len(sp)
        sp.sort(key = lambda x:x[0])
        one = sp[-1][1]
        firsts = ' '.join([f'{x[0]:.3f}' for x in sp[-5:]])
        print(f'<{self.name}> struct {struct}, nb {n}, avg {average:.3f}, best {sp[-1][0]:.3f}, firsts {firsts}')
        one.context += f'={sp[-1][0]:.3f}'
        one[struct][0].context += '=' + f'={sp[-1][0]:.3f}'
        return one

    def gen(self, gens_in=None) -> Data:
        new = Data()

        structures = set(self.structure)
        if gens_in:
            structures = structures.union(set(gens_in.data.keys()))
        if len(structures) >= 2 and ALL in structures:
            structures.remove(ALL)

        for struct in structures:
            one = self.one_filtered(gens_in if gens_in else None, struct)
            for struct_child in one.data.keys():
                struct_dest = struct_child if struct_child != ALL else struct
                self.gens[struct_dest] += one[struct_child]
                new[struct_dest] += one[struct_child]
        return new

    def generate(self, n=20):
        for i in range(n):
            self.gen()

    def add_filter(self, scorer, weight):
        self.filters += [(scorer, weight)]

    def set_structure(self):
        for (s, mod) in self.structurers:
            s.structure_full = s.gens[ALL][0].one
            s.structure = s.structure_full.replace('-', '')
            mod.structure = s.structure
    def str_score(self, s):
        return f'{s:0.3f}'

    def score(self):
        for s in self.scorers:
            if not s.two():
                continue
            structures = set(s.mod1.gens.data.keys()).intersection(set(s.mod2.gens.data.keys()))
            print(f'Scoring {s}') # {structures}')
            for struct in structures:
                for (d1, d2) in zip(s.mod1.gens[struct], s.mod2.gens[struct]):
                    ss = s.score_item(d1, d2)
                    d2.context += ',' + self.str_score(ss)
                    # print("  ", struct, ss, d1, d2)

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

    def export(self, structure, rhythms=None, lyrics=None, annotation=False):
        out = []
        lyr = []
        for struct in structure:

            if struct == '-':
                out += [ ' r4  ']
                continue

            items = self.gens[struct][0].one
            if not annotation:
                items = list(map(music.abc_from_m21, items))

            rhy = rhythms.gens[struct][0].one if rhythms else None
            if lyrics:
                ly = lyrics.gens[struct][0].one
            i_ly = 0
            for i, item in enumerate(items):
                if not rhythms:
                    out += [ item ]
                    continue
                if annotation:
                    out += [ item ]
                    if rhy[i].strip() in ['2', '4. 8']:
                        out += [ '' ]
                    continue

                rhy_i = rhy[i]

                if lyrics:
                    n_ly = len(rhy_i.split())
                    lyr += ly[i_ly:i_ly+n_ly]
                    i_ly += n_ly

                if not annotation:
                    rhy_i, new_lyr, new_items = flourish.flourish(items, i, rhy_i, self.flourish)
                    lyr += new_lyr

                s = ''

                # Follow common rhythm
                for j, rh in enumerate(rhy_i.split(' ')):
                    if j >= 1:
                        if i < len(items)-1:
                            item = new_items[j-1] if new_items else nonchord.note_nonchord(item, items[i+1])

                    s += f' {item}{rh} '
                out += [ s ]

        return out, lyr

    def str(self, indent=0):
        ind = '    ' * indent
        s = ind
        s += f'<{self.id()}>\n'
        if self.gens:
            s += self.gens.str(ind)
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

    def one(self, gens_in=None, struct=None):
        m = pwchoice(self.mods)
        gs = m.gen(gens_in)
        gs.context = self.id() + '/' + gs.context
        return gs


class And(Gen):

    # def __init__(self, mods):
    #    super().__init__()
    #    self.mods = mods

    def one(self, gens_in=None, struct=None):
        d = Data()
        for m in self.mods:
            d.update(m.gen(gens_in))
        return d

### Item generators

class ItemChoice(Gen):

    def item(self, gens_in=None, struct=None):
        return Item(pwchoice(self.CHOICES))


class ItemLyricsChoiceFiles(ItemChoice):

    STRESS_WORDS = []

    def load(self):
        self.CHOICES = []
        for f in self.FILES:
            for l in open(f).readlines():
                text = l.replace('-', ' -').strip() + '/'
                words = []
                for w in text.split():
                    for ww in self.STRESS_WORDS:
                        if ww in w:
                            w = '!' + w
                    words += [w]
                if len(words) >= 4:
                    self.CHOICES += [words]
        print(f'<== {len(self.FILES)} files, {len(self.CHOICES)} lines')

    def xitem(self, gens_in=None, struct=None):
        f = random.choice(self.FILES)
        print('<==', f)

        text = ''
        for l in open(f).readlines():
            text += l.strip() + '/ '

        text = text.replace('-', ' -')
        words = text.split()[:50]
        return Item(words, self.id() + ':' + str(n))


class ItemSequence(Gen):
    
    def items(self, i, n):
        if i == n-1:
            try:
                return self.ITEMS_LAST
            except AttributeError:
                pass
        return self.ITEMS

    def item(self, gens_in=None, struct=None):
        n = self.len_to_gen(gens_in=gens_in, struct=struct)
        seq = []
        for i in range(n):
            seq += [pwchoice(self.items(i, n))]
        return Item(seq, self.id() + ':' + str(n))


class ItemSpanSequence(ItemSequence):

    def item(self, gens_in=None, struct=None):
        n = self.len_to_gen(gens_in=gens_in, struct=struct)
        seq = []
        i = 0
        while i < n:
            nn = 0
            while i + nn > n or (not nn):
                # Do not generate a last thing that go beyond n
                its = pwchoice(self.items(i, n))
                nn = len(its.split())
            seq += [its]
            i += nn
        return Item(seq, self.id() + f':{n/len(seq)}')



class ItemMarkov(Gen):

    def setup(self):
        self.initial = self.INITIAL
        self.transitions = self.TRANSITIONS

    def filter_state(self, state):
        if state is None:
            return False
        return True

    def item(self, gens_in=None, struct=None):

        i = 0
        n_min = self.len_to_gen(gens_in=gens_in, struct=struct)

        while i != n_min:
            # i == n_min : item has exact targeted length
            i = 0
            state = pwchoice(self.initial)
            emits = []

            emit = pwchoice(self.EMISSIONS[state])
            emits += [emit]
            i += 1
            while i < n_min or state not in self.FINAL:
                next_state = None
                while not self.filter_state(next_state):
                    next_state = pwchoice(self.transitions[state])
                state = next_state
                emit = pwchoice(self.EMISSIONS[state])
                emits += [emit]
                i += 1

        return Item(emits, self.id() + ':' + str(i))

class ItemPitchMarkov(ItemMarkov):

    def filter_state(self, pitch):
        # Redundant, but we may here implement melodic rules
        if pitch is None:
            return False
        return music.in_range(pitch, self.AMBITUS)

    def set_key(self, key):
        self.EMISSIONS = {
            x: {x: 1.00} for x in self.STATES
        }    
        self.key = key
        self.initial = self.INITIAL.copy()
        self.transitions = self.TRANSITIONS.copy()

        for n1 in list(self.transitions):
            for n2 in list(self.transitions[n1]):
                if not music.in_range(n2, self.AMBITUS, self.key) or '#' in n2 or '-' in n2:
                    # print(self.key, 'del', n1, n2)
                    del self.transitions[n1][n2]
                    if len(self.transitions[n1]) == 0:
                        del self.transitions[n1]
        for n in list(self.initial):
            if not music.in_range(n, self.AMBITUS_INITIAL, self.key):
                self.initial.remove(n)




### Scores



class ScorerOne(object):

    def __init__(self, mod):
        self.mod1 = mod

    def __str__(self):
        return f'<<{self.mod1.id()}>>'

    def two(self):
        return False

    def score(self, gens1: Data):
        for struct in gens1.data.keys():
            self.score_item(gens1[struct])

    def score_item(self, gen1, gen2):
        raise NotImplemented


class ScorerTwo(object):

    def __init__(self, mod1, mod2):
        self.mod1 = mod1
        self.mod2 = mod2

    def two(self):
        return True

    def __str__(self):
        return f'<<{self.mod1.id()} // {self.mod2.id()}>>'

    def score(self, gens1: Data, gens2: Data):
        # print(gens1, gens2)
        for struct in set(gens1.data.keys()).union(set(gens2.data.keys())):
            print(struct)
            self.score_item(gens1[struct], gens2[struct])

    def score_item(self, gen1, gen2):
        raise NotImplemented

class ScorerTwoSequence(ScorerTwo):

    def span(self, g):
        return g

    def score_element(self, e1, e2):
        raise NotImplemented

    def score_first_last_element(self, e1, e2):
        return self.score_element(e1, e2)

    def score_item(self, gen1: Item, gen2: Item, verbose=False):
        z = list(zip(self.span(gen1.one), self.span(gen2.one)))
        scores =  [self.score_first_last_element(z[0][0], z[0][1])]
        scores += [self.score_element(e1, e2) for (e1, e2) in z[1:-1]]
        scores += [self.score_first_last_element(z[-1][0], z[-1][1])]

        if verbose:
            print(scores, gen1, gen2)
        return sum(scores)/len(scores)

class ScorerTwoSequenceIntervals(ScorerTwo):

    def span(self, g):
        return g

    def score_element(self, e1, f1, e2, f2):
        raise NotImplemented

    def score_item(self, gen1: Item, gen2: Item, verbose=False):
        z = list(zip(self.span(gen1.one), self.span(gen2.one)))
        scores = []
        for i in range(len(z)-1):
            scores += [self.score_element(z[i][0], z[i+1][0], z[i][1], z[i+1][1]) ]

        if verbose:
            print(scores, gen1, gen2)
        return sum(scores)/len(scores)



class ScorerTwoSpanSequence(ScorerTwoSequence):
    def span(self, g):
        return ' '.join(g).split()

### Model

class Model(And):

    def __getitem__(self, name):
        for m in self:
            if m.name == name:
                return m
        raise KeyError(name)

    def add(self, mod):
        self.mods += [mod]

    def scorer(self, scorer, mod1, mod2=None, weight=1):
        if mod2:
            sco = scorer(self[mod1], self[mod2])
        else:
            sco = scorer(self[mod1])
        self.scorers += [sco]
        self[mod1].add_filter(sco, weight)
        return sco

    def structurer(self, struct, mod):
        self.structurers += [(self[struct], self[mod])]

    def export(self, code, title, structure, rhythms, lyrics, mods_melodies, mods_annots):
        print('Exporting...')
        melodies = [(mod, self[mod].export(structure, rhythms, lyrics=lyrics)) for mod in mods_melodies]
        annots   = [(mod, self[mod].export(structure, rhythms, annotation=True)) for mod in mods_annots]
        export.export(code, title, melodies, annots, self.key)