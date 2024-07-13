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
T = TypeVar('T')

class WindowIterator:
    def __init__(self, size: Optional[int], n: RefinementNode, outside: bool = False):
        self.node = n.vp.root if outside else n
        if size is None:
            self.size = self.node.get_elt_count()
            self.possible_positions = [0]
        else:
            self.size = size
            if outside:
                first_pos = max(n.start.relative_p() - size + 1, 0)
                last_pos = n.end.relative_p() - size + 1
                self.possible_positions = list(range(first_pos, last_pos))
            else:
                self.possible_positions = list(range(0, n.get_elt_count() - size + 1))

        self.start = self.node.new_index()
        self.end = self.node.new_index()
        self.i = iter(self.possible_positions)

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Tuple[Index, Index]:
        pos = next(self.i)
        self.start.set_offset(pos)
        self.end.set_offset(pos + self.size)
        return (self.start, self.end)

    def __len__(self) -> int:
        return len(self.possible_positions)


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
    ARGS: List[Tuple[type, Interval]] = []

    NEEDS_START: bool = False

    T = TypeVar('T')

    def __call__(self, *args: T) -> R:
        raise NotImplementedError()


    def applies_to(self, *args: T, start: Optional[Index] = None) -> bool:
        ''' whether the rule can be applied, given args and a start position
        overwrite to implement specific behavior'''
        return True 

    def check_args(self, *args: T) -> None:
        if len(args) != len(self.ARGS):
            raise RuntimeError("Number of specified and of passed arguments do not match")
        for a, (t, s) in zip(args, self.ARGS):
            if not isinstance(a, List):
                raise RuntimeError("Passed argument is not a list")

            if len(a) not in s or len(a) == 0:
                raise RuntimeError("Passed lists are not of specified length")
            if not isinstance(a[0], t):
                raise RuntimeError("Passed argument list is not of specified type")

    def get_range(self, _vp: ViewPoint) -> Optional[Interval]:
        for (i, vp) in enumerate(self.vps):
            if vp == _vp:
                return self.ARGS[i][1]
        raise None

### Producers

class Producer(Rule[List[List[C]]]):

    OUT_COUNT: Interval

    NEEDS_CONTEXT: bool = False
    NEEDS_DURATION: bool = False
    NEEDS_LEN: bool = False
    DISPATCH_BY_NODE: bool = False

    def flexible_length(self) -> bool:
        return self.OUT_COUNT.max is None

    def call_applies_to(self, node:RefinementNode, window_start: Index, window_end: Index) -> bool:
        args = self.fetch_args(node, window_start, window_end, True)
        return self.applies_to(*args)

    def fetch_args(self, node: RefinementNode, window_start: Index, window_end: Index, for_applies_to: bool) -> list:

        args = [vp[window_start:window_end] for vp in self.vps]
        self.check_args(*args)

        if self.NEEDS_START or for_applies_to:
            args.append(window_start)

        if for_applies_to:
            return args

        if self.NEEDS_CONTEXT:
            pre_context: List[C] = node.vp[:window_start]
            post_context: List[C] = node.vp[window_end:]
            args += [pre_context, post_context]

        if self.NEEDS_LEN:
            len_to_gen: Interval
            if node.vp.fixed_count():
                len_to_gen = Interval(node.get_elt_count(), node.get_elt_count()) 
            else:
                len_to_gen = Interval(1)
            if len_to_gen not in self.OUT_COUNT:
                raise RuntimeError(f"Producer {self.__class__.__name__} can't generate the specified number of elements.")
            args.append(len_to_gen)
        
        if self.NEEDS_DURATION:
            args.append(node.get_duration())

        if self.DISPATCH_BY_NODE:
            args += self.get_node_args(node)

        return args

    def get_node_args(self, node: RefinementNode) -> list:
        raise NotImplementedError()



class Enumerator(Producer[C]):

    def __call__(self, node: RefinementNode) -> List[List[C]]:
        args = self.fetch_args(node, node.start, node.end, False)
        return self.enumerate(*args)

    def enumerate(self, *args: T) -> List[List[C]]:
        raise NotImplementedError()

class RandomizedProducer(Producer[C]):

    def __call__(self, node: RefinementNode, batch_size: int) -> List[List[C]]:
        args = self.fetch_args(node, node.start, node.end, False)
        return [self.produce(*args) for i in range(batch_size)]
        

    def produce(self, *args: T) -> List[C]:
        raise NotImplementedError()



### Constraints

class Evaluator(Rule[R]):
        
        def fetch_args(self, node: RefinementNode, generated: List[C], window_start: Index, window_end: Index) -> list:
            args = []
            for vp in self.vps:
                # replace new span of currently generated VP
                if node.vp == vp:
                    start_p: int = window_start.pos - node.start.relative_p(window_start.node.name)
                    prefix = vp[window_start:node.start]
                    # if window_start is before the start of generated:
                    if start_p < 0:
                        # prefix += [node.vp.undefined()] * (- start_p)
                        start_p = 0
                    suffix = vp[node.end:window_end]
                    # if window_end is after the end of generated
                    end_p: int = window_end.pos - node.start.relative_p(window_start.node.name)
                    if end_p > len(generated):
                        # suffix = [node.vp.undefined()] * (end_p - len(generated)) + suffix
                        end_p = len(generated)
                    args.append(prefix + generated[start_p:end_p] + suffix)
                else: 
                    args.append(vp[window_start:window_end])
            self.check_args(*args)
            
            if self.NEEDS_START:
                args.append(window_start)

            return args


class Constraint(Evaluator[bool]):
    def __call__(self, node: RefinementNode, generated: List[C], window_start: Index, window_end: Index) -> bool:
        args = self.fetch_args(node, generated, window_start, window_end)
        return self.valid(*args)

    def valid(self, *args: T) -> bool:
        raise NotImplementedError()

    

### Scores

class Scorer(Evaluator[float]):

    def __call__(self, node: RefinementNode, generated: List[C], window_start: Index, window_end: Index) -> float:
        args = self.fetch_args(node, generated, window_start, window_end)
        return self.score(*args)

    def score(self, *args: T) -> float:
        raise NotImplementedError()


class Generator(Generic[C]):

    BATCH_SIZE = 100
   # S = TypeVar('S', bound=m.Content)

    def __init__(self, node: RefinementNode, prod: Producer) -> None:
        # the generated data
        self.gens: List[Tuple[List[C], float]] = []
        self.node: RefinementNode = node
        self.producer: Producer = prod
        self.constraints: List[Constraint] = []
        self.scorers: List[Scorer] = []
        # self.setup()

    def generate(self) -> None:

        # call producer
        gens: List[List[C]] = []
        succeeding: List[List[C]] = []
        failing: List[Tuple[List[C], int]] = []
        if isinstance(self.producer, Enumerator):
            gens += self.producer(self.node)
        else:
            assert isinstance(self.producer, RandomizedProducer)
            gens += self.producer(self.node, self.BATCH_SIZE)

        # call constraints (only those for which all involved VPs have been generated)
        self.constraints = [c for c in self.node.vp.constraints \
                            if all([vp.generated for vp in c.vps])]
        for g in gens:
            fail_count: int = 0
            for c in self.constraints:
                r = c.get_range(self.node.vp)
                assert r 
                for window_start, window_end in WindowIterator(r.max, self.node, True):
                    fail_count += not c(self.node, g, window_start, window_end)

            if fail_count == 0:
                succeeding.append(g)
            else:
                failing.append((g, fail_count))
        
        # refine
        if len(succeeding) == 0:
            failing.sort(key = lambda x: x[1])
            out = failing[0][0]
            self.node.set_to(out, self.producer.fixedness)

            faulty_nodes: List[RefinementNode] = []
            for c in self.constraints:
                r = c.get_range(self.node.vp)
                if r.max is None or len(out) <= r.max: # only deal with sub-constraint (scope should be DECREASING during refinement)
                    continue
                for window_start, window_end in WindowIterator(r.max, self.node, True):
                    if not c(self.node, out, window_start, window_end):
                        # if a partially outside constraint is failing, only regenerate its intersection with self.node
                        start, end = (self.node.start.relative_p(), self.node.end.relative_p())
                        if window_start.pos < start:
                            window_start.set_offset(start)
                        if window_end.pos > end:
                            window_end.set_offset(end)
                        faulty_nodes += self.node.vp.root.get_subrange(window_start, window_end)
            
            for n in faulty_nodes:
                if n == self:
                    # ran out of options
                    raise NotImplementedError("Backtracking would be sensible here, but it is not yet implented")
                n.generate()
            return

        # call scorers
        self.scorers = [s for s in self.node.vp.scorers \
                        if all([vp.generated for vp in s.vps])]
        for g in succeeding:
            score: float = 0.0
            for s in self.scorers:
                r = s.get_range(self.node.vp)
                assert r
                subscore: float = 0.0
                windows = WindowIterator(r.max, self.node, True)
                for window_start, window_end in windows:
                    subscore += s(self.node, g, window_start, window_end)
                subscore = subscore / len(windows)  
                score += subscore * s.weight
            self.gens.append((g, score))

        # sort
        self.gens.sort(key = lambda p: p[1], reverse=True)

        self.node.set_to(self.gens[0][0], self.producer.fixedness)


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

class HiddenMarkov(RandomizedProducer[C]):
    
    # INITIAL_S, FINAL_S : dict[str, List[str]]
    # structure-dependent initial and final states
    # INITIAL_S: Dict[str, List[str]]
    # FINAL_S: Dict[str, List[str]]

    OUT_COUNT = Interval(1)
    NEEDS_CONTEXT = True
    NEEDS_LEN = True

    STATES: List[str]
    INITIAL: List[str]

    TRANSITIONS: Dict[str, Dict[str, float]]
    EMISSIONS: Dict[str, Dict[str, float]]

    def state_legal(self, state: Optional[str]) -> bool:
        '''Return whether state is legal
        '''
        return state is not None

    def produce(self, pre_context: List[C], post_context: List[C], len_to_gen: Interval) -> List[C]:
        '''Return a sequence of emitted states
        '''

        i: int = 0

        # otherwise the final states constraint has led to a too long sequence
        i = 0
        state: Optional[str] = None
        if len(pre_context) == 0 or pre_context[-1].is_undefined():
            state = pwchoice(self.INITIAL)
        else:
            # if we know the last emitted state, update the probabilities for the first hidden state accordingly
            last: C = pre_context[-1]
            prob = lambda s: sum([self.TRANSITIONS[s1][s] * self.EMISSIONS[s1][str(last)] for s1 in self.STATES])
            initial = dict([(s, prob(s)) for s in self.STATES])
            while not self.state_legal(state):
                state = pwchoice(initial)
        emits: List[C] = []

        assert state
        emit: C = self.vp_out.content_cls(pwchoice(self.EMISSIONS[state]))
        emits.append(emit)
        i += 1
        while i < len_to_gen.min:
            next_state: Optional[str] = None
            while not self.state_legal(next_state):
                try:
                    next_state = pwchoice(self.TRANSITIONS[state])
                except KeyError:
                    print(f"[red]! No transition for [yellow]{self.__class__.__name__} {state}")
                    raise
            assert next_state
            state = next_state
            emit = self.vp_out.content_cls(pwchoice(self.EMISSIONS[state]))
            emits += [emit]
            i += 1

        return emits

class Markov(HiddenMarkov[C]):
    
    def __init__(self):
        self.EMISSIONS = {
            x: defaultdict(float, {x: 1.00}) for x in self.STATES
        }

class PitchMarkov(Markov[m.Pitch]):

    AMBITUS: Tuple[m.Pitch, m.Pitch]
    INITIAL_AMBITUS: Tuple[m.Pitch, m.Pitch]

    def __init__(self, key: str):
        super().__init__()
        self.set_key(key)

    def state_legal(self, pitch: str) -> bool:
        # Redundant, but we may here implement melodic rules
        if pitch is None:
            return False
        return music.in_range(pitch, self.AMBITUS, self.key)

    def set_key(self, key: str) -> None:
        ''' Adapt transitions and states to key
        '''
        self.key = key

        for n1 in list(self.TRANSITIONS):
            for n2 in list(self.TRANSITIONS[n1]):
                if not music.in_range(n2, self.AMBITUS, self.key) or '#' in n2 or '-' in n2:
                    del self.TRANSITIONS[n1][n2]
                    if len(self.TRANSITIONS[n1]) == 0:
                        del self.TRANSITIONS[n1]
        for n in list(self.INITIAL):
            if not music.in_range(n, self.AMBITUS_INITIAL, self.key):
                self.INITIAL.remove(n)


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

class Model:

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

    def add_vp(self, name: str, content_cls: Type[C], before: List[str] = [], use_copy: bool = True, lead_name: Optional[str] = None, gapless: bool = True) -> None:

        error_msg: str = "Need to specify existing Lead ViewPoint when creating a Follow ViewPoint."
        new_vp: ViewPoint
        if lead_name:
            if lead_name in [vp.name for vp in self]:
                lead: ViewPoint = self[lead_name]
                if isinstance(lead, ViewPointLead):
                    new_vp = ViewPointFollow(name, content_cls, use_copy, self, lead, gapless)
                else:
                    raise RuntimeError(error_msg)
            else:
                raise RuntimeError(error_msg)
        else:
            new_vp = ViewPointLead(name, content_cls, use_copy, self, gapless)
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
                if vp1.get_leader() == vp2.get_leader() and vp2.fixed_count_in is None:
                    vp1.fixed_count_out.append(vp2)
                    vp2.fixed_count_in = vp1

        for vp in self.vps:
            vp.init()

    def set_structure(self, struc: StructureNode) -> None:
        self.structure: StructureNode = struc
        for vp in self.vps:
            vp.initialize_structure()

    def add_producer(self, producer: Producer, vp: str, *vp_in_names: str, fixedness: float = 0.5, default: bool = False) -> None:
        producer.model: Model = self
        producer.fixedness: float = fixedness
        try:
            producer.vp_out: ViewPoint = self[vp]
            producer.vps: List[ViewPoint] = [self[n] for n in vp_in_names]
        except KeyError:
            raise RuntimeError("Need to specify names of existing ViewPoints")

        self[vp].producers.append(producer)
        if default:
            if not producer.flexible_length():
                raise RuntimeError(f"Default producers have to be of flexible length")
            self[vp].default_prod = producer
    
    def add_evaluator(self, evaluator: Evaluator, *vp_names: str, weight: float = 1.0) -> None:
        try:
            evaluator.vps: List[ViewPoint] = [self[n] for n in vp_names]
        except KeyError:
            raise RuntimeError("Need to specify names of existing ViewPoints")
        if isinstance(evaluator, Constraint):
            for v in evaluator.vps:
                v.constraints.append(evaluator)
        elif isinstance(evaluator, Scorer):
            evaluator.weight: float = weight
            for v in evaluator.vps:
                v.scorers.append(evaluator)

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