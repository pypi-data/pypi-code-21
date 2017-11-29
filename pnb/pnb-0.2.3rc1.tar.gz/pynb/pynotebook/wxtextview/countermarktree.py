# -*- coding: latin-1 -*-

"""TODO: 

updatecount() braucht den state der Startposition! Wir brauchen also
eine effiziente Methode um den zu ermitteln. Eine denkbare Lösung wäre
ein spezielles Gewicht für alle Modifier-Noden.

"""
"""
Countertree+Marktree

Konzept: 
- Kombination des bisherigen Coutnertree und des Marktree
- Marktree verlangt eine doppelt verlinkte Struktur

Begriffe:
- Counter ist die Hülle (analog TextModel)
- Modifier (Increment, FixedValue)

Baumstruktur:
- Jedes Blatt ist ein Modifier oder eine Marke
- Jedes Blatt erstreckt sich über einen Bereich n>=0
- Die Ausführung des Befehls geschieht erst an der Position n
- n ist also der Abstand zum letzten Modifier nach links
- n kann auch 0 sein, sodass verschiedene Aktionen an der selben 
  Indexposition stattfinden können
- Die Aktion ist mit dem Index rechts daneben verknüpft
- Das hat Auswirkungen auf das Löschen:
  * wird 0 bis n gelöscht, dann bleibt die Aktion erhalten
  * wird dagegen n bis n+1 gelöscht, dann verschwindet die Aktion
"""


nmax = 15

class Node:
    parent = None
    n = 0

class Mark(Node):
    def __init__(self, label, n=0):
        self.n = n
        self.label = label
        
    def get(self):
        if not self.parent:
            return self.n
        return abspos(self)+self.n
        
class Increment(Node):
    def __init__(self, level, n=0):
        self.n = n
        self.level = level
            
class FixedValue(Node):
    def __init__(self, level, value, n=0):
        self.n = n
        self.level = level
        self.value = value
                
class Group(Node):
    def __init__(self, childs):
        self.childs = tuple(childs)
        n = 0
        for c in childs:
            c.parent = self    
            n += c.n
        self.n = n 
        
def dump(tree, i0=0, d=0):
    if isinstance(tree, Increment):
        print "    "*d, i0+tree.n, "INC", tree.level
    elif isinstance(tree, FixedValue):
        print "    "*d, i0+tree.n, "SET", tree.level, tree.value
    elif isinstance(tree, Mark):
        print "    "*d, i0+tree.n, "Mark %s"%repr(tree.label)
    elif isinstance(tree, Group):
        print "    "*d, i0, "Group"
        for c in tree.childs:
            dump(c, i0, d+1)
            i0 += c.n
        
def groups(l):
    # Create one or two groups out of l. It is assumed, that len(l) <=
    # nmax+1.
    assert len(l) <= nmax+1
    if len(l) <= nmax:
        return [Group(l)]
    n = nmax // 2
    return [Group(l[:n]), Group(l[n:])]


def grouped(stuff):
    while len(stuff) > nmax:
        stuff = groups(stuff)
    if len(stuff) == 1:
        return stuff[0]
    return Group(stuff) # if stuff is empty or if it has more than 1 element
    
def depth(tree):
    d = 0
    if isinstance(tree, Group):
        for child in tree.childs:
            d = max(d, depth(child))
        d += 1
    return d

def insert(tree, i, n):
    if 0 <= i <= tree.n:
        tree.n += n
    if isinstance(tree, Group):
        for child in tree.childs:
            j = child.n
            if i <= j:
                insert(child, i, n)
                break
            i -= j    
            
def add_modifier(tree, i, m):
    if isinstance(tree, Group):
        if not tree.childs:
            m.n = i
            return [m]
        l = []
        for k, child in enumerate(tree.childs):
            l.append(child)
            i -= child.n
            if i <= 0:
                break
        l.pop()
        l.extend(add_modifier(child, i+child.n, m))
        l.extend(tree.childs[k+1:])
        return groups(l)
    elif i >= tree.n:
        m.n = i-tree.n
        return [tree, m]
    else:
        m.n = i
        tree.n -= i        
        return [m, tree]            

def remove(tree, i1, i2): 
    """
- Das hat Auswirkungen auf das Löschen:
  * wird 0 bis n gelöscht, dann bleibt die Aktion erhalten
  * wird dagegen n bis n+1 gelöscht, dann verschwindet die Aktion

"""
    # XXX Sollte der Algorithmus auf das Carryover-Konzept geändert werden?
    assert i2 >= i1 >= 0
    if i1 == i2 or i1 > tree.n: # XXX  > oder >= ?
        return [tree]
    n = tree.n
    n = n-min(n, i2)+max(0, i1)
    i = i1
    if isinstance(tree, Group):
        l = []
        for child in tree.childs:
            j = child.n
            if i1 <= 0 and j < i2:
                pass
            elif i2 <= 0 or j < i1:
                l.append(child)
            else:
                i -= i1
                l.extend(remove(child, i1, i2))               
            i1 -= j
            i2 -= j
        g = Group(l)
        if g.n < n and i < g.n: # Das AND ist nötig, da rechts von
                                # einer Node kein Leeraum eingefügt
                                # werden kann. Die Assertion könnte
                                # damit nicht erfüllt werden.
            print "inserting! i=", i
            insert(g, i, n-g.n)
            tmp = Group(l)
            assert tmp.n == n
        return [g]
    else:
        if i1 <= tree.n < i2:
            return []
        tree.n = n
        return [tree]


def remove(tree, i1, i2):  # Variante mit Carryover
    assert i2 >= i1 >= 0
    if i1 == i2 or i1 > tree.n: # XXX  > oder >= ?
        return [tree], 0
    n = tree.n
    n = n-min(n, i2)+max(0, i1)
    i = i1
    if isinstance(tree, Group):
        l = []
        co = 0
        for child in tree.childs:
            j = child.n
            if i1 <= 0 and j < i2:
                pass
            elif i2 <= 0 or j < i1:
                child.n += co
                co = 0
                l.append(child)
            else:
                i -= i1
                l1, co = remove(child, i1, i2)
                l.extend(l1)               
            i1 -= j
            i2 -= j
        return [Group(l)], co
    else:
        if i1 <= tree.n < i2:
            return [], 0
        tree.n = n
        return [tree], 0

        
def remove_mark(tree, mark, i):
    if tree is mark:
        if i != mark.n:
            raise IndexError(i) # Wrong index position
        mark.parent = None
        return [], mark.n
    if not isinstance(tree, Group):
        return [tree], 0 # this is ok!
    l = []
    co = 0 # carry over
    for child in tree.childs:
        if co:
            insert(child, 0, co)
            co = 0
        n = child.n
        if i < 0 or n < i:
            l.append(child)
        else:
            l1, co = remove_mark(child, mark, i)
            l.extend(l1)
        i -= n
    g = Group(l)
    assert co == tree.n-g.n
    return [g], co
                       
def abspos(node):
    p = node.parent
    if p is None:
        return 0
    i = 0
    for c in p.childs:
        if c is node:
            return i+abspos(p)
        i += c.n 
    raise Exception() # bad tree structure 
    
def all_marks(tree, i0=0):
    if isinstance(tree, Mark):
        return [(i0+tree.n, tree)]
    l = []
    for child in tree.childs:
        l.extend(all_marks(child, i0))
        i0 += child.n
    return l
    
def update_counts(tree, i, state):
    if isinstance(tree, Group):
        for child in tree.childs:
            if i<child.n:
                done = update_counts(child, i, state)
                if done:
                    return True
                i -= child.n
        return False
    else:
        if i> tree.n:
            return False
        if isinstance(tree, Increment):
            state[tree.level] += 1
        elif isinstance(tree, FixedValue):
            state[tree.level] = tree.value
        done = tree.state == tuple(state)
        if not done: 
            print "changing ", tree.state, "to", state
        else:
            print "done at", state
        tree.state = tuple(state)
        return done
                 
def dump_counts(tree, i0=0):
    if isinstance(tree, Group):
        for child in tree.childs:
            dump_counts(child, i0)
            i0 += child.n
    elif isinstance(tree, Modifier):
        print i0, tree.state

                        
class Counter:
    def __init__(self):
        self.tree = Group([])
        
    def increase(self, i, level):
        m = Increment(level)
        self.tree = grouped(add_modifier(self.tree, i, m))
        
    def set(self, i, level, value):
        m = FixedValue(level, valuei)
        self.tree = grouped(add_modifier(self.tree, i, m))

    def create_mark(self, i, label=''):
        m = Mark(label)
        self.tree = grouped(add_modifier(self.tree, i, m))
        return m

    def remove_mark(self, m):
        i = m.get()
        self.tree = grouped(remove_mark(self.tree, m, i)[0])
                
    def insert(self, i, n):
        if n<0:
            raise ValueError(n)
        insert(self.tree, i, n)

    def remove(self, i1, i2):
        if not 0 <= i1 <= i2:
            raise IndexError((i1, i2))
        self.tree = grouped(remove(self.tree, i1, i2)[0])

    def _dump(self):
        dump(self.tree)
        
    def _all_marks(self):
        return all_marks(self.tree)

    def _get_labels(self):
        return [(i, m.label) for (i, m) in self._all_marks()]
        

                      
CHAPTER, SECTION, PAGE = range(3)
def print_toc(tree, v=None, i0=0):
    if v is None:
        v = [0, 0, 0]
    if isinstance(tree, Group):
        for c in tree.childs:
            print_toc(c, v, i0)
            i0 += c.n
        return    
    if isinstance(tree, Increment):
        v[tree.level] += 1
    elif isinstance(tree, FixedValue):
        v[tree.level] = tree.value
    for i in range(tree.level+1, 3):
        v[i] = 0        
    print tree.n+i0, "%i.%i.%i" % tuple(v)
    
    
   

def test_00():
    counter = Counter()
    counter.increase(10, CHAPTER)
    counter.increase(15, SECTION)    
    counter.increase(19, PAGE)
    counter.increase(18, PAGE)
    counter.increase(17, PAGE)
    counter._dump()

    counter.remove(5, 10)
    counter._dump()

    counter.remove(10, 11)
    counter._dump()

    counter.insert(17, 100)
    counter._dump()

    counter.remove(17, 117)
    counter._dump()

    counter.increase(20, CHAPTER)
    counter.increase(21, PAGE)
    counter.increase(21, PAGE)

    print_toc(counter.tree)
    
def test_01():
    "add_mark"
    b = Counter()
    A = b.create_mark(0, 'A')
    B = b.create_mark(1, 'B')
    C = b.create_mark(2, 'C')
    assert b._get_labels() == [(0, 'A'), (1, 'B'), (2, 'C')]
    assert A.get() == 0
    assert B.get() == 1
    assert C.get() == 2

    b = Counter()
    A = b.create_mark(10, 'A')
    B = b.create_mark(15, 'B')
    C = b.create_mark(5, 'C')
    #b._dump()    
    assert b._get_labels() == [(5, 'C'), (10, 'A'), (15, 'B')]

    global nmax
    nmax = 5
    for i in range(10):
        b.create_mark(i, 'X%i'%i)
    assert depth(b.tree) == 2
    #b._dump()
    assert b._get_labels() == [(0, 'X0'), (1, 'X1'), (2, 'X2'), (3, 'X3'), 
        (4, 'X4'), (5, 'C'), (5, 'X5'), (6, 'X6'), (7, 'X7'), (8, 'X8'), 
        (9, 'X9'), (10, 'A'), (15, 'B')]
    
def test_02():
    "remove_mark"
    b = Counter()
    global nmax
    nmax = 5
    #A = b.create_mark(5, 'A')
    m = []
    for i in range(6):
        m.append(b.create_mark(i, 'X%i'%i))    
    assert b._get_labels() == [(0, 'X0'), (1, 'X1'), (2, 'X2'), 
                               (3, 'X3'), (4, 'X4'), (5, 'X5')]

    for i in range(6):
        #print i, m[i].get()
        assert m[i].get() == i

    #b._dump()
    assert depth(b.tree) == 2
    b.remove_mark(m[0])
    assert m[0].parent is None
    #assert m[0].get() is None

    assert m[4].get() == 4
    b.remove_mark(m[5])
    assert m[5].parent is None
    #assert m[5].get() is None
    assert b._get_labels() == [(1, 'X1'), (2, 'X2'), (3, 'X3'), (4, 'X4')]


    b.remove_mark(m[3])
    assert m[3].parent is None
    #assert m[3].get() is None
    #b._dump()

    #print b._get_labels()
    assert b._get_labels() == [(1, 'X1'), (2, 'X2'), (4, 'X4')]


    b = Counter()
    m = []
    for i in range(6):
        m.append(b.create_mark(10+i, 'X%i'%i))    
    assert b._get_labels() == [(10, 'X0'), (11, 'X1'), (12, 'X2'), 
                               (13, 'X3'), (14, 'X4'), (15, 'X5')]
    b.remove_mark(m[0])
    assert b._get_labels() == [(11, 'X1'), (12, 'X2'), 
                               (13, 'X3'), (14, 'X4'), (15, 'X5')]

def test_03():
    "insert"
    b = Counter()
    A = b.create_mark(10, 'A')
    B = b.create_mark(10, 'B')
    C = b.create_mark(15, 'C')

    b.insert(16, 1)
    assert b._get_labels() == [(10, 'A'), (10, 'B'), (15, 'C')]

    b.insert(15, 1)
    assert b._get_labels() == [(10, 'A'), (10, 'B'), (16, 'C')]

    b.insert(15, 1)
    assert b._get_labels() == [(10, 'A'), (10, 'B'), (17, 'C')]

    b.insert(10, 1)
    assert b._get_labels() == [(11, 'A'), (11, 'B'), (18, 'C')]

def test_04():
    "remove"
    b = Counter()
    A = b.create_mark(10, 'A')

    b.remove(9, 10)
    assert b._get_labels() == [(9, 'A')]
    b._dump()

    b.remove(20, 21)
    b._dump()
    assert b._get_labels() == [(9, 'A')]

    b.remove(11, 12)
    assert b._get_labels() == [(9, 'A')]

    b.remove(0, 9)
    assert b._get_labels() == [(0, 'A')]

    b.remove(0, 1)
    assert b._get_labels() == []

    b = Counter()
    A = b.create_mark(10, 'A')
    B = b.create_mark(10, 'B')
    C = b.create_mark(15, 'C')

    b.remove(14, 15)
    assert b._get_labels() == [(10, 'A'), (10, 'B'), (14, 'C')]

    b.remove(13, 20)
    assert b._get_labels() == [(10, 'A'), (10, 'B')]

    b.remove(5, 20)
    assert b._get_labels() == []


