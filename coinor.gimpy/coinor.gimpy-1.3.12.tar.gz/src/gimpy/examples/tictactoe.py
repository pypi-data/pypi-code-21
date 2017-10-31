try:
    from coinor.gimpy import Graph
    from coinor.gimpy import DIRECTED_GRAPH
except:
    from src.gimpy import Graph
    from src.gimpy import DIRECTED_GRAPH

import random

g = Graph(display='off',type=DIRECTED_GRAPH, splines = 'true', K = 9,
          rankdir = 'LR', layout = 'dot')

g.add_node('Start')
for i in range(1,10):
    g.add_node((i,))
    g.add_edge('Start',(i,),label="'X' in square %i"%i)
    for j in range(2,3):
        if (i != j):
            g.add_node((i,j))
            g.add_edge((i,),(i,j),label="'Y' in square %i"%j)
            for k in range(1,10):
                if (k != i and k !=j):
                    g.add_node((i,j,k))
                    g.add_edge((i, j),(i,j,k),label="'X' in square %i"%k)
                    for l in range(9,10):
                        if (l != i and l !=j and l !=k):
                            g.add_node((i,j,k,l))
                            g.add_edge((i, j, k),(i, j, k, l),label="'Y' in square %i"%l)
                            for m in range(1,10):
                                if (m != i and m !=j and m !=k and m != l):
                                    if ((i == 1 and k == 4 and m ==7) or
                                        (i == 4 and k == 5 and m ==6) or
                                        (i == 3 and k == 5 and m ==7)):
                                        g.add_node((i,j,k,l,m), style = 'filled', fillcolor='green')
                                    else:
                                        g.add_node((i,j,k,l,m))
                                    g.add_edge((i, j, k, l), (i, j, k, l, m),label="'X' in square %i"%m)
            
g.set_display_mode('xdot')
g.display()
