import numpy as np
from scipy.sparse import dia_matrix, triu, lil_matrix, coo_matrix
import networkx as nx
import gzip
import inspect

import iterativeCorrection

debug = 1


def flattenList(alist):
    """
    given a list of list of list, returns a list
    For example: given [1,[[2]], [3,4]]
    returns [1, 2, 3 4]
    This is a recursive function
    """
    ret = []
    for values in alist:
        if type(values) == int:
            ret.append(values)
        else:
            ret.extend(flattenList(values))
    return ret


class hicAssembler:
    def __init__(self, hic_matrix, PE_scaffolds_file, overlap_graph_file):
        # the scaffolds list contains PE_scaffolds ids.
        # but for simplicity I refer to the initial PE_scaffolds
        # as contigs.

        # The list is modified with each iteration replacing its members
        # by lists. After two iterations a scaffold
        # list could look like: [[0],[1,2,3]]
        # which means that there are two scaffolds
        # one of those is composed of the contigs 1, 2 and 3

        # the list if initialized with the ids as the matrix row numbers
        self.scaffolds = []
        self.id2label = dict()
        self.hic = hic_matrix
        # the original matrix is going to be modified
        # for this reason a copy is created
        self.matrix = hic_matrix.matrix.copy()


        self.merge_PE_scaffolds(PE_scaffolds_file)

        # reads overlap file from SGA
        #self.overlap_graph = self.get_overlap_graph(overlap_graph_file)

        # read labels
        print "[{}] initial N50: {} ".format(
            inspect.stack()[0][3], self.compute_N50())

        self.maskUnreliableRows()

        self.initial_matrix = self.matrix.copy()

        self.matrix = \
            iterativeCorrection.iterativeCorrection(self.matrix, M=1000)[0]

        self.iterateGetContigsReduce()

        # now merge the right sides of the contigs
        self.final_scaffolds = []
        while(self.scaffolds):
            self.final_scaffolds.append(
                self.arrange_and_merge(self.scaffolds.pop(0)))

        self.PE_final = []
        for scaf in self.final_scaffolds:
            # translate each scaffold to the original PE_ scaffolds
            self.PE_final.append([self.PE_kept[x] for x in scaf])

    def merge_PE_scaffolds(self, PE_scaffolds_file):
        """
        Reads the PE_scaffolds file, reduces
        the matrix according to the scaffolds
        and sets the scaffold ids
        """
        # read the file that contains information
        # to join contigs into scaffolds
        self.PE_scaffolds = self.read_PE_scaffolds(PE_scaffolds_file)

        # join all known PE scaffolds
        self.reduce_matrix(self.PE_scaffolds, update_scaffolds=False)


    def iterateGetContigsReduce(self, n=2):
        self.iteration = -1
        for iter_num in range(n):
            self.iteration += 1

            if self.matrix.shape[0] == 1:
                print "[{}] iteration: {}".format(inspect.stack()[0][3],
                                                  iter_num)
                break
            super_contig, net = self.get_super_contigs()
            # stop iterating if there is no improvement
            if sum([len(x) - 1 for x in super_contig]) < 1:
                break

            allnodes = []
            for cont_sequence in super_contig:
                allnodes.extend(cont_sequence)
            print "[{}] len nodes {}, max {}".format(inspect.stack()[0][3],
                                                     len(allnodes),
                                                     max(allnodes))

            self.reduce_matrix(super_contig)

            if self.matrix.shape[0] < 2:
                print "[{}] matrix shape reached 2 finishing " \
                    "after {} iterations ".format(
                    inspect.stack()[0][3], self.matrix.shape)
                print iter_num
                break

            # normalize matrix
            self.matrix = \
                iterativeCorrection.iterativeCorrection(self.matrix, M=100)[0]

            #####
            # convert the net to graph to save
            # and read using cytoscape
            np.savez(
                '/home/ramirez/tmp/mat_{}'.format(iter_num), mat=self.matrix,
                con=super_contig)
            GG = nx.from_scipy_sparse_matrix(net)
            nx.write_edgelist(GG, '/home/ramirez/tmp/g_{}.txt'.format(iter_num))
            fh = open('/home/ramirez/tmp/g_attr_{}.txt'.format(iter_num), 'w')
            for k, v in self.id2label.iteritems():
                fh.write("{}\t{}\n".format(k, v))
            fh.close()
            ##### end writting for debugging

    def maskUnreliableRows(self):
        """
        identifies rows that are too small or that have very
        few interactions. Those rows will be
        excluded from any computation.
        """
        label, length = zip(*self.bin_info)
        small_list = np.flatnonzero(np.array(length) < 200)
        ma_sum = np.asarray(self.matrix.sum(axis=1)).flatten()
        few_inter = np.flatnonzero(ma_sum < 10)
        self.mask = np.unique(np.hstack([small_list, few_inter]))
        print "[{}] removing {} ({}%) low quality regions from hic matrix " \
            "whose length is smaller than 2000 and have in total less " \
            "than 25 interactions to other contigs ".format(
            inspect.stack()[0][3], len(self.mask), 100* float(len(self.mask))/self.matrix.shape[0])

        # remove rows and cols from matrix
        rows = cols = np.delete(range(self.matrix.shape[1]), self.mask)
        self.matrix = self.matrix[rows, :][:, cols]
        
        # record how to map back to original PE_scaffolds
        self.PE_skipped = [self.PE_scaffolds[x] for x in self.mask]
        self.PE_kept = [self.PE_scaffolds[x] for x in rows]

        # 


        self.bin_info_skipped = [self.bin_info[x] for x in self.mask]
        self.bin_info = [self.bin_info[x] for x in rows]


        # initialize the scaffolds ids as the matrix row numbers
        # each new scaffold id corresponds to  a PE_kept scaffold
        self.scaffolds = range(self.matrix.shape[0])
        self.id2label = dict([(x, label[rows[x]]) for x in range(len(rows))])


    def reduce_matrix(self, super_contigs, update_scaffolds=True):
        """
        This function sums the rows and colums corresponding
        to the super_contigs, returning a new sparse
        matrix of size len(super_contigs).

        The function uses sparse matrices tricks to work very fast.
        The idea is that all the cells in the new reduced matrix
        whose sum needs to be computed are expressed as a vector
        of bins.  Using the bincount function the sum of each bin
        is obtained. Then this sum vector is converted to a
        sparse matrix.


        Parameters
        ----------

        super_contigs : A list of lists. The values of the lists should
            correspond to the indices of the matrix.

        Returns
        -------

        A sparse matrix.

        >>> A = np.array([[12,5,3,2,0],[0,11,4,1,1],
        ... [0,0,9,6,0], [0,0,0,10,0], [0,0,0,0,0]])
        >>> t = superContig(A)
        >>> ll = [(0,2), (1,3), (4,)]
        >>> t.reduce_matrix(ll)
        >>> t.matrix.todense()
        matrix([[ 24.,  17.,   0.],
                [ 17.,  22.,   1.],
                [  0.,   1.,   0.]])
        """

        #use only the upper triangle of the matrix
        # and convert to coo
        ma = triu(self.matrix, k=0, format='coo')
        M = len(super_contigs)

        # place holder for the new row and col
        # vectors
        new_row = np.zeros(len(ma.row), dtype='int')
        new_col = np.zeros(len(ma.col), dtype='int')

        # each original col and row index is converted
        # to a new index based on the super_contigs.
        # For example, if rows 1 and 10 are to be merged
        # then all rows whose value is 1 or 10 are given
        # the as new value the index in the super_contigs list.
        for index in range(M):
            for value in super_contigs[index]:
                new_row[ma.row == value] = index
                new_col[ma.col == value] = index

        # The following line converts each combination
        # of row and col into a list of bins. For example,
        # for each case in which row = 1 and col =3 or
        # row = 3 and col = 1 a unique bin id is given
        # The trick I use to get the unique bin ids is
        # to order and convert the pair (row,col) into
        # a complex number  ( for the pair 3,1 the
        # complex es 1,3j.

        uniq, bin_array = np.unique([np.complex(min(p), max(p))
                                     for p in zip(new_row, new_col)],
                                    return_inverse=True)

        # sum the bins. For each bin, all values associated
        # to the bin members are added. Those values are in
        # the ma.data array.
        sum_array = np.bincount(bin_array, weights=ma.data)
        sum_array = sum_array[sum_array > 0]
        # To reconstruct the new matrix the row and col
        # positions need to be obtained. They correspond
        # to the positions of the unique values in the bin_array.
        uniq, ind = np.unique(bin_array, return_index=True)
        new_row_ = new_row[ind]
        new_col_ = new_col[ind]

        result = coo_matrix((sum_array, (new_row_, new_col_)),
                            shape=(M, M))

        # make result symmetric
        diagmatrix = dia_matrix(([result.diagonal()], [0]),
                                shape=(M, M))
        # diagmatrix*2 to remove the diagonal
        self.matrix = result + result.T - (diagmatrix * 2)

        # update scaffold information
        if update_scaffolds:
            self.merge_scaffolds(super_contigs)

    def merge_scaffolds(self, super_contigs):
        """
        Merges the scaffolds. For the first iteration
        the scaffolds are just a list of ids.
        In the second reduction iteration the
        the scaffolds are a list of a list. For
        the third, a list of a list of a list that
        reflects the subsecuent merging steps

        """
        new_scaf = []
        for ii in range(len(super_contigs)):
            try:
                # translate matrix ids to contig_ids
                new_scaf.append([self.scaffolds[x] for x in super_contigs[ii]])
            except:
                import ipdb; ipdb.set_trace()
        self.scaffolds = new_scaf
        """
        print "[{}] scaffold ids:".format(inspect.stack()[0][3])
        for scaf in self.scaffolds:
            print scaf
        """

        self.super_contigs = super_contigs
         
    def arrange_and_merge(self, scaffolds, problematic=[]):
        """
        given the scaffolds sequence
        tries to join them in a single
        sequence, inverting a sequence
        when necesary.

        For example to merge
        [[6, 5], [7], [8]] correctly
        the first sequence [6, 5] needs to
        be reversed. To decide if a sequence
        needs to be inverted, the flanking
        contigs are used to decide which one
        is closer to the next sequence.
        """

        if len(scaffolds) == 1 and type(scaffolds[0]) == list:
            scaffolds = self.arrange_and_merge(scaffolds[0])

        if all([type(x) == int for x in scaffolds]):
            return scaffolds
        print "[{}] Arranging {} ".format(
            inspect.stack()[0][3],
            scaffolds)
        for index in range(len(scaffolds) - 1):
            if type(scaffolds[index][0]) == list:
                scaffolds[index], prob = \
                    self.arrange_and_merge(scaffolds[index])
                self.scaffolds.append(prob)
            if type(scaffolds[index + 1][0]) == list:
                scaffolds[index + 1], prob = \
                    self.arrange_and_merge(scaffolds[index + 1])
                self.scaffolds.append(prob)
            # 0: end - start
            # 1: end - end
            # 2: start - end
            # 3: start - start
            end_point_vals = [self.initial_matrix[scaffolds[index][-1],
                                                  scaffolds[index + 1][0]],
                              self.initial_matrix[scaffolds[index][-1],
                                                  scaffolds[index + 1][-1]],
                              self.initial_matrix[scaffolds[index][0],
                                                  scaffolds[index + 1][-1]],
                              self.initial_matrix[scaffolds[index][0],
                                                  scaffolds[index + 1][0]],
                              ]
            max_value = max(end_point_vals)
            max_index = end_point_vals.index(max_value)
            if max_index == 1:
                # The following contig (+1) has to be inverted
                scaffolds[index + 1] = scaffolds[index + 1][::-1]
            elif index  == 0:
                # only for the first iteration it is allowed
                # to invert the first contig
                if max_index == 2:
                    # Both super contigs have to be inverted
                    scaffolds[index + 1] = scaffolds[index + 1][::-1]
                    scaffolds[index] = scaffolds[index][::-1]
                elif max_index == 3:
                    # The first super_contig has to be inverted
                    scaffolds[index] = scaffolds[index][::-1]

            if index > 0 and max_index > 1:
                # if max_index > 1 it means that the previous seq
                # has to be inverted to get the right order
                # This is fine for the first iteration but does not
                # make sense for the following ones. Thus
                # a warning is printed and the remaining
                # sequences are not merged
                print "Problem when merging {} and {}. Problem id: {}\n" \
                    "id 2: Need to invert first and second\n" \
                    "id 3: Need to invert first only ".format(
                    scaffolds[index], scaffolds[index + 1],
                    max_index )
                # stop merging at this point
                p_scaf = self.arrange_and_merge(scaffolds[index + 1:])
                print "adding {} as new scaffold".format(p_scaf)
                self.scaffolds.append(p_scaf)
                del(scaffolds[index + 1:])
                break

        final_scaffold = np.hstack(scaffolds).tolist()
        print "[{}] Result {} ".format(
            inspect.stack()[0][3],
            final_scaffold)
        ####### TEST LINES, SHOULD BE REMOVED
        diff = np.diff(final_scaffold)
        if np.any(np.flatnonzero(diff > 1)):
            import ipdb;ipdb.set_trace()
        ####### END TEST LINES
        return final_scaffold

    @staticmethod
    def get_overlap_graph(overlap_file):
        """
        This is based on the SGA format stored
        in files ending with asqg.gz
        It contains, both the sequences and the
        network at the end of the file.
        The network part is recognized
        by the ED prefix.
        """
        print "[{}] reading overlap graph {} ".format(
            inspect.stack()[0][3], overlap_file)

        if overlap_file.endswith(".gz"):
            fh = gzip.open(overlap_file, 'rb')
        else:
            fh = open(overlap_file, 'r')
        G = nx.MultiGraph()

        for line in fh:
            if line.startswith("ED"):
                node_a, node_b, start_a, end_a, len_a, \
                    start_b, end_b, len_b, dir, num = \
                    line.split('\t')[1].split(' ')
                G.add_edge(
                    node_a, node_b,
                    start_a=start_a,
                    start_b=start_b)
        return G

    def read_PE_scaffolds(self, scaffolds_file, format='abyss'):
        """
        this code parses the file that contains
        the information to construct PE_scaffolds
        from contigs.

        This is saved in a .de file
        The format is explained here:
        https://groups.google.com/d/msg/abyss-users/G2BmG4I3YPs/2coOJSo5mNEJ
        and looks like this:

        contig-39 contig-81+,1251,3,469.6 contig-261-,361,3,469.6 ; contig-307-,926,3,469.6
        
        which is translated to:
        contig-39+ -> contig-81+ [d=1251 e=469.6 n=3] 
        contig-39+ -> contig-261- [d=361 e=469.6 n=3] 
        contig-39- -> contig-307+ [d=926 e=469.6 n=3]

        where d is estimated distance, n is number
        of pairs supporting the join and e is the
        error of the distance estimation.

        The semicolon separates the contigs that are merged to the left
        or to the right
        """
        print "[{}] reading scaffolding data based on PE {} ".format(
            inspect.stack()[0][3], scaffolds_file)

        PE_scaffolds = []
        labels, start, end, extra = zip(*self.hic.cut_intervals)
        length = np.array(end) - np.array(start)
        # contig id is its index in the list
        label2id = dict([(labels[x], x) for x in range(len(labels))])
        
        PE_length = []
        for line in scaffolds_file:
            PE_scaf = []
            _temp = []
            left, right = line.strip().split(' ;')
            scaf = left.split(' ')
            # first element of 'left' is 
            # the seed contig that is extended left 
            # and right.
            seed_contig = scaf.pop(0).strip()
            for contig in scaf:
                _temp.append(contig.split(',')[0][:-1])

            _temp.append(seed_contig)
            scaf = right.split(' ')
            for contig in scaf:
                _temp.append(contig.split(',')[0][:-1])
            for contig_id in _temp:
                if contig_id in label2id:
                    PE_scaf.append(label2id[contig_id])
                    del label2id[contig_id]
                elif contig_id.strip() != '':
                    """
                    print "PE scaffold considers contig {} "\
                        "but this contig is not in the hic "\
                        "matrix".format(contig_id)
                    """
            if len(PE_scaf):
                PE_scaffolds.append(PE_scaf)

        # append all ids that were
        # not considered in the scaffolds_file as singletons
        for scaf in label2id.values():
            PE_scaffolds.append([scaf])

        for PE_scaf in PE_scaffolds:
            PE_length.append(sum([length[x] for x in PE_scaf]))
        
        if debug:
            # order the PE_scaffols by contig id
            order = np.argsort([min(x) for x in PE_scaffolds])
            PE_scaffolds = [PE_scaffolds[x] for x in order]

        self.PE_scaffolds = PE_scaffolds
        # create a list of ids that corresponds to the ids of the PE_scaffolds
        self.scaffolds = range(len(PE_scaffolds))
        # create a list of labels for the scaffolds using the id
        labels = ['scaffold_{}'.format(x) for x in self.scaffolds]
        self.id2label = dict([(x, labels[x]) for x in range(len(labels))])
        self.bin_info = zip(labels, PE_length)

        return self.PE_scaffolds

    def get_super_contigs(self):
        """ Thu, 23 May 2013 16:14:51
        The idea is to take the matrix and order it
        such that neighbors are placed next to each other.

        The algorithm is as follows:

        1. identify the cell with  highest number of shared pairs and
        save the pair of rows that corresponds to that cell.
        2. remove that number from the matrix.
        3. Quit if all nodes already have two pairs,
           otherwise repeat.

        In theory, if everything is consistent, at the end of
        the for loop each node should have *only* two
        neighbors. This is rarely the case and some of the nodes
        end up with more than two neighbors. However, a large
        fraction of the nodes only have two neighbors and they
        can be chained one after the other to form a super
        contig.
        """
        # consider only the upper triangle of the
        # matrix and convert it to COO for quick
        # operations
        ma = triu(self.matrix, k=1, format='coo')

        order_index = np.argsort(ma.data)[::-1]
        # neighbors dictionary
        # holds, for each node the list of neighbors
        neighbors = {}

        # using a sparse matrix is much faster
        # than creating a network and populating it
        net = lil_matrix(ma.shape, dtype='float64')
        for index in range(ma.shape[0]):
            neighbors[index] = []
        for index in order_index:
            row = ma.row[index]
            col = ma.col[index]
            if col == row:
                continue
            if len(neighbors[row]) < 2 or len(neighbors[col]) < 2:
                neighbors[row].append(col)
                neighbors[col].append(row)
                net[row, col] = ma.data[index]

        return self.create_super_contigs(net)


    @staticmethod
    def argsort(seq):
        """
        returns the indeces of an ordered python list
        """
        return sorted(range(len(seq)), key=seq.__getitem__)


#    @staticmethod
    def create_super_contigs(self, net):
        """Fri, 24 May 2013 15:19:15 +0200
        Uses networkx to find shortest path
        joining connected -components

        Params:
        ------
        net: a sparse matrix 


        Returns:
        -------

        super_contigs: list of lists. Each list member
        contains the sequence of sequential contigs
        """

        print "create_super_contigs"
        super_contigs = []
        problematic = []
        total = net.shape[0]  # total number of nodes in net. 
        G = nx.from_scipy_sparse_matrix(net)
        net=net.tocoo()
        cen = nx.degree(G)
        # high degree nodes are those with
        # more than two neighbors
        high_deg = [k for k, v in cen.iteritems() if v > 2]
        # for the first iteration, remove all hubs
        if self.iteration == 0:
            for node in high_deg:
                print "removing high degree node\ndegree: {}\n" \
                    "length: {}".format(G.degree(node), self.bin_info[node][1])
                G.remove_node(node)
                problematic.append([node])
            # very stringent criteria
            weight_threshold = np.percentile(net.tocoo().data, 40)
            mask = np.flatnonzero(net.data < weight_threshold)
            G.remove_edges_from(zip(net.row[mask], net.col[mask]))
        else:
            # define an upper level threshold
            # to keep high scoring interactions
            weight_threshold = np.percentile(net.data, 20)
            print "[{}] weight threshold set to {}".format(inspect.stack()[0][3],
                                                           weight_threshold)
            for x in high_deg:
                # for nodes with degree higher than 2, remove
                # all edges, except the edge with the highest
                # value
                if G.degree(x) > 0:  # this check is needed because
                                     # during the edge removal the degree changes.
                                     # Nevertheless, is important to target all
                                     # original nodes with high degree
                    weights, nodes = zip(*[(v['weight'], k)
                                           for k, v in G[x].iteritems()])
                    nodes = list(nodes)
                    max_weight = max(weights)
                    if max_weight > weight_threshold:
                        # remove the neighbor that has
                        # the highest edge weight. This will be kept,
                        # all other will be deleted
                        nodes.pop(weights.index(max_weight))
                    G.remove_edges_from([(x, y) for y in nodes])

        # get connected componets
        conn = nx.connected_components(G)
        for nodes in conn:
            if len(nodes) == 1:
                super_contigs.append(nodes)
                continue
            # get all nodes with degree 1.
            # This should be the nodes at the
            # opposite sides. All other nodes
            # in between should have a degree equal to two
            deg_one = [x for x in nodes if G.degree(x) == 1]
            if len(deg_one) != 2:
                print '[{}] probably the nodes form a closed loop' \
                    'because no opposite sides exist' \
                    '{}'.format(inspect.stack()[0][3], nodes)
                edges, weight = zip(*[((x[0], x[1]), x[2]['weight'])
                                      for x in G.edges(nodes, data=True) ])
                min_index = weight.index(min(weight))

                # remove weakest edge
                G.remove_edge(*edges[min_index])
                deg_one = [x for x in nodes if G.degree(x) == 1]
                if len(deg_one) != 2:
                    print "[{}] problem continues after removing weakest link" \
                        "giving up".format(inspect.stack()[0][3])
                    for node in nodes:
                        problematic.append([node])

            # create a new scaffold by finding the shortest
            # path between the two nodes that have degree one
            super_contigs.append(nx.shortest_path(G, source=deg_one[0],
                                                  target=deg_one[1]))
            if debug and self.iteration == 0:
                diff = np.diff(super_contigs[-1])
                if np.any(np.flatnonzero(diff > 1)):
                    super_contigs_with_weight = []
                    for ii in range(len(super_contigs[-1]) - 1):

                        super_contigs_with_weight.append(
                            (super_contigs[-1][ii],
                             super_contigs[-1][ii + 1],
                             G[super_contigs[-1][ii]][super_contigs[-1][ii + 1]]))
                    import ipdb; ipdb.set_trace()

        for node in problematic:
            super_contigs.append(node)
        # consistency check
        after_total = []
        for x in super_contigs:
            after_total.extend(x)
        
        if total != len(after_total):
            # add missing edges (due to removal)
            # to super_contigs
            import ipdb;ipdb.set_trace()
        return super_contigs, net

    def compute_N50(self):
        labels, length = zip(*self.bin_info)
        length = np.array(length)
        length = length[length>200]
        cumsum = np.cumsum(length)
        for i in range(len(length)):
            if cumsum[i] >= float(cumsum[-1]) / 2:
                break

        return length[i] 
            
            

class scaffold:
    """
    This class is a place holder to keep track of the iterative scaffolding
    """
    def __init__(self):
        pass

