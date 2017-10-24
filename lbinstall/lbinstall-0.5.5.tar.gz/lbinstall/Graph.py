###############################################################################
# (c) Copyright 2012-2016 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''


:author: Stefan-Gabriel Chitic
'''
from collections import deque


class Graph(object):
    """
    Object to represent the packages to be installed as an oriented graph where
    nodes are connected by their dependencies.
    """
    def __init__(self):
        """ initializes a graph object """
        self.__graph_dict = {}
        self.__graph_nodes = []
        self.__topological_order = []
        self.__packages = {}

    def vertices(self):
        """ Returns the vertices of a graph

        :returns: the list of vertices
        """
        return list(self.__graph_dict.keys())

    def edges(self):
        """ Returns the edges of a graph

        :returns: the list of edges"""
        return self.__generate_edges()

    def add_vertex(self, vertex, package):
        """
        If the vertex "vertex" is not in self.__graph_dict, a key "vertex" with
        an empty list as a value is added to the dictionary. Otherwise nothing
        has to be done.

        :param vertex: the vertex that will be added
        :param package: the package represented by the vertex
        """
        self.__topological_order = []
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []
            self.__graph_nodes.append(vertex)
            self.__packages[vertex] = package

    def add_edge(self, edge):
        """ Addes a edge to the graph

        :param edge: a tuple representing the source vertex and the destination
                     vertex
        """
        (vertex1, vertex2) = edge
        Nertex1 = "%s|%s|%s" % (vertex1.name,
                                vertex1.version,
                                vertex1.release)
        Nertex2 = "%s|%s|%s" % (vertex2.name,
                                vertex2.version,
                                vertex2.release)
        self.add_vertex(Nertex1, vertex1)
        self.add_vertex(Nertex2, vertex2)
        if Nertex1 in self.__graph_dict:
            self.__graph_dict[Nertex1].append(Nertex2)
        else:
            self.__graph_dict[Nertex1] = [Nertex2]

    def getPackageOrder(self):
        """ Sets the graphs in a topological order

        :returns: the list of packages in the topological order
        """
        self.topological()
        package_list = []
        for name in self.__topological_order:
            package_list.append(self.__packages[name])
        return package_list

    def topological(self):
        """ Sets the graphs in a topological order

        It checks first fi the topological order has changed, then eliminates
        the cycles in the graph and in the end it orders them in a topological
        list
        """
        if len(self.__topological_order):
            return
        self.eliminate_cycles()
        self._topological()

    def _topological(self):
        """ Internal function to do the actual sorting. It requires no
        cycles in the graph
        """
        order, enter, state = deque(), set(self.__graph_dict), {}
        GRAY, BLACK = 0, 1

        def dfs(node):
            state[node] = GRAY
            for k in self.__graph_dict.get(node, ()):
                sk = state.get(k, None)
                if sk == GRAY:
                    raise ValueError("cycle")
                if sk == BLACK:
                    continue
                enter.discard(k)
                dfs(k)
            order.appendleft(node)
            state[node] = BLACK
        while enter:
            dfs(enter.pop())
        order = list(order)
        for o in order[::-1]:
            self.__topological_order.append(o)

    def __generate_edges(self):
        """ A static method generating the edges of the
            graph "graph". Edges are represented as sets
            with one (a loop back to the vertex) or two
            vertices
        """
        edges = []
        for vertex in self.__graph_dict:
            for neighbour in self.__graph_dict[vertex]:
                if (vertex, neighbour) not in edges:
                    edges.append((vertex, neighbour))
        return edges

    def eliminate_cycles(self, print_cycle=False):
        """ Eliminates the cycles in the graph

        :param print_cycle: Flag used to print the cycles if present
        """
        if len(self.__graph_nodes) == 0:
            return
        self._eliminate_cycles(self.__graph_nodes[0],
                               print_cycle=print_cycle)

    def _eliminate_cycles(self, vertex, visited=[], print_cycle=False):
        """
        Internal function to remove cycles
        :param vertex: the root vertex
        :param visited: the list of visited vertexes
        :param print_cycle: flag used to print the cycles if present

        :returns: (the visited vertexes list, flag to notify if a cycle was
                  found)
        """
        if vertex in visited:
            if print_cycle:
                visited.append(vertex)
                print("\nCycle found:\n%s" % '-\n'.join(visited))
                visited.pop()
            return (visited, True)
        visited.append(vertex)
        new_edges = []
        for edge in self.__graph_dict[vertex]:
            visited, strats_cycle = self._eliminate_cycles(
                edge, visited=visited, print_cycle=print_cycle)
            if not strats_cycle:
                new_edges.append(edge)
            if len(visited):
                visited.pop()
        self.__graph_dict[vertex] = new_edges
        return (visited, False)

    def generate_dot(self, tree_mode=False, filename="output"):
        """
        A static method generating the dot file

        :param tree_mode: if True, the graph will be changed to a tree where a
                          a leaf is placed in the last position of the
                          topological order that have a connection to it.
        :param filename: the output filename for the dot file
        """
        self.topological()
        edges = []
        if '.dot' not in filename:
            filename = "%s.dot" % filename
        with open(filename, 'w') as f:
            f.write('digraph {\n')
            nodes = self.__topological_order
            for vertex in nodes:
                f.write('\t%d [label="%s"];\n' % (
                    nodes.index(vertex),
                    vertex.replace('|', '-')))
            visited = []
            for vertex in nodes:
                for edge in self.__graph_dict[vertex]:
                    if tree_mode and edge in visited:
                        continue
                    visited.append(edge)
                    f.write('\t%d -> %d;\n' % (
                        nodes.index(vertex),
                        nodes.index(edge)))
            f.write('}')
        imgage_file = filename.replace('.dot', '')
        print("In order to generate a svg file use:\n")
        print("dot -Goverlap=false -Ksfdp -Tsvg %s > %s.svg\n" %
              (filename, imgage_file))
        print("In order to generate a svg file use:\n")
        print("display ./%s.svg\n" % imgage_file)

    def __str__(self):
        """ Converts the graph to string"""
        res = "vertices: "
        for k in self.__graph_dict:
            res += str(k) + " "
        res += "\nedges: "
        for edge in self.__generate_edges():
            res += str(edge) + " "
        return res
