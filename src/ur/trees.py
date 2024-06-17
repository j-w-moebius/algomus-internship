from anytree import NodeMixin, RenderTree, PreOrderIter
from anytree.exporter import DotExporter
from typing import Self, Generic, TypeVar, Optional, Callable, Dict
import copy
import music

T = TypeVar('T')

class RefinementNode(NodeMixin, Generic[T]):

    def __init__(self, start: int, end: int, name: str, *children: Self):
        self.start: int = start
        self.end: int = end
        self.name: str = name
        self.content: list[T] = []
        self.children = children
        self.copy_of: Optional[Self] = None
        self.generatable: bool = True
    
    def get_duration(self) -> int:
        return self.end - self.start

    def global_start(self) -> int:
      result: int = self.start
      if self.parent:
        result += self.parent.global_start()
      return result

    def unset_generatable(self):
      self.generatable = False
      # propagate change upwards
      if self.parent:
        self.parent.unset_generatable()

    def print(self):
        for pre, _, node in RenderTree(self):
            treestr = u"%s%s" % (pre, node.name)
            content_str = '[' + ' '.join([str(c) for c in node.content]) + ']'
            print(treestr.ljust(8), node.start, node.end, content_str)

    def export_to_dot(self, filename: str):
        with open(filename, 'w') as file:
            file.writelines(DotExporter(self))


class ViewPoint(Generic[T]):

  def __init__(self, name: str, use_copy: bool = True):
    self.name: str = name
    self.use_copy: bool = use_copy

  def set_structure(self, struc: RefinementNode) -> None:
    self.root: RefinementNode = struc
    
  def set_structurer(self, structurer: Self) -> None:
    self.structurer: Self = structurer

  def inherit_structure(self) -> None:
    self.root = copy.deepcopy(self.structurer.root)
    self.nodes: Dict[str, RefinementNode[T]] = {}
    for n in PreOrderIter(self.root):
      self.nodes[n.name] = n
      if self.use_copy:
        if n.name[-1] == '\'':
          to_copy: str = n.name[:-1]
          if to_copy in self.nodes.keys():
            n.copy_of = self.nodes[to_copy]
            n.unset_generatable()


  def set_to(self, bars: list[list[T]], fixedness: float = 1.0) -> None:

    self.inherit_structure()

    for n in PreOrderIter(self.root):
      # only set content of leafs
      if not n.children:
        if n.copy_of and self.use_copy:
          n.content = n.copy_of.content
        for i in range(n.get_duration()):
          new_bar: list[T] = bars.pop(0)
          if not (n.copy_of and self.use_copy):
            n.content += new_bar

    self.root.print()