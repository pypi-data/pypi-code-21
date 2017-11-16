from dxpy.filesystem import Path
from treelib import Node, Tree


class PathTree:
    def __init__(self):
        self.tree = Tree()
        self.create_node()

    @classmethod
    def _resolve_path(cls, name, path_parent):
        if name is None:
            if path_parent is None:
                return None, Path('/').abs
            else:
                raise TypeError("Name is None while path_parent is not None")
        else:
            if path_parent is None:
                return Path('/').abs, (Path('/') / name).abs
            else:
                return Path(path_parent).abs, (Path(path_parent) / name).abs

    def create_node(self, name=None, path_parent=None, data=None):
        path_parent, path_current = self._resolve_path(name, path_parent)
        if path_parent is not None and self.get_node(path_parent) is None:
            self.create_node(Path(path_parent).name,
                             Path(path_parent).father, None)
        return self.tree.create_node(name, path_current, parent=path_parent, data=data)

    def get_node(self, path):
        return self.tree.get_node(path)
    

    def get_data(self, path):
        return self.get_node(path).data

    def sub_tree(self, path):
        return self.tree.sub_tree(path)
