
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
    def __init__(self, quarter: float, pos: int):
        self.quarter: float = quarter
        self.pos: int = pos
        self.node: RefinementNode

    def __add__(self, other: Self) -> Self:
        return self.__init__(0)

    def __sub__(self, other: Self) -> Self:
        return self.__init__(0)

    def __str__(self) -> str:
        return f"({self.quarter}, {self.pos})"

    def relative_p(self, label = 'ALL') -> int:
        if self.node.name == label:
            return self.pos - self.node.start.pos
        elif self.node.parent is not None:
            return self.pos + self.node.parent.start.relative_p(label)
        else:
            raise RuntimeError("n is not a parent of current node")

    def relative_q(self, label = 'ALL') -> float:
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
        self.quarter = sum(durations)
        self.pos = offset + self.node.start.pos
    

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
    def __init__(self, start: float, end: float, name: str, children: List[Self] = []):
        super().__init__(start, end, name, children)

class RefinementNode(Node[Index]):

    def __init__(self, start: Index, end: Index, name: str, vp: ViewPoint, children: List[Self] = [], structure: bool = False):
        super().__init__(start, end, name, children)
        self.start.node = self
        self.end.node = self
        self.copy_of: Optional[Self] = None
        self.generatable: bool = True
        self.generator: Optional[ur.Generator] = None
        self.fixedness: float = .0
        
        self.structure: bool = structure
        self.vp: ViewPoint = vp

    def __iter__(self):
        for e in self.vp.out[self.start.pos:self.end.pos]:
            yield e

    def index(self) -> Index:
        i = Index(0.0, 0)
        i.node = self
        return i

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


    def set_to(self, content: List[C], fixedness: float) -> None:
        self.fixedness = fixedness

        self.vp.out[self.start.relative_p():self.end.relative_p()] = content
        old_length = self.end.pos - self.start.pos
        self.increase_size(len(content) - old_length)

        if self.parent is not None:
            self.parent.update_fixedness()
        
        for vp in self.vp.fixed_count_out:
            # for now:
            assert self.structure
            vp.nodes[self.name].set_to([vp.undefined()] * len(content), 0.0)

    def generate(self) -> None:
        if self.fixedness > 0.0:
            return
        if self.copy_of is not None:
            self.set_to(self.vp[self.copy_of.start:self.copy_of.end], 1.0) # TODO: not sure if sensible
        if not self.generatable:
            for c in self.children:
                c.generate()
            return 
        if not self.generator:
            self.generator = ur.Generator(self)
        new_content, fixedness = self.generator.generate()
        self.set_to(new_content, fixedness)

    def __str__(self) -> str:
        out: str = ""
        for pre, _, node in RenderTree(self):
            treestr = u"%s%s" % (pre, node.name)
            content_str = ""
            if node.copy_of is not None:
                content_str += f' (same as {node.copy_of.name})'
            out += treestr.ljust(8) + str(node.start) + str(node.end) + content_str + "\n"
        return out


class RefinementNodeFollow(RefinementNode):
    pass
        

class RefinementNodeLead(RefinementNode):
    pass

class ViewPoint(Generic[C]):

    def __init__(self, name: str, content_cls: Type[C], use_copy: bool, model: ur.Model):
        self.name: str = name
        self.use_copy: bool = use_copy
        self.model: ur.Model = model
        self.producers: List[ur.Producer] = []
        self.constraints: List[ur.Constraint] = []
        self.scorers: List[ur.Scorer] = []
        self.initialized: bool = False
        self.out: List[C] = []
        self.content_cls: Type[C] = content_cls
        self.fixed_count_out: List[ViewPoint] = []
        self.fixed_count_in: Optional[ViewPoint] = None
        self.generated: bool = False
    
    def get_pos(self, i: Index) -> int:
        if i.node.vp.get_leader() == self.get_leader():
            return i.relative_p()

        struc_parent: RefinementNode = i.node.get_structure_parent()
        ind_q: float = i.relative_q(struc_parent.name)
        acc: float = 0.0
        for (ctr, e) in enumerate(self.get_leader()[self.nodes[struc_parent.name].start:]):
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
        self.initialized = True
        self.nodes: Dict[str, RefinementNode] = {}
        self.root: RefinementNode = self.copy_struc_node(self.model.structure)
        i: int = 0
        for n in PreOrderIter(self.root):
            self.nodes[n.name] = n
            if not self.use_copy or n.name[-1] != '\'':
                continue
            to_copy: str = n.name[:-1]
            if to_copy in self.nodes.keys():
                n.copy_of = self.nodes[to_copy]
                n.unset_generatable()

    def set_to(self, bars: list[C], fixedness: float = 1.0) -> None:
        raise NotImplementedError()

    def undefined(self) -> C:
        return self.content_cls.undefined()

    def copy_struc_node(self, n: StructureNode, offset: int = 0) -> RefinementNode:
        '''Construct a RefinementNode by copying a StructureNode 
        '''
        if not n.children:
            self.out.append(self.undefined())
            return RefinementNode(Index(n.start, offset), Index(n.end, offset + 1), n.name, self, structure=True)
        children = []
        offset_children = 0
        for c in n.children:
            child_node = self.copy_struc_node(c, offset_children)
            children.append(child_node)
            offset_children = child_node.end.pos
        return RefinementNode(Index(n.start, offset), Index(n.end, offset + offset_children), n.name, self, children=children, structure=True)

    def generate(self) -> None:
        self.generated = True
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
    def __init__(self, name: str, content_cls: Type[T], use_copy: bool, model: ur.Model):
        super().__init__(name, content_cls, use_copy, model)
        self.followers: List[ViewPointFollow] = []

    def initialize_to(self, l: list[T], fixedness: float = 1.0) -> None:
        ''' For now, lead needs to be set first'''
        self.generated = True
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
                n.set_to(self[n.copy_of.start:n.copy_of.end], fixedness)
            else:
                n.set_to(new_content, fixedness)
            new_content = []

        print(self)

    def get_leader(self) -> ViewPointLead:
        return self

class ViewPointFollow(ViewPoint[C]):
    def __init__(self, name: str, content_cls: Type[C], use_copy: bool, model: ur.Model, lead: ViewPointLead):
        super().__init__(name, content_cls, use_copy, model)
        self.leader: ViewPointLead = lead
        lead.followers.append(self)

    def initialize_to(self, l: list[C], fixedness: float = 1.0) -> None:
        ''' assume that lead VP is set first''' 
        assert self.fixed_count_in is not None and self.fixed_count_in.generated
        self.generated = True
        for n in PreOrderIter(self.root):

            # only set content of leafs
            if n.children:
                continue
            new_content: list[C] = l[:n.get_elt_count()]
            l = l[n.get_elt_count():]
            if n.copy_of and self.use_copy:
                n.set_to(self[n.copy_of.start:n.copy_of.end], fixedness)
            else:
                n.set_to(new_content, fixedness)

        print(self)

    def get_leader(self) -> ViewPointLead:
        return self.leader