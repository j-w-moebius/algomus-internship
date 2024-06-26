
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
C = TypeVar('C')
# Content type with Temporality
T = TypeVar('T', bound=music.Temporal)
# Index type
I = TypeVar('I', bound='Numeric')

class Numeric(Protocol):

    def __add__(self, other: Self) -> Self:
        pass

    def __sub__(self, other: Self) -> Self:
        pass
    

class QuarterIndex(float):
    pass

class PosIndex(int):
    pass

class CumuList(Generic[C]):

    def __init__(self, elements: List[C], node: RefinementNode):
        self.elements: List[C] = elements
        self.node: RefinementNode = node

    def __len__(self) -> int:
        return len(self.elements)

    @overload
    def __getitem__(self, i: Numeric) -> C:
        pass

    @overload
    def __getitem__(self, i: slice) -> List[C]:
        pass

    def __getitem__(self, i: Numeric | slice) -> C | List[C]:
        if self.elements == []:
            return []
        if isinstance(i, int):
            return self.elements[i]
        if isinstance(i, float):
            return self.elements[self.get_pos_index(i)]
        if isinstance(i, slice):
            start:int = 0
            end: int = len(self.elements)
            if isinstance(i.start, int):
                start = i.start
            elif isinstance(i.start, float):
                start = self.get_pos_index(i.start)
            if isinstance(i.stop, int):
                end = i.stop
            elif isinstance(i.stop, float):
                end = self.get_pos_index(i.stop)
            return self.elements[start:end]
        else:
            raise RuntimeError("Index must be of type Numeric or slice")

    def __str__(self) -> str:
        return '[' + ', '.join([str(e) for e in self.elements]) + ']'

    def __iadd__(self, other: List[C]) -> Self:
        self.elements += other
        return self
    
    def get_pos_index(self, val: float) -> int:
        durations: RefinementNodeLead
        rel_start: int = 0
        if isinstance(self.node, RefinementNodeLead):
            durations = self.node
        elif isinstance(self.node, RefinementNodeFollow):
            structure_parent = self.node.get_structure_parent()
            rel_start = self.node.relative_start_p(structure_parent)
            assert(structure_parent.lead)
            durations = structure_parent.lead
        acc: float = 0.0
        for (i, e) in enumerate(durations, rel_start):
            if acc >= val:
                return i
            acc += e.quarter_length()
        return len(durations)
    
    def get_q_index(self, i: int) -> float:
        durations: RefinementNodeLead
        rel_start: int = 0
        if isinstance(self.node, RefinementNodeLead):
            durations = self.node
        elif isinstance(self.node, RefinementNodeFollow):
            structure_parent = self.node.get_structure_parent()
            rel_start = self.node.relative_start_p(structure_parent)
            assert(structure_parent.lead)
            durations = structure_parent.lead
        acc: float = 0.0
        for e in durations[:i]:
            acc += e.quarter_length()
        return acc


    def set(self, _elements: List[C]):
        self.elements = _elements

class Node(NodeMixin, Generic[I]):

    def __init__(self, start: I, end: I, name: str, children: List[Self] = []):
        self.start: I = start
        self.end: I = end
        self.name: str = name
        # ORDERED list of children
        self.children: List[Self] = children

    def zero_index(self) -> I:
        raise NotImplementedError() # overwritten in subclasses

    def relative_start_p(self, n: Node) -> int:
        raise NotImplementedError()

    def relative_start_q(self, n: Node) -> float:
        raise NotImplementedError()

    def export_to_dot(self, filename: str) -> None:
        with open(filename, 'w') as file:
            file.writelines(DotExporter(self))

class StructureNode(Node[QuarterIndex]):
    def __init__(self, start: float, end: float, name: str, children: List[Self] = []):
        super().__init__(QuarterIndex(start), QuarterIndex(end), name, children)

class RefinementNode(Node[I], Generic[C, I]):

    def __init__(self, start: I, end: I, name: str, vp: ViewPoint, children: List[Self] = [], structure: bool = False):
        super().__init__(start, end, name, children)
        self.generator_content: Optional[List[C]] = None
        self.copy_of: Optional[Self] = None
        self.generatable: bool = True
        self.generator: Optional[ur.Generator] = None
        self.elt_count: int = 0
        self.fixedness: float = .0
        self.buffer: CumuList[C] = CumuList([], self)
        self.buffer_above: CumuList[C] = CumuList([], self)
        self.buffer_below: List[Tuple[I, I, List[C]]] = []
        self.buffer_valid: bool = True
        self.buffer_above_valid: bool = True
        self.buffer_below_valid: bool = True
        self.structure: bool = structure
        self.vp: ViewPoint = vp

    def __iter__(self):
        self.update_buffer()
        for e in self.buffer.elements:
            yield e

    def __len__(self):
        self.update_buffer()
        return len(self.buffer)

    @overload
    def __getitem__(self, i: Numeric) -> C:
        pass

    @overload
    def __getitem__(self, i: slice) -> List[C]:
        pass

    def __getitem__(self, i: Numeric | slice) -> C | List[C]:
        self.update_buffer()
        return self.buffer[i]

    def get_duration(self) -> float:
        raise NotImplementedError() # overwritten in subclasses

    def update_buffer(self) -> None:
        if self.buffer_valid:
            return
        self.fetch_above()
        self.fetch_below()
        self.buffer.set([])

        ctr: I = self.zero_index()
        for (s, e, seq) in self.buffer_below:
            self.buffer += self.buffer_above[ctr:s]
            self.buffer += seq
            ctr = e
        self.buffer += self.buffer_above[ctr:]
        self.buffer_valid = True

    def fetch_above(self) -> None:
        if self.buffer_above_valid:
            return
        self.parent.fetch_above()
        self.buffer_above_valid = True
        self.buffer_above.set(self.parent.buffer_above[self.start, self.end])

    def fetch_below(self) -> None:
        if self.buffer_below_valid:
            return
        self.buffer_below = []
        for c in self.children:
            c.fetch_below()
            self.buffer_below += [(s + c.start, e + c.start, seq) for (s, e, seq) in c.buffer_below]

    def invalidate_buffer_upward(self) -> None:
        self.buffer_below_valid = False
        self.buffer_valid = False
        if self.parent is not None:
            self.parent.invalidate_buffer_upward()

    def invalidate_buffer_downward(self) -> None:
        self.buffer_above_valid = False
        self.buffer_valid
        for c in self.children:
            c.invalidate_buffer_downward()

    def update_elt_count(self) -> None:
        raise NotImplementedError()

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

    def set_to(self, content: List[C], fixedness: float) -> None:
        self.fixedness = fixedness
        self.buffer.set(content)
        self.buffer_above.set(content)
        self.buffer_below = [(self.zero_index(), self.end - self.start, content)]
        self.buffer_valid = True
        self.buffer_above_valid = True
        self.buffer_below_valid = True
        if self.parent is not None:
            self.parent.invalidate_buffer_upward()
        for c in self.children:
            c.invalidate_buffer_downward()

        if self.parent is not None:
            self.parent.update_fixedness()

    def generate(self) -> None:
        if self.fixedness > 0.0:
            return
        if self.copy_of is not None:
            start = self.copy_of.relative_start_p(self.vp['A']) # TODO: replace this ugly hack
            self.set_to(self.vp['A'][start:start + self.copy_of.elt_count], 1.0) # TODO: not sure if sensible
        if not self.generatable:
            for c in self.children:
                c.generate()
            return 
        if not self.generator:
            self.generator = ur.Generator(self)
        self.update_elt_count()
        new_content, fixedness = self.generator.generate()
        self.set_to(new_content, fixedness)

    def print(self) -> None:
        for pre, _, node in RenderTree(self):
            treestr = u"%s%s" % (pre, node.name)
            content_str: str = '[' + ' '.join([str(c) for c in node]) + ']'
            if node.copy_of:
                content_str += f' (same as {node.copy_of.name})'
            print(treestr.ljust(8), node.start, node.end, content_str)


class RefinementNodeFollow(RefinementNode[C, PosIndex]):

    def __init__(self, start: int, end: int, name: str, vp: ViewPointFollow, children: List[Self] = [], structure: bool = False, lead: Optional[RefinementNodeLead] = None):
        super().__init__(PosIndex(start), PosIndex(end), name, vp, children, structure)
        self.lead: Optional[RefinementNodeLead] = lead

    def update_elt_count(self) -> None:
        if self.lead:
            self.elt_count = self.lead.elt_count
        else:
            raise NotImplementedError()
    
    def zero_index(self) -> PosIndex:
        return PosIndex(0)

    def get_duration(self) -> float:
        if self.structure:
            return self.lead.get_duration()
        else:
            raise NotImplementedError()

    def relative_start_p(self, n: Node) -> int:
        if self == n:
            return 0
        elif self.parent is not None:
            self.parent.update_buffer()
            return self.start + self.parent.relative_start_p(n)
        else:
            raise RuntimeError("n is not a parent of current node")

    def relative_start_q(self, n: Node) -> float:
        if self == n:
            return 0.0
        elif self.parent is not None:
            self.parent.update_buffer()
            start_index = self.parent.buffer.get_pos_index(self.start)
            return start_index + self.parent.relative_start_q(n)
        else:
            raise RuntimeError("n is not a parent of current node")
        

class RefinementNodeLead(RefinementNode[T, QuarterIndex]):

    def __init__(self, start: float, end: float, name: str, vp: ViewPointLead, children: List[Self] = [], structure: bool = False):
        super().__init__(QuarterIndex(start), QuarterIndex(end), name, vp, children, structure)

    def update_elt_count(self) -> None:
        if self.buffer_valid:
            self.elt_count = len(self.buffer)
            return
        self.elt_count = 0
        for c in self.children:
            c.update_elt_count()
            self.elt_count += c.elt_count

    def zero_index(self) -> QuarterIndex:
        return QuarterIndex(0.0)

    def get_duration(self) -> float:
        return self.end - self.start

    def relative_start_p(self, n: Node) -> int:
        if self == n:
            return 0
        elif self.parent is not None:
            self.parent.update_buffer()
            start_p = self.parent.buffer.get_pos_index(self.start)
            return start_p + self.parent.relative_start_p(n)
        else:
            raise RuntimeError("n is not a parent of current node")

    def relative_start_q(self, n: Node) -> float:
        if self == n:
            return 0.0
        elif self.parent is not None:
            self.parent.update_buffer()
            return self.start + self.parent.relative_start_q(n)
        else:
            raise RuntimeError("n is not a parent of current node")


class ViewPoint(Generic[C, I]):

    def __init__(self, name: str, use_copy: bool, model: ur.Model):
        self.name: str = name
        self.use_copy: bool = use_copy
        self.model: ur.Model = model
        self.producers: List[ur.Producer] = []
        self.constraints: List[ur.Constraint] = []
        self.scorers: List[ur.Scorer] = []
        self.initialized: bool = False

    def __getitem__(self, name: str) -> RefinementNode[C, I]:
        return self.nodes[name]

    def get_lead(self) -> ViewPointLead:
        raise NotImplementedError()

    def initialize_structure(self) -> None:
        self.initialized = True
        self.nodes: Dict[str, RefinementNode[C, I]] = {}
        for n in PreOrderIter(self.root):
            self.nodes[n.name] = n
            if not self.use_copy or n.name[-1] != '\'':
                continue
            to_copy: str = n.name[:-1]
            if to_copy in self.nodes.keys():
                n.copy_of = self[to_copy]
                n.unset_generatable()


    def set_to(self, bars: list[C], fixedness: float = 1.0) -> None:
        raise NotImplementedError()

class ViewPointLead(ViewPoint[T, QuarterIndex]):
    def __init__(self, name: str, use_copy: bool, model: ur.Model):
        super().__init__(name, use_copy, model)
        self.follows: List[ViewPointFollow] = []

    def set_to(self, l: list[T], fixedness: float = 1.0) -> None:
        
        if not self.initialized:
            self.initialize_structure()

        new_content: list[T] = []
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
                n.set_to(n.copy_of.buffer.elements, fixedness)
            else:
                n.set_to(new_content, fixedness)
            new_content = []

        self.root.update_elt_count()
        self.root.print()

    def get_lead(self) -> ViewPointLead:
        return self

    def copy_struc_node(self, n: StructureNode) -> RefinementNodeLead[T]:
        '''Construct a RefinementNode by copying a StructureNode 
        '''
        new_node = RefinementNodeLead[T](n.start, n.end, n.name, self, structure=True)
        new_node.children = [self.copy_struc_node(c) for c in n.children]
        return new_node

    def initialize_structure(self) -> None:
        self.root: RefinementNodeLead[T] = self.copy_struc_node(self.model.structure)
        super().initialize_structure()

class ViewPointFollow(ViewPoint[C, PosIndex]):
    def __init__(self, name: str, use_copy: bool, model: ur.Model, lead: ViewPointLead):
        super().__init__(name, use_copy, model)
        self.lead: ViewPointLead = lead
        lead.follows.append(self)

    def set_to(self, l: list[C], fixedness: float = 1.0) -> None:
        # needs lead VP to be set first
        
        if not self.initialized:
            self.initialize_structure()

        for n in PreOrderIter(self.root):

            # only set content of leafs
            if n.children:
                continue
            n.update_elt_count()
            new_content: list[C] = l[:n.elt_count]
            l = l[n.elt_count:]
            if n.copy_of and self.use_copy:
                n.set_to(n.copy_of.buffer.elements, fixedness)
            else:
                n.set_to(new_content, fixedness)

        self.root.print()

    def get_lead(self) -> ViewPointLead:
        return self.lead

    def copy_lead_node(self, n: RefinementNodeLead[T], offset: int) -> RefinementNodeFollow[C]:

        new_node = RefinementNodeFollow[C](offset, offset + n.elt_count, n.name, self, structure=True, lead=n)
        new_node.elt_count = n.elt_count
        children: List[RefinementNodeFollow[C]] = []
        acc: int = 0
        for c in n.children:
            if c.structure:
                pass
            children.append(self.copy_lead_node(c, acc))
            acc += c.elt_count
        new_node.children = children
        return new_node

    def initialize_structure(self) -> None:
        self.root: RefinementNodeFollow[C] = self.copy_lead_node(self.lead.root, 0)
        super().initialize_structure()


