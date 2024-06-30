#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  This file is part of "Ur" <http://www.algomus.fr>,
#  Co-creative generic music generation
#  Copyright (C) 2024 by Algomus team at CRIStAL 
#  (UMR CNRS 9189, Université Lille)
#
#  Contributors:
#   - Mathieu Giraud
#   - Ken Déguernel
#   - Romain Carl
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

from __future__ import annotations
from typing import Any, List, Generic, Type
from tools import *
from collections import defaultdict
from rich import print
import music as m
import flourish
import nonchord
import export
import tools

from trees import *

# Result type
R = TypeVar('R')

class Interval:
    def __init__(self, min: int = 0, max: Optional[int] = None):
        self.min: int = min
        self.max: Optional[int] = max

    @overload
    def __contains__(self, item: Interval) -> bool:
        pass

    @overload
    def __contains__(self, item: int) -> bool:
        pass

    def __contains__(self, item: Interval | int) -> bool:
        if isinstance(item, int):
            if (item < self.min) or \
               (self.max and item > self.max):
                return False
        elif isinstance(item, slice):
            if (item.min < self.min) or \
               (self.max and item.max and item.max > self.max) or \
                (self.max and not item.max):
                return False 
        return True


class Rule(Generic[R]):
    LIST_ARGS: List[Tuple[type, Interval]] = []
    ARGS: List[type] = []

    T = TypeVar('T')

    def __init__(self, vps: List[ViewPoint]) -> None:
        self.vps: List[ViewPoint] = vps

    def __call__(self, *args: T) -> R:
        raise NotImplementedError()

    def check_args(self, *args: T) -> None:
        if len(args) != len(self.LIST_ARGS) + len(self.ARGS):
            raise RuntimeError("Number of specified and of passed arguments do not match")
        for (i, (a, (t, s))) in enumerate(zip(args, self.LIST_ARGS)):
            if not isinstance(a, List):
                raise RuntimeError("Passed argument is not a list")

            if len(a) not in s or len(a) == 0:
                raise RuntimeError("Passed lists are not of specified length")
            if not isinstance(a[0], t):
                raise RuntimeError("Passed argument list is not of specified type")
        if len(self.LIST_ARGS) == 0:
            i = 0
        else:
            i += 1
        for (a, t) in zip(args[i:], self.ARGS):
            if not isinstance(a, t):
                raise RuntimeError("Passed argument is not of specified type")

    def get_range(self, _vp: ViewPoint) -> Optional[Interval]:
        for (i, vp) in enumerate(self.vps):
            if vp == _vp:
                return self.LIST_ARGS[i][1]
        raise None

### Producers

class Producer(Rule[List[List[C]]]):

    OUT_COUNT: Interval

    def __init__(self, vp_out: ViewPoint, vps_in: List[ViewPoint], fixedness: float):
        self.vp = vp_out
        self.fixedness = fixedness
        super().__init__(vps_in)


class Enumerator(Producer[C]):

    ARGS = [Interval]

    def __call__(self, *list_args: List[T], len_to_gen: Interval) -> List[List[C]]:
        self.check_args(*list_args, len_to_gen)
        return self.enumerate(*list_args, len_to_gen=len_to_gen)

    def enumerate(*list_args: List[T], len_to_gen: Interval) -> List[List[C]]:
        raise NotImplementedError()

class RandomizedProducer(Producer[C]):

    ARGS = [Interval, int]

    def __call__(self, *list_args: List[T], len_to_gen: Interval, batch_size: int) -> List[List[C]]:
        self.check_args(*list_args, len_to_gen, batch_size)
        return [self.produce(*list_args, len_to_gen=len_to_gen) for i in range(batch_size)]

    def produce(self, *list_args: List[T], len_to_gen: Interval) -> List[C]:
        raise NotImplementedError()



### Constraints

class Evaluator(Rule[R]):
    pass


class Constraint(Evaluator[bool]):
    def __call__(self, *list_args: List[T]) -> bool:
        self.check_args(*list_args)
        return self.valid(*list_args)

    def valid(self, *list_args: List[T]) -> bool:
        raise NotImplementedError()

    

### Scores

class Scorer(Evaluator[float]):
    def __init__(self, vps: List[ViewPoint], weight: float = 1.0):
        self.weight: float = weight
        super().__init__(vps)

    def __call__(self, *list_args: List[T]) -> float:
        self.check_args(*list_args)
        return self.score(*list_args)

    def score(self, *list_args: List[T]) -> float:
        raise NotImplementedError()


class Generator(Generic[C]):

    BATCH_SIZE = 100
   # S = TypeVar('S', bound=m.Content)

    def __init__(self, node: RefinementNode) -> None:
        # the generated data
        self.gens: List[Tuple[List[C], float]] = [] # TODO: Maybe CumuList ?
        self.node: RefinementNode = node
        self.producers: List[Producer] = []
        self.constraints: List[Constraint] = []
        self.scorers: List[Scorer] = []
        # self.setup()

    def call_prod(self, prod: Producer[C]) -> List[List[C]]:
        list_args = [vp[self.node.start:self.node.end] for vp in prod.vps]
        len_to_gen: Interval
        if self.node.vp.fixed_count():
            len_to_gen = Interval(self.node.get_elt_count(), self.node.get_elt_count()) 
        else:
            len_to_gen = Interval(1)
        if len_to_gen not in prod.OUT_COUNT:
            raise RuntimeError(f"Producer {prod.__class__.__name__} can't generate the specified number of elements.")
        if isinstance(prod, RandomizedProducer):
            return prod(*list_args, len_to_gen=len_to_gen, batch_size=self.BATCH_SIZE)
        else:
            assert isinstance(prod, Enumerator)
            return prod(*list_args, len_to_gen=len_to_gen)
            

    def call_eval(self, eval: Evaluator[R], generated: List[C], window_start: Optional[Index] = None, window_end: Optional[Index] = None) -> R:
        if window_start is None:
            window_start = self.node.start
        if window_end is None:
            window_end = self.node.end
        args = []
        for vp in eval.vps:
            if self.node.vp == vp:
                start: int = window_start.pos - self.node.start.pos
                end: int = window_end.pos - self.node.start.pos
                args.append(generated[start:end])
            else: 
                args.append(vp[window_start:window_end])
        return eval(*args)

    def generate(self) -> Tuple[List[C], float]:

        # call producers
        self.producers = self.node.vp.producers
        gens: List[List[C]] = []
        succeeding: List[List[C]] = []
        failing: List[Tuple[List[C], int]] = []
        for p in self.producers:
            gens += self.call_prod(p)

        window_start: Index = Index(0.0, 0, self.node)
        window_end: Index = Index(0.0, 0, self.node)

        # call constraints
        self.constraints = [c for c in self.node.vp.constraints]
        for g in gens:
            fail_count: int = 0
            for c in self.constraints:
                possible_positions = list(range(len(g)))
                for pos in possible_positions:
                    if not self.call_eval(c, g):
                        fail_count += 1
            if fail_count == 0:
                succeeding.append(g)
            else:
                failing.append((g, fail_count))
        
        if len(succeeding) == 0:
            failing.sort(key = lambda x: x[1])
            # TODO: refine
            raise NotImplementedError()

        # call scorers
        self.scorers = [s for s in self.node.vp.scorers \
                        if all([vp.initialized for vp in s.vps])]
        for g in succeeding:
            score: float = 0.0
            for s in self.scorers:
                r = s.get_range(self.node.vp)
                assert r
                subscore: float = 0.0
                if len(g) in r:
                    subscore += self.call_eval(s, g)
                elif len(g) < r.min:
                    pass # s only scores longer sequences; is not of interest
                else: # len(g) > r.max
                    assert r.max
                    possible_positions = list(range(0, len(g) - r.max, r.max))
                    for offset in possible_positions:
                        window_start.set_offset(offset)
                        window_end.set_offset(offset + r.max)
                        subscore += self.call_eval(s, g, window_start, window_end)
                    subscore = subscore / len(possible_positions)  
                score += subscore * s.weight
            self.gens.append((g, score))

        # sort
        self.gens.sort(key = lambda x: x[1], reverse = True)

        return (self.gens[0][0], self.producers[0].fixedness) # TODO: choose the right producer


#     def setup(self):
#         pass

#     def reset(self):
#         self.gens = Data()
#         for m in self.mods:
#             m.reset()

#     # iterate through models      
#     def __iter__(self):
#         yield self
#         for m in self.mods:
#             for mm in m:
#                 yield mm

#     def learn(self):
#         raise NotImplemented

#     def load(self):
#         raise NotImplemented

#     def save(self):
#         raise NotImplemented

#     def hash(self):
#         return hex(hash(id(self)))[-3:]

#     def id(self):
#         return f'{self.__class__.__name__}-{self.name}'

#     def export(self, structure, rhythms=None, lyrics=None, annotation=False, meter=None, modes=None):
#         out = []
#         lyr = []

#         if meter:
#             self.set_meter(meter)

#         for struct in structure:

#             if struct == '-':
#                 out += [ ' r$%s  ' % self.beat()]
#                 continue

#             items = self.gens[struct][0].one
#             rhy = rhythms.gens[struct][0].one if rhythms else None
#             if lyrics:
#                 ly = lyrics.gens[struct][0].one
#             i_ly = 0
#             for i, item in enumerate(items):
#                 if not rhythms:
#                     out += [ item ]
#                     continue
#                 if annotation:
#                     out += [ item ]
#                     if rhy[i].strip() in ['2', '4. 8']:
#                         out += [ '' ]
#                     continue

#                 rhy_i = rhy[i]

#                 if lyrics:
#                     n_ly = len(rhy_i.split())
#                     lyr += ly[i_ly:i_ly+n_ly]
#                     i_ly += n_ly

#                 if not annotation:
#                     rhy_i, new_lyr, new_items = flourish.flourish(items, i, rhy_i, self.flourish, self.ternary())
#                     lyr += new_lyr

#                 s = ''

#                 # Follow common rhythm
#                 for j, rh in enumerate(rhy_i.split(' ')):
#                     if j >= 1:
#                         if i < len(items)-1:
#                             item = new_items[j-1] if new_items else nonchord.note_nonchord(item, items[i+1])

#                     s += f' {item}${rh} '

#                 # Mode colouring
#                 if modes:
#                     mode = random.choice(modes)
#                     for (n, nn) in mode:
#                         s = s.replace(n, nn).replace(n.upper(), nn.upper())

#                 out += [ s ]

#         return out, lyr


# ### Item generators

# class ItemChoice(Gen):

#     def item(self, gens_in=None, struct=None):
#         return Item(pwchoice(self.CHOICES))


# class ItemLyricsChoiceFiles(ItemChoice):

#     STRESS_WORDS = []
#     MIN_LENGTH = 4

#     def load(self):
#         self.CHOICES = []
#         for f in self.FILES:
#             for l in open(f, encoding='utf-8').readlines():
#                 text = l.replace('-', ' -').strip() + '/'
#                 words = []
#                 for w in text.split():
#                     for ww in self.STRESS_WORDS:
#                         if ww in w:
#                             w = '!' + w
#                     words += [w]
#                 if len(words) >= self.MIN_LENGTH:
#                     self.CHOICES += [words]
#         print(f'<== Lyrics: {len(self.FILES)} files, {len(self.CHOICES)} lines')

#     def xitem(self, gens_in=None, struct=None):
#         f = random.choice(self.FILES)
#         print('<==', f)

#         text = ''
#         for l in open(f, encoding='utf-8').readlines():
#             text += l.strip() + '/ '

#         text = text.replace('-', ' -')
#         words = text.split()[:50]
#         return Item(words, self.id() + ':' + str(n))


# class ItemSequence(Gen):
    
#     def items(self, i, n):
#         if i == n-1:
#             try:
#                 return self.ITEMS_LAST
#             except AttributeError:
#                 pass
#         return self.ITEMS

#     def item(self, gens_in=None, struct=None):
#         n = self.len_to_gen(gens_in=gens_in, struct=struct)
#         seq = []
#         for i in range(n):
#             seq += [pwchoice(self.items(i, n))]
#         return Item(seq, self.id() + ':' + str(n))


# class ItemSpanSequence(ItemSequence):

#     def item(self, gens_in=None, struct=None):
#         n = self.len_to_gen(gens_in=gens_in, struct=struct)
#         seq = []
#         i = 0
#         while i < n:
#             nn = 0
#             while i + nn > n or (not nn):
#                 # Do not generate a last thing that goes beyond n
#                 its = pwchoice(self.items(i, n))
#                 nn = len(its.split())
#             seq += [its]
#             i += nn
#         return Item(seq, self.id() + f':{n/len(seq)}')  # ??

# Hidden State Type
S = TypeVar("S")

class HiddenMarkov(RandomizedProducer[C], Generic[S, C]):
    
    # INITIAL_S, FINAL_S : dict[str, list[str]]
    # structure-dependent initial and final states
    # INITIAL_S: Dict[str, List[str]]
    # FINAL_S: Dict[str, List[str]]

    OUT_COUNT = Interval(1)

    STATES: List[S]
    INITIAL: List[S]
    FINAL: List[S]

    TRANSITIONS: Dict[S, Dict[S, float]]
    EMISSIONS: Dict[S, Dict[C, float]]


    # def reset_to_struct(self, struct) -> None:
    #     '''Set INITIAL and FINAL to state lists associated to struct in 
    #     INTIIAL_S / FINAL_S (if given)
    #     '''
    #     # Incompatible with ItemPitchMarkov
    #     # To be used with Func
    #     if self.INITIAL_S:
    #         self.INITIAL = self.INITIAL_S[struct if struct in self.INITIAL_S else None]
    #     if self.FINAL_S:
    #         self.FINAL = self.FINAL_S[struct if struct in self.FINAL_S else None]

    # def setup(self):
    #     self.initial = self.INITIAL
    #     self.transitions = self.TRANSITIONS

    def __init__(self, vp_out: ViewPoint, vps_in: List[ViewPoint], fixedness: float):
        super().__init__(vp_out, vps_in, fixedness)

        # TODO: avoid this barbary (but type annotations system makes it difficult)
        self.TRANSITIONS = dict([(m.Pitch(s1), dict([(m.Pitch(s2), p) for s2, p in d.items()])) \
                                 for s1, d in self.TRANSITIONS.items()])
        self.STATES = [m.Pitch(s) for s in self.STATES]
        self.INITIAL = [m.Pitch(s) for s in self.INITIAL]
        self.FINAL = [m.Pitch(s) for s in self.FINAL]

        self.transitions: Dict[S, Dict[S, float]] = self.TRANSITIONS
        self.initial: List[S] = self.INITIAL

    def state_legal(self, state: Optional[S]) -> bool:
        '''Return whether state is legal
        '''
        return state is not None

    def produce(self, len_to_gen: Interval) -> List[C]:
        '''Return a sequence of emitted states
        '''

        i: int = 0

        while i not in len_to_gen:
            # otherwise the final states constraint has led to a too long sequence
            i = 0
            state: S = pwchoice(self.initial)
            emits: List[C] = []

            emit: C = pwchoice(self.EMISSIONS[state])
            emits.append(emit)
            i += 1
            while i < len_to_gen.min or state not in self.FINAL:
                next_state: Optional[S] = None
                while not self.state_legal(next_state):
                    try:
                        next_state = pwchoice(self.transitions[state])
                    except KeyError:
                        print(f"[red]! No transition for [yellow]{self.__class__.__name__} {state}")
                        raise
                assert next_state
                state = next_state
                emit = pwchoice(self.EMISSIONS[state])
                emits += [emit]
                i += 1

        return emits

class Markov(HiddenMarkov[C, C]):
    
    def __init__(self, vp_out: ViewPoint, vps_in: List[ViewPoint], fixedness: float):
        super().__init__(vp_out, vps_in, fixedness)
        self.EMISSIONS = {
            x: {x: 1.00} for x in self.STATES
        }

class PitchMarkov(Markov[m.Pitch]):

    AMBITUS: Tuple[m.Pitch, m.Pitch]
    INITIAL_AMBITUS: Tuple[m.Pitch, m.Pitch]

    def __init__(self, vp_out: ViewPoint, vps_in: List[ViewPoint], fixedness: float):
        super().__init__(vp_out, vps_in, fixedness)
        self.set_key(vp_out.model.key)

    def state_legal(self, pitch: m.Pitch) -> bool:
        # Redundant, but we may here implement melodic rules
        if pitch is None:
            return False
        return music.in_range(pitch, self.AMBITUS, self.key)

    def set_key(self, key: str) -> None:
        ''' Adapt transitions and states to key
        '''
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


# class ScorerOne(Scorer):
#     '''A scorer of one single model
#     '''
#     def __init__(self, mod):
#         self.mod1 = mod

#     def __str__(self):
#         return f'<<{self.mod1.id()}>>'

#     def score(self, gens1: Data):
#         for struct in gens1.data.keys():
#             self.score_item(gens1[struct], struct=struct)


# class ScorerTwo(Scorer):
#     '''A scorer of two models
#     '''
#     def __init__(self, mod1, mod2):
#         self.mod1 = mod1
#         self.mod2 = mod2

#     def two(self):
#         return True

#     def __str__(self):
#         return f'<<{self.mod1.id()} // {self.mod2.id()}>>'

#     def score(self, gens1: Data, gens2: Data):
#         # print(gens1, gens2)
#         for struct in set(gens1.data.keys()).union(set(gens2.data.keys())):
#             print(struct)
#             self.score_item(gens1[struct], gens2[struct], struct)


# class ScorerTwoSequence(ScorerTwo):
#     '''A scorer of two sequences with special first / last handling
#     '''

#     def span(self, g):
#         return g

#     def score_element(self, e1, e2):
#         raise NotImplemented

#     def score_first_last_element(self, e1, e2):
#         return self.score_element(e1, e2)

#     def score_first_element(self, e1, e2):
#         return self.score_first_last_element(e1, e2)
#     def score_last_element(self, e1, e2):
#         return self.score_first_last_element(e1, e2)

#     def score_item(self, gen1: Item, gen2: Item, struct=None, verbose=False):
#         '''Return average pair-wise score of zipped sequences'''
#         z = list(zip(self.span(gen1.one), self.span(gen2.one)))
#         scores =  [self.score_first_element(z[0][0], z[0][1])]
#         scores += [self.score_element(e1, e2) for (e1, e2) in z[1:-1]]
#         scores += [self.score_last_element(z[-1][0], z[-1][1])]

#         if verbose:
#             print(scores, gen1, gen2)
#         return sum(scores)/len(scores)

# class ScorerTwoSequenceAllPairs(ScorerTwoSequence):
#     '''A scorer of two sequences without special first / last handling
#     '''

#     def score_item(self, gen1: Item, gen2: Item, struct=None):
#         z = list(zip(self.span(gen1.one), self.span(gen2.one)))
#         return self.score_all_pairs(z)

#     def score_all_pairs(z):
#         raise NotImplemented

# class ScorerTwoSequenceIntervals(ScorerTwo):
#     '''A two-sequence scorer which takes into account the relation between two
#     neighbouring notes
#     '''

#     def span(self, g):
#         return g

#     def score_element(self, e1, f1, e2, f2):
#         raise NotImplemented

#     def score_item(self, gen1: Item, gen2: Item, struct=None, verbose=False):
#         z = list(zip(self.span(gen1.one), self.span(gen2.one)))
#         scores = []
#         for i in range(len(z)-1):
#             scores += [self.score_element(z[i][0], z[i+1][0], z[i][1], z[i+1][1]) ]

#         if verbose:
#             print(scores, gen1, gen2)
#         return sum(scores)/len(scores)


# class ScorerTwoSpanSequence(ScorerTwoSequence):
#     # ?? better call that flatten
#     def span(self, g):
#         return ' '.join(g).split()

# class RelativeScorer(Scorer):
#     '''Scores an item based on the comparison of its prescore to that of all
#     other items 
#     '''

#     def init(self):
#         # collection of all scores seen during generation
#         self.scores = []

#     def prescore_item(self, gen1, gen2, struct):
#         score = self.score_item(gen1, gen2, struct)
#         self.scores += [score]

#     def postscore_item(self, gen1, gen2, struct):
#         '''Evaluate gen1 and gen2 wrt how they score relatively to all scores
#         '''
#         bot = min(self.scores)
#         top = max(self.scores)
#         score = self.score_item(gen1, gen2, struct)
#         ratio = (score-bot) / (top-bot)
#         return self.score_ratio(ratio, struct)

#     def score_ratio(self, ratio, struct):
#         raise NotImplemented

# class RelativeScorerSection(RelativeScorer):

#     TARGET = { None: (0.0, 1.0) }

#     def score_ratio(self, ratio, struct):
#         '''Return a value expressing how far ratio is from the interval under struct in TARGET
#         '''
#         bot, top = self.TARGET[struct] if struct in self.TARGET else self.TARGET[None]
#         dist = tools.distance_to_interval(ratio, bot, top)
#         norm = max(bot, 1.0-top)
#         return -dist/norm if norm else 0


### Model

class Model:#(Gen):

    def __init__(self, key: str, mode: str, meter: str):
        self.key: str = key
        self.mode: str = mode
        self.meter: str = meter
        self.quarters_per_bar: float = music.quarters_per_bar(meter)
        self.vps: List[ViewPoint] = []
        

    # iterate through models      
    def __iter__(self):
        for vp in self.vps:
            yield vp

    def __getitem__(self, name: str) -> ViewPoint:
        for vp in self:
            if vp.name == name:
                return vp
        raise KeyError(name)

    def add_vp(self, name: str, content_cls: Type[C], before: List[str] = [], use_copy: bool = True, lead_name: Optional[str] = None) -> None:

        error_msg: str = "Need to specify existing Lead ViewPoint when creating a Follow ViewPoint."
        new_vp: ViewPoint
        if lead_name:
            if lead_name in [vp.name for vp in self]:
                lead: ViewPoint = self[lead_name]
                if isinstance(lead, ViewPointLead):
                    new_vp = ViewPointFollow(name, content_cls, use_copy, self, lead)
                else:
                    raise RuntimeError(error_msg)
            else:
                raise RuntimeError(error_msg)
        else:
            new_vp = ViewPointLead(name, content_cls, use_copy, self)
        if before:
            ind: int = min([self.vps.index(self[vp]) for vp in before])
            self.vps.insert(ind, new_vp)
        else:
            self.vps.append(new_vp)

    def setup(self) -> None:
        ''' Set up fixed count dependency
        '''
        for (i, vp1) in enumerate(self.vps):
            for vp2 in self.vps[i + 1:]:
                if vp1.get_leader() == vp2.get_leader():
                    vp1.fixed_count_out.append(vp2)
                    vp2.fixed_count_in = vp1

    def set_structure(self, struc: StructureNode) -> None:
        self.structure: StructureNode = struc
        for vp in self.vps:
            vp.initialize_structure()

    def add_producer(self, _producer: type, vp: str, *vp_in_names: str, fixedness: float = 0.5) -> None:
        vps_in: List[ViewPoint] = [self[n] for n in vp_in_names]
        if issubclass(_producer, Producer):
            producer = _producer(self[vp], vps_in, fixedness)
            self[vp].producers.append(producer)
    
    def add_evaluator(self, evaluator: type, *vp_names: str, weight: float = 1.0) -> None:
        vps: List[ViewPoint] = [self[n] for n in vp_names]
        if issubclass(evaluator, Constraint):
            constraint = evaluator(vps)
            for v in vps:
                v.constraints.append(constraint)
        elif issubclass(evaluator, Scorer):
            scorer = evaluator(vps, weight)
            for v in vps:
                v.scorers.append(scorer)

    def generate(self) -> None:
        for vp in self.vps:
            print(f'[yellow]### generate VP \'{vp.name}\'')
            vp.generate()
    
    # def scorer(self, scorer: Scorer, mod1, mod2=None, weight=1):
    #     '''Bind scorer to mod1 (and mod2 if it scores two models)
    #     '''
    #     if mod2:
    #         sco = scorer(self[mod1], self[mod2])
    #     else:
    #         sco = scorer(self[mod1])
    #     self.scorers += [sco]
    #     self[mod1].add_filter(sco, weight)
    #     return sco

    # def structurer(self, struct, mod):
    #     self.structurers += [(self[struct], self[mod])]

    def export(self, filename: str, title: str, lyr_vp: str, melody_vp_names: List[str], annot_vp_names: List[str], svg: bool) -> None:
        print('[yellow]## Exporting')
        melodies = [(vp,
                     self[vp][:],
                     self[lyr_vp].export_text(self[vp])) for vp in melody_vp_names]
        annots   = [(vp, \
                     self[vp].export_text(self[melody_vp_names[-1]])) for vp in annot_vp_names]
        export.export(filename, title, melodies, annots, self.key, self.meter, svg)