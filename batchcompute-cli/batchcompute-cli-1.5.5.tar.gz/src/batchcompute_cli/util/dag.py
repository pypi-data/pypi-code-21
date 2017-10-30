
from __future__ import print_function
from terminal import white

def draw(deps, matric=None):

    # window has not __curses module
    try:
        from drawille import Turtle

    except:
        print(white('DAG view in this system is unsupported.'))
        return

    if matric==None:
        matric = sortIndex(deps)

    t = Turtle()

    DX = 50
    DY = 5
    SUBLEN = 8

    ylen = max([len(i) for i in matric]) * DY

    m = {}
    c = 0
    for i,cols in enumerate(matric):
        cols.sort()
        for j,n in enumerate(cols):
            c+= 1
            pos = {'x': DX * i, 'y': DY * (j+1) * round(ylen/(len(cols)+1) ), 'n': n }

            m[n] = pos
            task_name = (n[:SUBLEN-1]+'..') if len(n)>SUBLEN else n
            t.set_text(pos.get('x'), pos.get('y'),  '%d.%s' %(c, task_name) )

    for k in deps:
        for k2 in deps[k]:
            t.brush_on = False
            t.move(m[k].get('x'),m[k].get('y'))
            t.brush_on = True
            t.move(m[k2].get('x'),m[k2].get('y'))

    s = t.frame()

    print(s)
    return len(s.split('\n'))



def sortIndex(deps):
    matric = []
    #1. getFirstColumn
    matric.append(getFirstColumn(deps))

    #2. addChildren
    while (addChildren(deps, matric)):
        pass
    #3. removeLowTargets
    return removeLowTargets(matric)



def getFirstColumn(deps):

    allTargets = set()
    for k in deps:
        allTargets = allTargets | set(deps[k])
    allTargets = [i for i in allTargets]

    t = []
    for k in deps:
        if k not in allTargets:
            t.append(k)
    return t


def addChildren(deps, matric):
    lastCol = matric[-1]

    nextCol = set()

    for n in lastCol:
        if deps.get(n):
            nextCol =  nextCol | set(deps.get(n))
    nextCol = [i for i in nextCol]

    if len(nextCol) == 0:
        return False
    else:
        matric.append(nextCol)
        return True



def removeLowTargets(matric):
    m = {}
    for i,n in enumerate(matric):
        for j,n2 in enumerate(n):
            pos = m.get(n2)
            if pos:
                if pos.get('x') < i:
                    #remove
                    matric[pos.get('x')].pop(pos.get('y'))
                    m[n2]  = {'x':i, 'y':j}
            else:
                m[n2] = {'x':i, 'y':j}
    return matric

