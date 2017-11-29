import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class dd_dict(dict):    # the dd is for "deferred delete"
    _deletes = None
    def __delitem__(self, key):
        if key not in self:
            raise KeyError(str(key))
        dict.__delitem__(self, key) if self._deletes is None else self._deletes.add(key)
    def __enter__(self):
        self._deletes = set()
    def __exit__(self, type, value, tb):
        for key in self._deletes:
            try:
                dict.__delitem__(self, key)
            except KeyError:
                pass
        self._deletes = None

#| common class ordering of ring systems for 5,6 rings
common5rings = [("C2'", "C3'", "C4'", "O4'", "C1'"), ("C2R", "C3R", "C4R", "O4R", "C1R")]
common6rings = [("C3'", "C4'", "C5'", "O5'", "C1'", "C2'"), ("C3A", "C4A", "C5A", "O5A", "C1A", "C2A"),
                ("C3", "C4", "C5", "O5", "C1", "C2")]
commonrings = common5rings + common6rings


def getcommonring(ring):
    """
    Common atom naming systems for rings, this routine is used to automagically reorder guesses for
    rings s.t. that they provide the expected results...
    """
    thiscycle = {}
    if len(ring) == 5:
        import re
        for atom in ring:  # note this is for a five ring...
            if (atom.startswith('C1') or atom.endswith('C1')) and ('1' in re.findall(r'\d+',atom)): # make sure not matching C13
                thiscycle['C1'] = atom
            elif (atom.startswith('C2') or atom.endswith('C2')) and ('2' in re.findall(r'\d+',atom)): # make sure not matching C23
                thiscycle['C2'] = atom
            elif (atom.startswith('C3') or atom.endswith('C3')) and ('3' in re.findall(r'\d+',atom)): # make sure not matching C33
                thiscycle['C3'] = atom
            elif (atom.startswith('C4') or atom.endswith('C4')) and ('4' in re.findall(r'\d+',atom)): # make sure not matching C44
                thiscycle['C4'] = atom
            elif atom.startswith('O') or atom.endswith('O'):
                thiscycle['O4'] = atom
            else:
                # there is an atom that is not common. So cannot apply this ordering trick.
                return None
        try:
            return (thiscycle['C2'], thiscycle['C3'], thiscycle['C4'], thiscycle['O4'], thiscycle['C1'])
        except:
            return None
    elif len(ring) == 6:
        import re
        for atom in ring:  # note this is for a six ring...
            if (atom.startswith('C1') or atom.endswith('C1')) and ('1' in re.findall(r'\d+',atom)): # make sure not matching C13
                thiscycle['C1'] = atom
            elif (atom.startswith('C2') or atom.endswith('C2')) and ('2' in re.findall(r'\d+',atom)):
                thiscycle['C2'] = atom
            elif (atom.startswith('C3') or atom.endswith('C3')) and ('3' in re.findall(r'\d+',atom)):
                thiscycle['C3'] = atom
            elif (atom.startswith('C4') or atom.endswith('C4')) and ('4' in re.findall(r'\d+',atom)):
                thiscycle['C4'] = atom
            elif (atom.startswith('C5') or atom.endswith('C5')) and ('5' in re.findall(r'\d+',atom)):
                thiscycle['C5'] = atom
            elif atom.startswith('O') or atom.endswith('O'):
                thiscycle['O5'] = atom
            else:
                # what about C10 O9 C14 C13 C12 C11 - should reverse to C11 C12 C13 C14 O9 C10
                # if 10>9 and 10<11 and 11 < 12 then reverse
#                import copy
#                allatoms = " ".join(ring)
#                intsinatoms=re.findall(r'\d+',allatoms)
#                logger.debug("ORDERING %s %s", ring, intsinatoms)
#                if int(intsinatoms[0])> int(intsinatoms[1]) and int(intsinatoms[0])<int(intsinatoms[5]) and int(intsinatoms[5])< int(intsinatoms[4]):
#                    localcopyofring=copy.deepcopy(ring)
#                    #popped=localcopyofring.pop()
#                    #localcopyofring.insert(0,popped)
#                    localcopyofring.reverse()
#                    logger.debug("REVERSE %s", localcopyofring)
#                    return localcopyofring

                #. get O into position 3 (0,1,2,3)
                #. Get O to position 3, then check numbering 4<0
                #!. this depends on atom numbering. If C1 is numbered higher than C4 then the non-contextualised conformer will seem incorrect
                indices = []
                for i, elem in enumerate(ring):
                    if 'O' in elem:
                        indices.append(i)
                if len(indices) == 1:
                    opos=indices[0]
                    if opos==3:
                        return ring
                    pos=opos
                    while pos!=3:
                       popped=ring.pop()
                       ring.insert(0,popped)
                       indices=[]
                       for i, elem in enumerate(ring):
                           if 'O' in elem:
                               indices.append(i)
                       pos=indices[0]
                    logger.debug("POPPEDTOPOS4 %s", ring)
                    try:
                        if int(re.findall(r'\d+',ring[4])[0]) < int(re.findall(r'\d+',ring[0])[0]) :
                            logger.debug("RETURN4 %s", ring)
                            return ring
                        else:
                            popped=ring.pop()
                            ring.insert(0,popped)
                            logger.debug("POPPEDAGAIN %s", ring)
                            return ring
                    except:
                        return None
                else:
                    return None
        try:
            return (
                thiscycle['C3'], thiscycle['C4'], thiscycle['C5'], thiscycle['O5'], thiscycle['C1'], thiscycle['C2'])
        except:
            return None
    else:
        return None


def getring(startatom, atomset):
    """getRing(startatom, atomset, lookup, oatoms)->atoms, bonds
    starting at startatom do a bfs traversal through the atoms
    in atomset and return the smallest ring found

    returns (), () on failure
    note: atoms and bonds are not returned in traversal order"""

    path = {}
    bpaths = {}
    for atomID in atomset.keys():
        # initially the paths are empty
        path[atomID] = []
        bpaths[atomID] = []
    #... insert from Figueras paper
    # The BFS algorithm. We wish to find the smallest ring in the molecule that includes startatom
    # we assign paths , path[i] to each node i. The path conrinas the nodes in the path from the starting node to node i
    # initialise all the paths to null
    # assign values to paths in the starting node
    #for subnodes in atomset[startatom]:
    #   path[subnodes]=[startatom,subnodes]
    # now check if subnodes subnodes is empty

    # but actually will start at starting node but do all nodes...
    q = []
    # Initialize the queue with nodes attached to rootNode
    # and initialise these paths

    for subnodes in atomset[startatom]:
        q.append([startatom, subnodes])
        path[subnodes] = [startatom, subnodes]
    logger.debug("getRING q nodes %s",q)
    logger.debug("getRING path nodes %s",path)
    # loop while the queue size is greater than zero (it exists)
    while q:
        root, node = q.pop()
        for subnodes in atomset[node]:
            logger.debug("getRING subnodes %s in set %s, root is %s", subnodes, atomset[node], root)
            if subnodes != root:  # node shouldn't be start atom but check...
                # check if path is empty or not
                if not path[subnodes]:  # if empty assign path as root path + subnodes
                    path[subnodes] = path[node] + [subnodes]
                    logger.debug("getRING had no paths now path %s from node %s paths %s and itself %s", path[subnodes], node, path[node],[subnodes])
                    q.append([node, subnodes])
                else:  # possible ring closure
                    # compute the intersection of path[root], path[subnodes], it must be a singleton i.e. one element
                    intersection = set(path[node]) & set(path[subnodes])
                    logger.debug("getRING intersection %s", intersection)
                    #print "INTERSECTION ", set(path[node])&set(path[subnodes]), len(intersection)
                    if len(intersection) == int(1):
                        logger.debug("getRING use intersection %s is size %i", intersection, len(intersection))
                        #union
                        union = set(path[node]) | set(path[subnodes])
                        logger.debug("getRING union %s", union)

                        avail = sorted(list(union))  # sort here to prevent dupl
                        logger.debug("getRING avail union %s", avail)
                        chosen = []
                        if len(union) < 5 or len(union)> 400: # it is pointless considering
                            return ()
                        while avail:
                            if not chosen:
                                chosen.append(avail[0])
                                del avail[0]
                            else:
                                lastadded = chosen[-1]
                                for children in atomset[lastadded]:
                                    if children not in chosen and children in avail:  # child must not be used and must be part of the atoms in the ring
                                        chosen.append(children)
                                        del avail[avail.index(children)]
                                        break
                        return chosen
                    else:  # ignore path
                        logger.debug("getRING pass on intersection %s is size %i", intersection, len(intersection))
                        pass
            else:
                logger.debug("subnode=root %s %s", subnodes, root)
    logger.debug("returning nothing")
    return ()  # for subnodes in atomSet[startAtom]:


def min_degree(edges):
    """getRing(edges)
    loop through all edges and calculate the min degree of the current nodes in the graph
    returns an int min_degree
    This is this literally the lowest available degree. A graph with 1,2 and 3 degree nodes has a mindegree of 1"""
    min_atom, min_degree = None, int(10000)
    # loop over edges
    for atom in edges:
        if len(edges[atom]) < min_degree:
            min_atom = atom
            min_degree = len(edges[atom])
    return min_atom, min_degree

def create_graph_and_find_rings_suite(atomlist, mineuclid=1.1, maxeuclid=2.0):
    """ find possible rings """
    try:
#        import getRing
        import tessellate.utils.getRing as getRing
    except Exception as e:
       print("Error - Cannot import module ", e)
       exit(1)
    SSSR=[]
    SSSR1=getRing.create_graph_and_find_rings_d3069(atomlist,mineuclid,maxeuclid) 
    SSSR2=getRing.create_graph_and_find_rings_6abb(atomlist,mineuclid,maxeuclid)
    SSSR.extend(SSSR1)
    for itm in SSSR2:
        if itm not in SSSR:
            SSSR.extend([itm])
    return SSSR

def make_unique(original_list):
    unique_list = []
    map(lambda x: unique_list.append(x) if (x not in unique_list) else False, original_list)
    return unique_list

def create_graph_and_find_rings_d3069(atomlist, mineuclid=1.1, maxeuclid=2.0):
    """
    :type atomlist: list
    :type mineuclid: float
    :type maxeuclid: float
    :rtype : list
    """
    try:
        #import getRing
        import tessellate.utils.getRing as getRing
        import itertools
        import numpy as np
    except Exception as e:
        print("Error - Cannot import module ", e)
        exit(1)
    SSSR = [] # keep track of all the rings
    edges = {}
    for a, b in itertools.combinations(atomlist, 2):
        # work out euclidean distance and choose to call this an edge if mineuclid<dist<maxeuclid
        dist = np.linalg.norm(a[1] - b[1])
        if maxeuclid > dist > mineuclid:
            try:
                edges[a[0]].append(b[0])
            except:
                edges[a[0]] = [b[0]]
            try:
                edges[b[0]].append(a[0])
            except:
                edges[b[0]] = [a[0]]

    # debug print out the edges
    for atom in edges:
        logger.debug('Atom edges info %s %s %s', atom, edges[atom], len(edges[atom]))
    # Now recursively remove all terminal nodes i.e.with only one edge
    alledges = dict(edges)
    deletededges = {}
    #logger.debug("allededges dict %s",alledges)
    #logger.debug("edges %s",edges)
    if edges != []:
        while edges:
            for atom in dict(edges).keys():
                N2nodes = []
                N3nodes = []
                logger.debug("all edge keys %s",edges.keys())
                logger.debug("Current edge %s",atom)
                if atom in deletededges.keys():
                    logger.critical("revisiting a deleted edge")
                    exit(1)
                if int(len(edges[atom])) == int(0):  # trim degree zero nodes
                    logger.debug("Zero edge node deleted %s",atom)
                    deletededges[atom]=edges[atom]
                    del edges[atom]  # cannot delete dictionary while iterating use a while
                elif int(len(edges[atom])) == int(1):  # trim degree one nodes
                    # pop it from other atoms
                    logger.debug("One edge node %s with %i edges %s removed from parent node edges list %s",atom, len(edges[atom]),edges[atom],edges[edges[atom][0]])
                    edges[edges[atom][0]].remove(atom)
                    edges[atom] = []
                    deletededges[atom]=edges[atom]
                    del edges[atom]  # cannot delete dictionary while iterating use a while
                elif int(len(edges[atom])) == int(2):  # find nodes of degree 2 and add to N2 nodes
                    logger.debug("Two edge node %s with %i edges",atom, len(edges[atom]))
                    N2nodes.append(atom)
                elif int(len(edges[atom])) == int(3):  # find nodes of degree 2 and add to N3 nodes
                    logger.debug("Three edge node %s with %i edges",atom, len(edges[atom]))
                    N3nodes.append(atom)

                if getRing.min_degree(edges)[1] == int(2) and N2nodes:  # the minimum degree of the entire graph
                    logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
                    for N2 in N2nodes:
                        ring = getRing.getring(N2, alledges)  # give this ring the entire graph
                        logger.debug("ring from getring %s", ring)
                        if len(ring) > 0:
                            if ring in SSSR:  # if exists then ignore, not sorting as a unique ring is being offered by getRing
                                logger.debug("ring already in SSSR %s %i %s", ring, len(ring),type(ring))
                                pass
                            else:
                                SSSR.append(ring)
                        else:
                            pass
                        try: # try isolate and eliminate one N2 node
                            logger.debug("isolate N2 node %s with %i edges and break one bond ", N2, len(edges[N2]) )
                            bondtobreak=edges[N2].pop()
                            logger.debug("break %s with current edges %s ", bondtobreak, edges[bondtobreak] )
                            edges[bondtobreak].remove(N2)
                        except:
                            logger.debug("N2 not eliminated")
                            pass

                elif getRing.min_degree(edges)[1] == int(3) and N3nodes:  # the minimum degree of the entire graph
                    logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
                    logger.debug("N3 d3069")
                    for N3 in N3nodes:
                        ring = getRing.getring(N3, alledges)  # give this ring the entire graph
                        logger.debug("ring from getring %s", ring)
                        if len(ring) > 0:
                            if ring in SSSR:  # if exists then ignore, not sorting as a unique ring is being offered by getRing
                                logger.debug("ring already in SSSR %s %i %s", ring, len(ring),type(ring))
                                pass
                            else:
                                SSSR.append(ring)
                        else:
                            pass
                        try: # try isolate and eliminate one N3 node
                            logger.debug("isolate N3 node %s with %i edges and break one bond ", N3, len(edges[N3]) )
                            bondtobreak=edges[N3].pop()
                            logger.debug("break %s with current edges %s ", bondtobreak, edges[bondtobreak] )
                            edges[bondtobreak].remove(N3)
                        except Exception as e:
                            logger.error(e)
                            print(e)


#    if edges != []:
#        while edges:
#            #currentkeyset=list(edges.keys())
#            for atom in list(edges.keys()):
#                N2nodes = []
#                N3nodes = []
#                logger.debug("all edge keys %s",edges.keys())
#                logger.debug("deleted edge keys %s",deletededges.keys())
#                logger.debug("Current edge %s",atom)
#                if atom in deletededges.keys():
#                    logger.critical("revisiting a deleted edge")
#                    exit(1)
#                if int(len(edges[atom])) == int(0):  # trim degree zero nodes
#                    logger.debug("Zero edge node deleted %s",atom)
#                    deletededges[atom]=edges[atom]
#                    del edges[atom]  # cannot delete dictionary while iterating use a while
#                    continue
#                elif int(len(edges[atom])) == int(1):  # trim degree one nodes
#                    # pop it from other atoms
#                    logger.debug("One edge node %s with %i edges %s removed from parent node edges list %s",atom, len(edges[atom]),edges[atom],edges[edges[atom][0]])
#                    edges[edges[atom][0]].remove(atom)
#                    edges[atom] = []
#                    deletededges[atom]=edges[atom]
#                    del edges[atom]  # cannot delete dictionary while iterating use a while
#                    continue
#                elif int(len(edges[atom])) == int(2):  # find nodes of degree 2 and add to N2 nodes
#                    logger.debug("Two edge node %s with %i edges",atom, len(edges[atom]))
#                    N2nodes.append(atom)
#                elif int(len(edges[atom])) == int(3):  # find nodes of degree 2 and add to N3 nodes
#                    logger.debug("Three edge node %s with %i edges",atom, len(edges[atom]))
#                    N3nodes.append(atom)
#
#                if getRing.min_degree(edges)[1] == int(2) and N2nodes:  # the minimum degree of the entire graph
#                    logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
#                    for N2 in N2nodes:
#                        ring = getRing.getring(N2, alledges)  # give this ring the entire graph
#                        logger.debug("ring from getring %s", ring)
#                        if len(ring) > 0:
#                            if ring in SSSR:  # if exists then ignore, not sorting as a unique ring is being offered by getRing
#                                logger.debug("ring already in SSSR %s %i %s", ring, len(ring),type(ring))
#                                pass
#                            else:
#                                SSSR.append(ring)
#                        else:
#                            pass
#                        try: # try isolate and eliminate one N2 node
#                            logger.debug("isolate N2 node %s with %i edges and break one bond ", N2, len(edges[N2]) )
#                            bondtobreak=edges[N2].pop()
#                            logger.debug("break %s with current edges %s ", bondtobreak, edges[bondtobreak] )
#                            edges[bondtobreak].remove(N2)
#                        except:
#                            logger.debug("N2 not eliminated")
#                            pass
#
#                elif getRing.min_degree(edges)[1] == int(3) and N3nodes:  # the minimum degree of the entire graph
#                    logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
#                    logger.debug("N3 d3069")
#                    for N3 in N3nodes:
#                        ring = getRing.getring(N3, alledges)  # give this ring the entire graph
#                        logger.debug("ring from getring %s", ring)
#                        if len(ring) > 0:
#                            if ring in SSSR:  # if exists then ignore, not sorting as a unique ring is being offered by getRing
#                                logger.debug("ring already in SSSR %s %i %s", ring, len(ring),type(ring))
#                                pass
#                            else:
#                                SSSR.append(ring)
#                        else:
#                            pass
#                        try: # try isolate and eliminate one N3 node
#                            logger.debug("isolate N3 node %s with %i edges and break one bond ", N3, len(edges[N3]) )
#                            bondtobreak=edges[N3].pop()
#                            logger.debug("break %s with current edges %s ", bondtobreak, edges[bondtobreak] )
#                            edges[bondtobreak].remove(N3)
#                        except Exception as e:
#                            logger.error(e)
#                            print(e)
    if SSSR:
        logger.debug("SSSR %s", SSSR)
    return SSSR



def create_graph_and_find_rings_old(atomlist, mineuclid=1.1, maxeuclid=2.0):
    """
    :type atomlist: list
    :type mineuclid: float
    :type maxeuclid: float
    :rtype : list
    """
    try:
        # import getRing
        import tessellate.utils.getRing as getRing
        import itertools
        import numpy as np
    except Exception as e:
        print("Error - Cannot import module ", e)
        exit(1)
    SSSR = [] # keep track of all the rings
    edges = {}
    for a, b in itertools.combinations(atomlist, 2):
        # work out euclidean distance and choose to call this an edge if mineuclid<dist<maxeuclid
        dist = np.linalg.norm(a[1] - b[1])
        if maxeuclid > dist > mineuclid:
            try:
                edges[a[0]].append(b[0])
            except:
                edges[a[0]] = [b[0]]
            try:
                edges[b[0]].append(a[0])
            except:
                edges[b[0]] = [a[0]]

    for atom in edges:
        logger.debug('Atom edges info %s %s %s', atom, edges[atom], len(edges[atom]))
    # Now recursively remove all terminal nodes i.e.with only one edge
    alledges = dict(edges)
    if edges != []:
        while edges:
            for atom in dict(edges).keys():
                N2nodes = []
                logger.debug("all edge keys %s",edges.keys())
                logger.debug("Current edge %s",atom)
                if int(len(edges[atom])) == int(0):  # trim degree zero nodes
                    logger.debug("Zero edge node deleted %s",atom)
                    del edges[atom]  # cannot delete dictionary while iterating use a while
                elif int(len(edges[atom])) == int(1):  # trim degree one nodes
                    # pop it from other atoms
                    logger.debug("One edge node %s with %i edges %s removed from parent node edges list %s",atom, len(edges[atom]),edges[atom],edges[edges[atom][0]])
                    edges[edges[atom][0]].remove(atom)
                    edges[atom] = []
                    del edges[atom]  # cannot delete dictionary while iterating use a while
                elif int(len(edges[atom])) == int(2):  # find nodes of degree 2 and add to N2 nodes
                    logger.debug("Two edge node %s with %i edges",atom, len(edges[atom]))
                    N2nodes.append(atom)
                if getRing.min_degree(edges)[1] == int(2):  # the minimum degree of the entire graph
                    logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
                    for N2 in N2nodes:
                        ring = getRing.getring(N2, alledges)  # give this ring the entire graph
                        logger.debug("ring from getring %s", ring)
                        if len(ring) > 0:
                            if ring in SSSR:  # if exists then ignore, not sorting as a unique ring is being offered by getRing
                                logger.debug("ring already in SSSR %s %i %s", ring, len(ring),type(ring))
                                pass
                            else:
                                SSSR.append(ring)
                        else:
                            pass
                        try: # try isolate and eliminate one N2 node
                            logger.debug("isolate N2 node %s with %i edges and break one bond ", N2, len(edges[N2]) )
                            bondtobreak=edges[N2].pop()
                            logger.debug("break %s with current edges %s ", bondtobreak, edges[bondtobreak] )
                            edges[bondtobreak].remove(N2)
                        except:
                            logger.debug("Couldn't eliminate N2")
                            pass

                elif getRing.min_degree(edges)[1] == int(3):  # the minimum degree of the entire graph
                    logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
                    ring = getRing.getring(atom, alledges)
                    logger.debug("ring from getring %s", ring)
                    if len(ring) > 0:
                        if ring in SSSR:
                            pass
                        else:
                            SSSR.append(ring)
                    else:
                        pass
                    try: # select an optimum edge for elimination. trial each edge in alledges
                        logger.error("FUTURETODO - N3 check edges not yet implemented only applicable to cages etc." )
                        exit(1)
                    except:
                        pass
    if SSSR:
        logger.debug("SSSR %s", SSSR)
    return SSSR

def create_graph_and_find_rings_6abb(atomlist, mineuclid=1.1, maxeuclid=2.0):
    """
    :type atomlist: list
    :type mineuclid: float
    :type maxeuclid: float
    :rtype : list
    """
    try:
        # import getRing
        import tessellate.utils.getRing as getRing
        import itertools
        import numpy as np
    except Exception as e:
        print("Error - Cannot import module ", e)
        exit(1)
    SSSR = [] # keep track of all the rings
    edges = {}
    for a, b in itertools.combinations(atomlist, 2):
        # work out euclidean distance and choose to call this an edge if mineuclid<dist<maxeuclid
        dist = np.linalg.norm(a[1] - b[1])
        if maxeuclid > dist > mineuclid:
            #edges.append([a,b]) # this works but is difficult to remove edges later
            try:
                edges[a[0]].append(b[0])
            except:
                edges[a[0]] = [b[0]]
            try:
                edges[b[0]].append(a[0])
            except:
                edges[b[0]] = [a[0]]

    for atom in edges:
        logger.debug('Atom edges info %s %s %s', atom, edges[atom], len(edges[atom]))
    # Now recursively remove all terminal nodes i.e.with only one edge
    alledges = dict(edges)
    deletededges = {}
    if edges != []:
        while edges:
            N2nodes = []
            N3nodes = []
            for atom in dict(edges).keys():
                logger.debug("all edge keys %s",edges.keys())
                logger.debug("Current edge %s",atom)
                if atom in deletededges.keys():
                    logger.critical("revisiting a deleted edge")
                    exit(1)

                if int(len(edges[atom])) == int(0):  # trim degree zero nodes
                    logger.debug("Zero edge node deleted %s",atom)
                    deletededges[atom]=edges[atom]
                    del edges[atom]  # cannot delete dictionary while iterating use a while
                elif int(len(edges[atom])) == int(1):  # trim degree one nodes
                    # pop it from other atoms
                    logger.debug("One edge node %s with %i edges %s removed from parent node edges list %s",atom, len(edges[atom]),edges[atom],edges[edges[atom][0]])
                    edges[edges[atom][0]].remove(atom)
                    edges[atom] = []
                    deletededges[atom]=edges[atom]
                    #logger.critical("Deleting atom %s %s",atom, deletededges)
                    del edges[atom]  # cannot delete dictionary while iterating use a while
                elif int(len(edges[atom])) == int(2):  # find nodes of degree 2 and add to N2 nodes
                    logger.debug("Two edge node %s with %i edges",atom, len(edges[atom]))
                    N2nodes.append(atom)
                elif int(len(edges[atom])) == int(3):  # find nodes of degree 2 and add to N3 nodes
                    logger.debug("Three edge node %s with %i edges",atom, len(edges[atom]))
                    N3nodes.append(atom)

            if getRing.min_degree(edges)[1] == int(2) and N2nodes:  # the minimum degree of the entire graph
                logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
                for N2 in N2nodes:
                    ring = getRing.getring(N2, alledges)  # give this ring the entire graph
                    logger.debug("ring from getring %s", ring)
                    if len(ring) > 0:
                        if ring in SSSR:  # if exists then ignore, not sorting as a unique ring is being offered by getRing
                            logger.debug("ring already in SSSR %s %i %s", ring, len(ring),type(ring))
                        else:
                            SSSR.append(ring)
                logger.debug("isolate N2 node %s with %i edges and break one bond ", N2nodes[0], len(edges[N2nodes[0]]) )
                bondtobreak=edges[N2nodes[0]].pop(0)
                logger.debug("break %s with current edges %s ", bondtobreak, edges[bondtobreak] )
                edges[bondtobreak].remove(N2nodes[0])

            elif getRing.min_degree(edges)[1] == int(3) and N3nodes:  # the minimum degree of the entire graph
                logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
                logger.debug("N3 6abb")
                for N3 in N3nodes:
                    ring = getRing.getring(N3, alledges)  # give this ring the entire graph
                    logger.debug("ring from getring %s", ring)
                    if len(ring) > 0:
                        if ring in SSSR:  # if exists then ignore, not sorting as a unique ring is being offered by getRing
                            logger.debug("ring already in SSSR %s %i %s", ring, len(ring),type(ring))
                            pass
                        else:
                            SSSR.append(ring)
                    else:
                        pass
                    try: # try isolate and eliminate one N3 node
                        logger.debug("isolate N3 node %s with %i edges and break one bond ", N3, len(edges[N3]) )
                        bondtobreak=edges[N3].pop()
                        logger.debug("break %s with current edges %s ", bondtobreak, edges[bondtobreak] )
                        edges[bondtobreak].remove(N3)
                    except Exception as e:
                        logger.error(e)
                        print(e)

#    if edges != []:
#        while edges:
#            N2nodes = []
#            N3nodes = []
#            #for atom in dict(edges).keys():
#            for atom in list(edges.keys()):
#                logger.debug("all edge keys %s",edges.keys())
#                logger.debug("deleted edge keys %s",deletededges.keys())
#                logger.debug("Current edge %s",atom)
#                if atom in deletededges.keys():
#                    logger.critical("revisiting a deleted edge")
#                    exit(1)
#
#                if int(len(edges[atom])) == int(0):  # trim degree zero nodes
#                    logger.debug("Zero edge node deleted %s",atom)
#                    deletededges[atom]=edges[atom]
#                    del edges[atom]  # cannot delete dictionary while iterating use a while
#                elif int(len(edges[atom])) == int(1):  # trim degree one nodes
#                    # pop it from other atoms
#                    logger.debug("One edge node %s with %i edges %s removed from parent node edges list %s",atom, len(edges[atom]),edges[atom],edges[edges[atom][0]])
#                    edges[edges[atom][0]].remove(atom)
#                    edges[atom] = []
#                    deletededges[atom]=edges[atom]
#                    #logger.critical("Deleting atom %s %s",atom, deletededges)
#                    del edges[atom]  # cannot delete dictionary while iterating use a while
#                elif int(len(edges[atom])) == int(2):  # find nodes of degree 2 and add to N2 nodes
#                    logger.debug("Two edge node %s with %i edges",atom, len(edges[atom]))
#                    N2nodes.append(atom)
#                elif int(len(edges[atom])) == int(3):  # find nodes of degree 2 and add to N3 nodes
#                    logger.debug("Three edge node %s with %i edges",atom, len(edges[atom]))
#                    N3nodes.append(atom)
#
#            if getRing.min_degree(edges)[1] == int(2) and N2nodes:  # the minimum degree of the entire graph
#                logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
#                for N2 in N2nodes:
#                    ring = getRing.getring(N2, alledges)  # give this ring the entire graph
#                    logger.debug("ring from getring %s", ring)
#                    if len(ring) > 0:
#                        if ring in SSSR:  # if exists then ignore, not sorting as a unique ring is being offered by getRing
#                            logger.debug("ring already in SSSR %s %i %s", ring, len(ring),type(ring))
#                        else:
#                            SSSR.append(ring)
#                logger.debug("isolate N2 node %s with %i edges and break one bond ", N2nodes[0], len(edges[N2nodes[0]]) )
#                bondtobreak=edges[N2nodes[0]].pop(0)
#                logger.debug("break %s with current edges %s ", bondtobreak, edges[bondtobreak] )
#                edges[bondtobreak].remove(N2nodes[0])
#
#            elif getRing.min_degree(edges)[1] == int(3) and N3nodes:  # the minimum degree of the entire graph
#                logger.debug("current min degree %i", getRing.min_degree(edges)[1] )
#                logger.debug("N3 6abb")
#                for N3 in N3nodes:
#                    ring = getRing.getring(N3, alledges)  # give this ring the entire graph
#                    logger.debug("ring from getring %s", ring)
#                    if len(ring) > 0:
#                        if ring in SSSR:  # if exists then ignore, not sorting as a unique ring is being offered by getRing
#                            logger.debug("ring already in SSSR %s %i %s", ring, len(ring),type(ring))
#                            pass
#                        else:
#                            SSSR.append(ring)
#                    else:
#                        pass
#                    try: # try isolate and eliminate one N3 node
#                        logger.debug("isolate N3 node %s with %i edges and break one bond ", N3, len(edges[N3]) )
#                        bondtobreak=edges[N3].pop()
#                        logger.debug("break %s with current edges %s ", bondtobreak, edges[bondtobreak] )
#                        edges[bondtobreak].remove(N3)
#                    except Exception as e:
#                        logger.error(e)
#                        print(e)
    if SSSR:
        logger.debug("SSSR %s", SSSR)
    return SSSR
