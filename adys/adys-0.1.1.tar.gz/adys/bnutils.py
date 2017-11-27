
import itertools
import re

import pydotplus

from .utils import *

class state:
    def __init__(self, *t):
        self._d = t

    @classmethod
    def zero(celf, n):
        v = (False,)*n
        return celf(*v)

    def update(self, i, v):
        v = self[:i] + (v,) + self[i+1:]
        return state(*v)

    def __len__(self):
        return self._d.__len__()
    def __getitem__(self, i):
        return self._d[i]

    def next(self):
        x = self
        for i in range(len(self)):
            if not x[i]:
                return x.update(i, True)
            else:
                x = x.update(i, False)
        return x

    def iszero(self):
        return not (True in self._d)
    def isone(self):
        return not (False in self._d)

    def __hash__(self):
        return hash(self._d)
    def __eq__(self, x):
        return self._d == x._d
    def __ne__(self, x):
        return self._d != x._d
    def __le__(self, x):
        return self._d <= x._d
    def __lt__(self, x):
        return self._d < x._d
    def __ge__(self, x):
        return self._d >= x._d
    def __gt__(self, x):
        return self._d > x._d
    def __repr__(self):
        return str(self)
    def __str__(self):
        return "".join(["1" if i else "0" for i in self._d])
    def __iter__(self):
        return self._d.__iter__()

    @classmethod
    def all(celf, n):
        x = celf.zero(n)
        yield x
        while not x.isone():
            x = x.next()
            yield x

    def dst(x, y):
        d = 0
        for i in range(len(x)):
            if x[i] != y[i]:
                d += 1
        return d



class graph(dict):
    def __init__(self):
        super(graph, self).__init__()
        self.parents = {}

    def register_node(self, n):
        if n not in self:
            self[n] = set()
        if n not in self.parents:
            self.parents[n] = set()

    def add_edge(self, n1, n2):
        assert n1 != n2
        self.register_node(n1)
        self.register_node(n2)
        self[n1].add(n2)
        self.parents[n2].add(n1)

    def to_dot(self, dotfile):
        with open(dotfile, "w") as f:
            f.write("digraph {\n")
            for n, children in self.items():
                f.write("%s;\n"% n)
                for m in children:
                    f.write("%s -> %s;\n" % (n, m))
            f.write("}\n")

    def to_pydot(self):
        g = pydotplus.Dot('', graph_type="digraph", strict=True)
        for n, children in self.items():
            g.add_node(pydotplus.Node(str(n)))
            for m in children:
                edge = pydotplus.Edge(str(n), str(m))
                g.add_edge(edge)
        return g

    def tarjan(g):
        global num
        num = 0
        P = []
        ret = []

        nums = {}
        root = {}

        def parcours(v):
            global num
            nums[v] = num
            root[v] = num
            num += 1
            P.append(v)

            for w in g[v]:
                if w not in nums:
                    parcours(w)
                    root[v] = min(root[v], root[w])
                elif w in P:
                    root[v] = min(root[v], nums[w])
            if root[v] == nums[v]:
                scc = set()
                w = None
                while w is None or w != v:
                    w = P.pop()
                    scc.add(w)
                ret.append(scc)

        for v in g:
            if v not in nums:
                parcours(v)

        return ret


re_var = re.compile("\\b([\\w\\d_]+)\\b")
re_varidx = re.compile("^x(\\d+)$")

def bn2py(bn):
    if isinstance(bn, str):
        bn = read_bn(bn)

    nodes = list(sorted(bn))

    def get_index(m):
        i = m.group(1)
        if i in ["True", "False"]:
            return i
        m = re_varidx.match(i)
        if m:
            i = int(m.group(1))
        return "x[%s]" % nodes.index(i)

    exprs = []
    for n in nodes:
        d = bn[n]
        d = d.replace("TRUE", "True")
        d = d.replace("FALSE", "False")
        d = re_var.sub(get_index, d)
        d = d.replace("|", " or ")
        d = d.replace("&", " and ")
        d = d.replace("!", " not ")
        exprs.append("lambda x: %s" % d.strip())

    return eval("(%s)" % ",".join(exprs))


sync = "sync"
async = "async"
general = "general"

def stategraph(f, mode):
    if isinstance(f, (str,dict)):
        f = bn2py(f)
    n = len(f)
    sg = graph()
    dims = list(range(n))
    def transitions(x, m, M):
        for k in range(m,M+1):
            for I in itertools.combinations(dims, k):
                y = x
                for i in I:
                    y = y.update(i, f[i](x))
                if y != x:
                    sg.add_edge(x,y)
    for x in state.all(n):
        sg.register_node(x)
        if mode == async:
            transitions(x, 1, 1)
        elif mode == sync:
            transitions(x, n, n)
        elif mode == general:
            transitions(x, 1, n)
    return sg

def basins(g, a):
    b = {}
    for i, scc in enumerate(a):
        # i est le numero de l'attracteur scc
        # x0 est un etat de depart appartenant a l'attracteur
        x0 = tuple(scc)[0]
        b[x0] = {i}
        todo = [x0]
        visited = set(todo)
        while todo:
            x = todo.pop()
            for y in g.parents[x]:
                if y not in visited:
                    visited.add(y)
                    todo.append(y)
                    if y not in b:
                        b[y] = {i}
                    else:
                        b[y].add(i)
    return b

def get_attractor_id(b, x):
    assert len(b[x]) == 1, "%s can reach different attractors" % x
    return list(b[x])[0]

