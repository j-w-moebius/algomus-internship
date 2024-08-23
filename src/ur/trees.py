
from __future__ import annotations
from anytree import NodeMixin, RenderTree, PreOrderIter
from anytree.exporter import DotExporter
from typing import Self, Generic, TypeVar, Optional, Callable, Dict, List, NewType, Protocol, SupportsIndex, Tuple, Union, overload, Type
import copy
import music
from functools import reduce
import operator
import ur
from abc import ABC, abstractmethod

# Content type
C = TypeVar('C', bound=music.Content)
# Content type with Temporality
T = TypeVar('T', bound=music.Temporal)
# Index type
I = TypeVar('I', bound='Numeric')

class Numeric(Protocol):

    def __add__(self, other: Self) -> Self:
        pass

    def __sub__(self, other: Self) -> Self:
        pass


class Index:
    def __init__(self, quarter: float, pos: int, node: RefinementNode):
        self.quarter: float = quarter
        self.pos: int = pos
        self.node: RefinementNode = node

    def __str__(self) -> str:
        return f"({self.quarter}, {self.pos})"

    def __gt__(self, other: Self) -> bool:
        assert self.node == other.node
        return self.pos > other.pos and self.quarter > other.quarter

    def __lt__(self, other: Self) -> bool:
        assert self.node == other.node
        return self.pos < other.pos and self.quarter < other.quarter

    def __ge__(self, other: Self) -> bool:
        assert self.node == other.node
        return self.pos >= other.pos and self.quarter >= other.quarter

    def __le__(self, other: Self) -> bool:
        assert self.node == other.node
        return self.pos <= other.pos and self.quarter <= other.quarter

    def __eq__(self, other: Self) -> bool:
        assert self.node == other.node
        return self.pos == other.pos and self.quarter == other.quarter

    def __add__(self, other: Self) -> Self:
        assert self.node == other.node
        return self.__class__(self.quarter + other.quarter, self.pos + other.pos, self.node)

    def __sub__(self, other: Self) -> Self:
        assert self.node == other.node
        return self.__class__(self.quarter - other.quarter, self.pos - other.pos, self.node)

    def maps_to(self, pos: int, level: int) -> bool:
        assert level >= 0
        level_ctr: int = self.node.depth
        ptr: RefinementNode = self.node
        if level_ctr <= level:
            acc: int = self.node.start.pos
            while level_ctr < level:
                for c in ptr.children:
                    if c.end.pos + acc > self.pos:
                        ptr = c
                        acc += c.start.pos
                        break
                level_ctr += 1
            if pos >= 0:
                return acc + pos == self.pos
            else:
                return acc + ptr.get_elt_count() + pos == self.pos
        else:
            acc = 0
            while True:
                ptr = ptr.parent
                level_ctr -= 1
                if level_ctr == level:
                    break
                acc +=  ptr.start.pos
            if pos >= 0:
                return acc + self.pos == pos
            else:
                return acc + self.pos == ptr.get_elt_count() + pos



    def relative_p(self, label: str = 'ALL') -> int:
        if self.node.name == label:
            return self.pos - self.node.start.pos
        elif self.node.parent is not None:
            return self.pos + self.node.parent.start.relative_p(label)
        else:
            raise RuntimeError("n is not a parent of current node")

    def relative_q(self, label: str = 'ALL') -> float:
        if self.node.name == label:
            return self.quarter - self.node.start.quarter
        elif self.node.parent is not None:
            return self.quarter + self.parent.start.relative_q(label)
        else:
            raise RuntimeError("n is not a parent of current node")

    def set_offset(self, offset: int) -> None:
        ''' Offset wrt to self.node.start '''
        offset = min(offset, self.node.get_elt_count())
        node_content: list = self.node.vp.get_leader()[self.node.start:self.node.end]
        durations = [e.quarter_length() for e in node_content[:offset]]
        self.quarter = sum(durations) + self.node.start.quarter
        self.pos = offset + self.node.start.pos

    def child_index(self, child: RefinementNode) -> Self:
        #assert child in self.node.children
        return self.__class__(self.quarter - self.node.start.quarter,
                              self.pos - self.node.start.pos,
                              child)

class Node(NodeMixin, Generic[I]):

    def __init__(self, start: I, end: I, name: str, children: List[Self] = []):
        self.start: I = start
        self.end: I = end
        self.name: str = name
        # ORDERED list of children
        self.children: List[Self] = children

    def export_to_dot(self, filename: str) -> None:
        with open(filename, 'w') as file:
            file.writelines(DotExporter(self))

class StructureNode(Node[float]):
    """
    A node of a Structure Tree.
    """
    def __init__(self, start: float, end: float, name: str, children: List[Self] = []):
        super().__init__(start, end, name, children)

    def __str__(self) -> str:
        out: str = ""
        for pre, _, node in RenderTree(self):
            treestr = u"%s%s" % (pre, node.name)
            out += treestr.ljust(8) + "\n"
        return out

class RefinementNode(Node[Index]):
    """
    A node of a (non-structure) Refinement Tree.
    """

    def __init__(self, start: Tuple[float, int] | Index, end: Tuple[float, int] | Index, name: str, vp: ViewPoint, children: List[Self] = [], structure: bool = False):
        if isinstance(start, tuple):
            my_start: Index = Index(*start, self)
        else:
            my_start = start.child_index(self)
        if isinstance(end, tuple):
            my_end: Index = Index(*end, self)
        else:
            my_end = end.child_index(self)

        super().__init__(my_start, my_end, name, children)
        self.copy_of: Optional[Self] = None
        self.generatable: bool = True
        self.generator: Optional[ur.Generator] = None
        self.fixedness: float = .0
        
        self.structure: bool = structure
        self.vp: ViewPoint = vp

    def __str__(self) -> str:
        out: str = ""
        for pre, _, node in RenderTree(self):
            treestr = u"%s%s" % (pre, node.name)
            content_str = ""
            if node.copy_of is not None:
                content_str += f' (same as {node.copy_of.name})'
            out += treestr.ljust(8) + str(node.start) + str(node.end) + content_str + "\n"
        return out

    def __iter__(self):
        for e in self.vp.out[self.start.pos:self.end.pos]:
            yield e

    def new_index(self) -> Index:
        return Index(0.0, 0, self)

    def get_duration(self) -> float:
        return self.end.quarter - self.start.quarter

    def get_elt_count(self) -> int:
        return self.end.pos - self.start.pos

    def unset_generatable(self) -> None:
        self.generatable = False
        if self.parent is not None:
            self.parent.unset_generatable()

    def get_structure_parent(self) -> Self:
        if self.structure:
            return self
        return self.parent.get_structure_parent()

    def update_fixedness(self) -> None:
        self.fixedness = max([c.fixedness for c in self.children])
        if self.parent is not None:
            self.parent.update_fixedness()

    def increase_size(self, delta: int) -> None:
        self.end.pos = self.end.pos + delta
        if self.parent is not None:
            ind: int = self.parent.children.index(self)
            for c in self.parent.children[ind + 1:]:
                c.start.pos += delta
                c.end.pos += delta
            self.parent.increase_size(delta)

    def increase_duration(self, delta: float) -> None:
        self.end.quarter += delta
        if self.parent is not None:
            ind: int = self.parent.children.index(self)
            for c in self.parent.children[ind + 1:]:
                c.start.quarter += delta
                c.end.quarter += delta
            self.parent.increase_duration(delta)

    def set_to(self, content: List[C], fixedness: float, update: bool = True) -> None:
        self.fixedness = fixedness

        self.vp.out[self.start.relative_p():self.end.relative_p()] = content
        old_length = self.end.pos - self.start.pos
        self.increase_size(len(content) - old_length)

        if self.parent is not None:
            self.parent.update_fixedness()
        
        if not update:
            return
        
        if isinstance(self.vp, ViewPointLead):
            # also update duration for lead VPs
            old_duration: float = self.get_duration()
            new_duration: float = sum([e.quarter_length() for e in content])
            self.increase_duration(new_duration - old_duration)

        for vp in self.vp.fixed_count_out:
            # for now (TODO)
            assert self.structure
            vp.nodes[self.name].set_to([vp.undefined()] * len(content), 0.0, False)


    def set_generator(self, prod: ur.Producer) -> ur.Generator:
        new_gen: ur.Generator = ur.Generator(self, prod, self.vp.model.batch_size)
        self.generator = new_gen
        return new_gen

    def dispatch_producers(self) -> List[ur.Generator]:
        # dispatch producers and create generators
        generators: List[ur.Generator] = []
        for p in self.vp.producers:
            # Dispatch by node: just call p on all descendants
            if p.DISPATCH_BY_NODE:
                for n in [self] + list(self.descendants):
                    if p.guard(n):
                        generators.append(n.set_generator(p))
                return generators
            if p.flexible_length():
                continue

            sup: Optional[int] = p.OUT_COUNT.max
            for window_start, window_end in ur.WindowIterator(sup, self):
                # check if rule guard allows application at window_start
                if p.guard(window_start):
                    generators += [n.set_generator(p) for n in self.get_subrange(window_start, window_end)]

        if self.vp.gapless:
            # fill intervals in between with default producer
            slices: List[Tuple[int, int]] = []
            for g in generators:
                start: int = g.node.start.relative_p(self.name)
                end: int = g.node.end.relative_p(self.name)
                slices.append((start, end))

            window_start = self.new_index()
            window_end = self.new_index()
            window_start.set_offset(0)
            for (start, end) in sorted(slices, key = lambda p: p[0]):
                if start + self.start.pos > window_start.pos:
                    window_end.set_offset(start)
                    generators += [n.set_generator(self.vp.default_prod) 
                                for n in self.get_subrange(window_start, window_end)]
                window_start.set_offset(end)
            if self.end.pos > window_start.pos:
                generators += [n.set_generator(self.vp.default_prod) 
                                for n in self.get_subrange(window_start, self.end)]
        
        return generators

    def generate(self) -> None:
        if self.fixedness > 0.0:
            return
        if self.copy_of is not None:
            self.set_to(self.vp[self.copy_of.start:self.copy_of.end], 1.0)
        if not self.generatable:
            for c in self.children:
                c.generate()
            return 

        # generate                    
        for g in self.dispatch_producers():
            g.generate()


    def get_subrange(self, start: Index, end: Index) -> List[Self]:
        ''' tree growing '''
        # for now, assume we are only operating on nodes that have the following property:
        # [start, end) is either completely covered by some contiguous children,
        # or it is fully outside any child

        assert start.pos >= self.start.pos and end.pos <= self.end.pos
        if start == self.start and end == self.end: # [start, end) is CONGRUENT with self
            return [self] 
        result: List[Self] = []
        ctr: int = 0
        for c in self.children:
            c_start: int = c.start.pos + self.start.pos
            c_end: int = c.end.pos + self.start.pos
            if c_start <= start.pos and c_end >= end.pos: # [start, end) is IN c
                result = c.get_subrange(start.child_index(c), end.child_index(c))
            elif c_end <= start.pos: # c is fully BEFORE [start, end)
                pass
            elif c_start >= end.pos: # c is fully AFTER [start, end)
                break
            else: # [start, end) is PARTIALLY in c
                if c_start < start.pos:
                    new_start = start.child_index(c)
                else:
                    new_start = c.start
                if c_end > end.pos:
                    new_end = end.child_index(c)
                else: 
                    new_end = c.end
                result += c.get_subrange(new_start, new_end)
                pass
            ctr += 1

        if result == []: # [start, end) is outside any child: create new one
            new_node = RefinementNode(start, end, "", self.vp)
            #new_node.parent = self
            self.children = list(self.children[:ctr]) + [new_node] + list(self.children[ctr:])
            result = [new_node]
        return result



class ViewPoint(Generic[C]):

    def __init__(self, name: str, content_cls: Type[C], use_copy: bool, model: ur.Model, gapless: bool):
        self.name: str = name
        self.use_copy: bool = use_copy
        self.model: ur.Model = model
        self.producers: List[ur.Producer] = []
        self.constraints: List[ur.Constraint] = []
        self.scorers: List[ur.Scorer] = []
        self.generated: bool = False
        self.out: List[C] = []
        self.content_cls: Type[C] = content_cls
        self.fixed_count_out: List[ViewPoint] = []
        self.fixed_count_in: Optional[ViewPoint] = None
        self.default_prod: ur.Producer
        self.gapless: bool = gapless

    def init(self) -> None:
        self.producers.sort(key = lambda p: p.fixedness, reverse = True)

    def initialize_to(self, l: List[T], fixedness: float = 1.0) -> None:
        """
        Set the VP to a fixed content.

        :param l: the list of elements to be set as fixed content.
        :param fixendess: the associated fixedness value.
        """
        pass
    
    def get_pos(self, i: Index) -> int:
        if i.node.vp.get_leader() == self.get_leader():
            return i.relative_p()

        struc_parent: RefinementNode = i.node.get_structure_parent()
        ind_q: float = i.relative_q(struc_parent.name)
        acc: float = 0.0
        parent_start: Index = self.nodes[struc_parent.name].start
        for (ctr, e) in enumerate(self.get_leader()[parent_start:], parent_start.relative_p()):
            if acc >= ind_q:
                return ctr
            acc += e.quarter_length()
        return ctr + 1

    @overload
    def __getitem__(self, i: Index) -> C:
        pass

    @overload
    def __getitem__(self, s: slice) -> C:
        pass

    def __getitem__(self, val: Index | slice) -> C | List[C]:
        if isinstance(val, Index):
            return self.out[self.get_pos(val)]
        if isinstance(val, slice):
            start:int = 0
            end: int = len(self.out)
            if val.start is not None and isinstance(val.start, Index):
                start = self.get_pos(val.start)
            if val.stop is not None and isinstance(val.stop, Index):
                end = self.get_pos(val.stop)  
            return self.out[start:end]
        else:
            raise RuntimeError("Index must be of type Index or slice")

    def __str__(self) -> str:
        out: str = f"ViewPoint {self.name}:\n"
        out += ' '.join([str(e) for e in self.out])
        out += "\n\n" + str(self.root) + "\n\n"
        return out

    def fixed_count(self) -> bool:
        return self.fixed_count_in is not None and self.fixed_count_in.generated

    def get_leader(self) -> ViewPointLead:
        raise NotImplementedError()

    def initialize_structure(self) -> None:
        self.nodes: Dict[str, RefinementNode] = {}
        self.root: RefinementNode = self.copy_struc_node(self.model.structure)
        i: int = 0
        for n in PreOrderIter(self.root):
            self.nodes[n.name] = n
            # handling rests
            if n.name[0] == '~':
                n.unset_generatable()
                n.set_to([self.undefined(music.beat(self.model.meter))], 0.0, False)
            if self.use_copy and n.name[-1] == '\'':    
                to_copy: str = n.name[:-1]
                if to_copy in self.nodes.keys():
                    n.copy_of = self.nodes[to_copy]
                    n.unset_generatable()

    def set_to(self, bars: List[C], fixedness: float = 1.0) -> None:
        raise NotImplementedError()

    def undefined(self, dur: float = 0.0) -> C:
        return self.content_cls.create_undefined(dur)

    def copy_struc_node(self, n: StructureNode, offset: int = 0) -> RefinementNode:
        '''Construct a RefinementNode by copying a StructureNode 
        '''
        if not n.children:
            self.out.append(self.undefined(n.end - n.start))
            return RefinementNode((n.start, offset), (n.end, offset + 1), n.name, self, structure=True)
        children = []
        offset_children = 0
        for c in n.children:
            child_node = self.copy_struc_node(c, offset_children)
            children.append(child_node)
            offset_children = child_node.end.pos
        return RefinementNode((n.start, offset), (n.end, offset + offset_children), n.name, self, children=children, structure=True)

    def generate(self) -> None:
        self.generated = True

        # update structure node durations from model structure
        for node in PreOrderIter(self.model.structure):
            peer_node = self.nodes[node.name]
            peer_node.start.quarter = node.start
            peer_node.end.quarter = node.end
        
        self.root.generate()
        print(self)

    def export_text(self, lead: ViewPoint) -> List[str]:
        assert isinstance(lead, ViewPointLead)
        self_content = self[:]
        self_durations = [e.quarter_length() for e in self.get_leader()[:]]
        lead_content = lead[:]

        acc_lead: float = 0.0
        acc_self: float = 0.0
        result: List[str] = []
        for e in lead_content:
            if acc_lead == acc_self:
                acc_self += self_durations.pop(0)
                result.append(str(self_content.pop(0)))
            else:
                result.append('-')
            acc_lead += e.quarter_length()
            
        return result

class ViewPointLead(ViewPoint[T]):
    def __init__(self, name: str, content_cls: Type[T], use_copy: bool, model: ur.Model, gapless: bool):
        super().__init__(name, content_cls, use_copy, model, gapless)
        self.followers: List[ViewPointFollow] = []

    def initialize_to(self, l: List[T], fixedness: float = 1.0) -> None:
        # lead VP needs to be set first
        self.generated = True
        new_content: List[T] = []
        for n in PreOrderIter(self.root):

            # only set content of leafs
            if n.children:
                continue
            acc: float = 0.0
            duration: float = n.get_duration()
            for (i, e) in enumerate(l):
                acc += e.quarter_length()
                if acc == duration:
                    new_content = l[:i + 1]
                    l = l[i + 1:]
                    break
            if n.copy_of and self.use_copy:
                # assume other n.copy_of is already set (-> only backward copy edges)
                n.set_to(self[n.copy_of.start:n.copy_of.end], fixedness)
            else:
                n.set_to(new_content, fixedness)
            new_content = []

        print(self)

    def get_leader(self) -> ViewPointLead:
        return self

    def generate(self) -> None:
        super().generate()
        # after generation, write new node durations into the model's structure tree
        for node in PreOrderIter(self.model.structure):
            peer_node = self.nodes[node.name]
            node.start = peer_node.start.quarter
            node.end = peer_node.end.quarter

class ViewPointFollow(ViewPoint[C]):
    def __init__(self, name: str, content_cls: Type[C], use_copy: bool, model: ur.Model, lead: ViewPointLead, gapless: bool):
        super().__init__(name, content_cls, use_copy, model, gapless)
        self.leader: ViewPointLead = lead
        lead.followers.append(self)

    def initialize_to(self, l: List[C], fixedness: float = 1.0) -> None:
        # assume that fixed_count_in VP is set first
        assert self.fixed_count_in is not None and self.fixed_count_in.generated
        self.generated = True
        for n in PreOrderIter(self.root):

            # only set content of leafs
            if n.children:
                continue
            new_content: List[C] = l[:n.get_elt_count()]
            l = l[n.get_elt_count():]
            if n.copy_of and self.use_copy:
                n.set_to(self[n.copy_of.start:n.copy_of.end], fixedness)
            else:
                n.set_to(new_content, fixedness)

    def get_leader(self) -> ViewPointLead:
        return self.leader