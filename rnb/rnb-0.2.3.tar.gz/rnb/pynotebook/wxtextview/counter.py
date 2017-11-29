# -*- coding: latin-1 -*-

# 1.4.17 -> Problem bei remove, siehe test_01

nmax = 15
class Increment:
    def __init__(self, level, n=0):
        self.n = n
        self.level = level
            
class FixedValue:
    def __init__(self, level, value, n=0):
        self.n = n
        self.level = level
        self.value = value
                
class Group:
    def __init__(self, childs):
        self.childs = tuple(childs)
        n = 0
        for c in childs:
            n += c.n
        self.n = n 
        
def dump(tree, i0=0, d=0):
    if isinstance(tree, Increment):
        print "    "*d, i0+tree.n, "INC", tree.level
    elif isinstance(tree, FixedValue):
        print "    "*d, i0+tree.n, "SET", tree.level, tree.value
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
    if len(stuff)==1:
        return stuff[0]        
    return Group(stuff)

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
        
class Counter:
    def __init__(self):
        self.tree = Group([])
        
    def increase(self, i, level):
        m = Increment(level, i)
        self.tree = grouped(add_modifier(self.tree, i, m))
        
    def set(self, i, level, value):
        m = Increment(level, i)
        self.tree = grouped(add_modifier(self.tree, i, m))

    def insert(self, i, n):
        insert(self.tree, i, n)

    def remove(self, i1, i2):
        if not 0 <= i1 <= i2:
            raise IndexError((i1, i2))
        self.tree = grouped(remove(self.tree, i1, i2))

    def _dump(self):
        dump(self.tree)
        
            
# XXX should remove nodes from tree. Replace this!
def remove(tree, i1, i2):
    assert i2 >= i1 >= 0
    tree.n -= max(min(i2, tree.n) - max(i1, 0), 0)
    if isinstance(tree, Group):
        for child in tree.childs:
            j = child.n
            child.n -=  max(min(i2, j) - max(i1, 0), 0)
            i1 -= j
            i2 -= j
            if i2 <= 0:
                break  
                

      
                      
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
    
    
def remove(tree, i1, i2):
    assert i2 >= i1 >= 0
    if i1 == i2:
        return []
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
    b = Counter()
    b.increase(10, CHAPTER)
    b._dump()
    b.remove(20, 30)
    b._dump() # -> 20 INC 0 --> da ist was faul mit remove!


test_01()
