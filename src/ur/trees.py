from anytree import NodeMixin, RenderTree, PreOrderIter
from anytree.exporter import DotExporter
from typing import Self, Generic, TypeVar, Optional, Callable, Dict
from copy import copy
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
    
    def duration(self) -> int:
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
            print(treestr.ljust(8), node.start, node.end)

    def export_to_dot(self, filename: str):
        with open(filename, 'w') as file:
            file.writelines(DotExporter(self))


class StructureTree(Generic[T]):

  def __init__(self, root: RefinementNode):
    self.root: RefinementNode[T] = root
    


class ViewPoint(Generic[T]):

    def __init__(self, name: str, template: StructureTree):
        self.name: str = name
        self.tree: RefinementNode = copy(template.root)
        self.nodes: Dict[str, RefinementNode[T]] = {}
        for n in PreOrderIter(self.tree):
          self.nodes[n.name] = n
          if n.name[-1] == '\'':
            to_copy: str = n.name[:-1]
            if to_copy in self.nodes.keys():
              n.copy_of = self.nodes[to_copy]
              n.unset_generatable()


    def set_to(self, val: list[list[T]]):
      for n in PreOrderIter(self.tree):
        # only set content of leafs
        if n.children == []:
          if n.copy_of:
            n.content = n.copy_of.content
          else:
            for i in range(n.duration):
              n.content += val.pop(0)