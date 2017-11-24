from pathlib import Path


class Node:

    def __init__(self, path: Path, children: list=None, relative_nodes: dict=None):

        if children is None:
            children = []
        if relative_nodes is None:
            relative_nodes = {}

        self.path = Path(path)
        self.children = children
        self.relative_nodes = relative_nodes

    def get_relative(self, label)-> 'Node':
        return self.relative_nodes[label]

    def add_relative(self, label: str, relative_path: Path)-> 'Node':
        node = Node(relative_path)
        self.relative_nodes[label] = node
        node.relative_nodes['orig'] = self
        return node

    def add_child(self, node: 'Node')-> 'Node':
        self.children.append(node)
        for key in node.relative_nodes:
            if key in self.relative_nodes:
                self.relative_nodes[key].children.append(node.relative_nodes[key])
        return node
