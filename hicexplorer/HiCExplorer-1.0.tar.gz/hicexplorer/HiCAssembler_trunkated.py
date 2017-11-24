import numpy as np
from scipy.sparse import dia_matrix, triu, lil_matrix, coo_matrix
import networkx as nx
import gzip
import inspect

from iterativeCorrection import iterativeCorrection

debug = 1
save_time = 1

MERGE_LENGTH = 2000 # after the first iteration, contigs are merged 
                  # as multiples of this length
MIN_LENGTH = 500  # minimun contig or PE_scaffold length to consider
MIN_TOTAL_INT = 400 # minimun number of HiC pairs per contig to consider
#MAX_INT_PER_LENGTH = 'auto' # maximun number of HiC pairs per length of contig
MAX_INT_PER_LENGTH = 0.1 # maximun number of HiC pairs per length of contig
MIN_COVERAGE = 0.8
METH = 1
TEMP_FOLDER = '/scratch/fidel/tmp/'
ITER = 10
MIN_MATRIX_VALUE = 5
MERGE_LENGTH_GROW = 1.5

SIM = True
if SIM:
    MERGE_LENGTH = 2000 # after the first iteration, contigs are merged 
                      # as multiples of this length
    MIN_LENGTH = 500  # minimun contig or PE_scaffold length to consider
    MIN_TOTAL_INT = 200 # minimun number of HiC pairs per contig to consider
    MAX_INT_PER_LENGTH = 'auto' # maximun number of HiC pairs per length of contig
    #MAX_INT_PER_LENGTH = 1 # maximun number of HiC pairs per length of contig
    MIN_COVERAGE = 0.8
    METH = 1
    TEMP_FOLDER = '/scratch/fidel/tmp/'
    ITER = 40
    MIN_MATRIX_VALUE = 5
    MERGE_LENGTH_GROW = 1.8

PE=False
if PE:
    MERGE_LENGTH = 50 # after the first iteration, contigs are merged 
                      # as multiples of this length
    MIN_LENGTH = 100  # minimun contig or PE_scaffold length to consider
    MIN_TOTAL_INT = 5 # minimun number of HiC pairs per contig to consider
    #MAX_INT_PER_LENGTH = 'auto' # maximun number of HiC pairs per length of contig
    MAX_INT_PER_LENGTH = 1 # maximun number of HiC pairs per length of contig
    MIN_COVERAGE = 0.8
    ITER = 1
    MIN_MATRIX_VALUE = 5
class HiCAssembler:
    def __init__(self, hic_matrix, PE_scaffolds_file, overlap_graph_file):
        # the scaffolds list contains PE_scaffolds ids.
        # but for simplicity I refer to the initial PE_scaffolds
        # as contigs.

        # The list is modified with each iteration replacing its members
        # by lists. After two iterations a scaffold
        # list could look like: [[0],[1,2,3]]
        # which means that there are two scaffolds
        # one of those is composed of the contigs 1, 2 and 3

        # replace the diagonal from the matrix by zeros
        hic_matrix.diagflat(0)


        self.PE_scaffolds_file = PE_scaffolds_file
        # the list if initialized with the ids as the matrix row numbers
        self.hic = hic_matrix
        self.matrix = hic_matrix.matrix.copy()
        self.matrix.eliminate_zeros()
        self.cmatrix = None
        self.scaffolds = Scaffolds(self.hic.cut_intervals)
        self.N50 = []
        self.compute_N50()
        self.merged_paths = None
        # reads overlap file from SGA
#        self.overlap_graph = self.get_overlap_graph(overlap_graph_file)
        self.iteration = 0


    def assembleContigs_algorithm1(self):
        # remove from the computation problematic contigs
        self.hic = self.maskUnreliableRows(self.hic)
        self.group = HiCAssembler.get_groups(self.hic.cut_intervals)
        self.matrix = self.hic.matrix.copy()
        self.matrix.eliminate_zeros()
        self.cmatrix_orig = iterativeCorrection(self.matrix, M=1000)[0]
        self.dist1 = self.compute_distances(1)
        print "[{}] edge threshold set to: {}".format(inspect.stack()[0][3],
                                                      self.edge_threshold)

        self.scaffolds = Scaffolds(self.hic.cut_intervals)
        self.scaffolds.save_network("/home/ramirez/tmp/contig_g_start.gml")
        self.compute_N50()
        self.paths = [[x] for x in range(self.hic.matrix.shape[0])]

        # create a graph containing the nearest neighbors
        self.G = self.get_nearest_neighbors(self.paths, min_neigh=3,
                                            threshold=noise_level)
        #REMOVE
        self.G3 = self.G # avoid braking some code
        self.join_nearest_neighbors(self.paths, self.dist1[4][40000]['median'])
        self.compute_N50()

        self.iteration+=1

        self.dist2 = self.compute_distances(2)
#        self.reduce_to_flanks(flank_length=self.dist2[0])
        self.reduce_to_flanks_and_center(flank_length=self.dist2[0])
        self.G = self.get_nearest_neighbors(self.paths,min_neigh=2)
#        self.clean_rows_from_matrix(margin=2)
        self.join_nearest_neighbors(self.paths,self.dist2[4][0]['median'])
        self.compute_N50()


        self.iteration+=1

        self.dist4 = self.compute_distances(4)
        merge_length = self.dist4[0]
        self.reduce_to_flanks_and_center(flank_length=merge_length)
#        self.reduce_to_flanks(flank_length=merge_length)
        self.G = self.get_nearest_neighbors(self.paths,min_neigh=2)
        self.join_nearest_neighbors(self.paths,100)
#        self.join_nearest_neighbors(self.paths,self.dist3[4][merge_length]['median'])
        self.compute_N50()

        return 
        self.iterateGetContigsReduce()

        # finish
        self.scaffolds.save_network("/home/ramirez/tmp/final.gml")

    def assembleContigs_algorithm2(self):
        # remove from the computation problematic contigs
        self.hic.matrix.data[self.hic.matrix.data<MIN_MATRIX_VALUE] = 0
        self.matrix.eliminate_zeros()
        self.hic = self.maskUnreliableRows(self.hic, self.astat_file)
        self.group = HiCAssembler.get_groups(self.hic.cut_intervals)
        self.matrix = self.hic.matrix.copy()
        self.matrix.eliminate_zeros()
        self.cmatrix_orig = iterativeCorrection(self.matrix, M=1000)[0]
        self.cmatrix = self.cmatrix_orig

        self.scaffolds = Scaffolds(self.hic.cut_intervals)
        if self.PE_scaffolds_file:
            self.add_PE_scaffolds(self.PE_scaffolds_file)
        self.compute_N50()
        # needed for debugging, can be removed
        self.paths = [[x] for x in range(self.hic.matrix.shape[0])]
#        self.G3 = self.get_nearest_neighbors(self.paths, min_neigh=3, trans=True)


#        for merge in np.hstack([[1],np.asarray(np.arange(1,20)**2).astype(int)]):
        for merge in np.hstack([[1],np.asarray(np.arange(1,100)**MERGE_LENGTH_GROW).astype(int)])[0:ITER]:
            self.iteration+=1
            max_int = self.reduce_to_flanks_and_center(flank_length=MERGE_LENGTH*merge)
            if self.matrix.shape[0] < 2:
                return 
            if self.iteration == 1:
                try:
                    noise_level = np.sort(self.cmatrix.data)[::-1][self.cmatrix.shape[0]*1.6]
                except IndexError:
                    noise_level = self.cmatrix.data.min()
            else:
                try:
                    noise_level = np.sort(self.cmatrix.data)[::-1][self.cmatrix.shape[0]*4]
                except:
                    import ipdb;ipdb.set_trace()
#                noise_level = np.sort(self.cmatrix.data)[::-1][self.cmatrix.shape[0]*(1+np.log(self.iteration))]
            print "[{}] noise level set to: {}".format(inspect.stack()[0][3],
                                                          noise_level)
            # create a graph containing the nearest neighbors
#            import ipdb;ipdb.set_trace()
            self.G = self.get_nearest_neighbors(self.paths, min_neigh=2, trans=False,
                                                threshold=noise_level)

            self.prev_paths = self.scaffolds.get_all_paths()
            self.assemble_super_contigs(self.G, self.paths, max_int)
            orphans = [x for x in self.scaffolds.get_all_paths() if len(x) == 1]
            print "in total there are {} orphans".format(len(orphans))
            small = [x for x in self.scaffolds.get_paths_length() if x <= MERGE_LENGTH*merge]
            
            print "in total there are {} scaffolds smaller than {}. "\
                "Median {}".format(len(small), MERGE_LENGTH*merge, np.mean(small))
            if self.prev_paths ==  self.scaffolds.get_all_paths():
                print "paths not changing. Returning after {} iterations, "\
                    "merge_length: {}".format(self.iteration, MERGE_LENGTH*merge)
#                break

            self.compute_N50()
        return

    def get_edge_threshold(self, matrix):
        ma = triu(matrix, k=1)
        order_index = np.argsort(ma.data)[::-1]
        threshold = ma.data[order_index[ma.shape[0]*2]]
        return threshold

    def clean_rows_from_matrix(self, margin=10):
        """ 
        because the normalization
        of the matrix becomes impaired
        if paths get too long
        some contigs at the middle
        of such paths are removed
        """
        to_remove = []
        for path in self.scaffolds.get_all_paths():
            if len(path)> 2*margin:
                path = np.array(path)
                to_remove.extend(path[range(margin, len(path)-margin)])
        removed = np.flatnonzero(self.hic.matrix.sum(axis=1)==0)
        to_remove = np.delete(to_remove, removed)
        if len(to_remove):
            print "removing {} contigs from matrix".format(len(to_remove))
            ma = self.hic.matrix.tocsr()
            ma[to_remove,:] = 0
            ma = ma.tocsc()
            ma[:,to_remove] = 0

            try:
                self.hic.matrix_orig
            except:
                self.hic.matrix_orig = self.hic.matrix.copy()
            self.hic.matrix = ma

    def iterateGetContigsReduce(self, n=15):
        is_clean = False
        for iter_num in range(n):
            self.iteration += 1

            if self.matrix.shape[0] == 1:
                print "matrix has reached size 1"
                print "[{}] iteration: {}".format(inspect.stack()[0][3],
                                                  iter_num)
                break
            paths = self.scaffolds.get_all_paths()
            net = self.get_nearest_neighbors()
            self.compute_N50()
            self.assemble_super_contigs(net)
           # stop iterating if there is no improvement
            if paths == self.scaffolds.get_all_paths():
                if is_clean is False:
                    self.clean_rows_from_matrix()
                    is_clean = True
                else:
                    print "paths are not changing compared to previous iteration"
                    break
            
            # from the original hic matrix, get all
            # the rows and calls reffered on the scaffolds path
            self.matrix = self.reduce_matrix(self.hic.matrix,
                                             self.scaffolds.get_all_paths())
            if self.matrix.shape[0] < 2:
                print "[{}] matrix shape reached size 2  " \
                    "after {} iterations ".format(
                    inspect.stack()[0][3], self.matrix.shape)
                print iter_num
                break


            #####
            # convert the net to graph to save
            # and read using cytoscape
            self.scaffolds.save_network(
                "/home/ramirez/tmp/contig_g_{}.gml".format(self.iteration))
            GG = nx.from_scipy_sparse_matrix(net)
            for node in GG.nodes(data=True):
                GG.add_node(node[0], label="'{}'".format(node[0]), 
                            id=node[0])
            nx.write_gml(GG,
                         "/home/ramirez/tmp/net_g_{}.gml".format(self.iteration))
            """
            np.savez(
                '/home/ramirez/tmp/mat_{}'.format(iter_num), mat=self.matrix,
                con=super_contig)
            GG = nx.from_scipy_sparse_matrix(net)
            nx.write_edgelist(GG, '/home/ramirez/tmp/g_{}.txt'.format(iter_num))
            fh = open('/home/ramirez/tmp/g_attr_{}.txt'.format(iter_num), 'w')
            for k, v in self.id2label.iteritems():
                fh.write("{}\t{}\n".format(k, v))
            fh.close()
            """
            ##### end writting for debugging

    def maskUnreliableRows(self, hic, astat_file, min_length=MIN_LENGTH,
                           min_int=MIN_TOTAL_INT,
                           min_coverage=MIN_COVERAGE,
                           max_int_per_length=MAX_INT_PER_LENGTH,
                           min_int_per_length=0.001):
        """
        identifies rows that are too small or that have very
        few interactions. Those rows will be
        excluded from any computation.
        
        Params:
        ------
        hic: data structure returned by HiCMatrix
        min_length: in bp, minimun length of contig to be considered
        min_int: int, minimun number of total interactions that a contig must 
                 have in order to be considered.

        Returns:
        -------
        None: The matrix object is edited in place

        """
        astat_dict = dict()
        for line in astat_file:
            contig_id, value1, value2, value3, value4, astat = line.split('\t')
            astat_dict[contig_id] = astat


        contig_id, c_start, c_end, coverage = zip(*hic.cut_intervals)

        # get contigs that are repeated
        astat = np.array([astat_dict[x] for x in contig_id])
        repetitive = np.flatnonzero(astat < 25)
        # get scaffolds length
        length = np.array(c_end) - np.array(c_start) 

        # get the list of paths (usually just single contigs) that are too small
        small_list = np.flatnonzero(np.array(length) < min_length)
        # get the list of contigs that have too few interactions to other
        ma_sum = np.asarray(self.hic.matrix.sum(axis=1)).flatten()
        few_inter = np.flatnonzero(ma_sum < min_int)

        # get list of contigs that have reduced coverage:
        low_cov_list = np.flatnonzero(np.array(coverage) < min_coverage)

        """
        # get the list of contigs that have too many 
        # interactions per length
        int_per_bp = []
        if max_int_per_length:
            for indx in range(len(length)):
                int_per_bp.append(float(ma_sum[indx])/length[indx])

            if max_int_per_length == 'auto':
                int_per_bp = np.asarray(int_per_bp)
                length = np.asarray(length)
                max_int_per_length = max(int_per_bp[length>10000])
                min_int_per_length = min(int_per_bp[length>1000])
                print "The max int per bp and min int per bp were set to "\
                    "{} and {} respectively based on {} number of contigs "\
                    "longer than 20000 bp".format(max_int_per_length, 
                                                 min_int_per_length,
                                                 len(length[length>5000]))

            int_per_bp = np.array(int_per_bp)
            repetitive = np.flatnonzero((int_per_bp > max_int_per_length) |
                                        (int_per_bp < min_int_per_length))
            print "length repetitive {}".format(len(repetitive))
        else:
            repetitive = np.array([], dtype=int)
        """

        mask = np.unique(np.hstack([small_list, few_inter, low_cov_list, repetitive]))
        # if the elements to remove are part of a contig
        # that was splitted, eigher remove the whole
        # contig or keep the part that wants to be removed
        group = HiCAssembler.get_groups(self.hic.cut_intervals)
        mask_s = set(mask)
        
        for contig in np.array(contig_id)[mask]:
            if contig in group:
                g_start, g_end = group[contig]
                overlap = mask_s.intersection(range(g_start, g_end))
                
                # only remove the whole contig if a significant part of
                # it is to be removed
                if float(len(overlap))/(g_end-g_start) >= 0.75:
                    mask_ids = [np.flatnonzero(mask==x)[0] for x in overlap]
                    mask = np.delete(mask, mask_ids)
                    print "removing contig {} of size {} containing {} parts" \
                          "".format(contig,
                                    sum(length[g_start:g_end+1]), g_end-g_start)
                    # to avoid 
                    del group[contig]

#        mask = np.unique(np.hstack([mask, flattenList(new_mask)]))
        rows_to_keep = cols_to_keep = np.delete(range(self.hic.matrix.shape[1]), mask)
        print "Total: {}, small: {}, few inter: {}, low cover: {}, " \
            "repetitive: {}".format(len(contig_id), len(small_list),
                                    len(few_inter),
                                    len(low_cov_list),
                                    len(repetitive))
        if len(mask) == len(ma_sum):
            print "Filtering to strong. All regions would be removed."
            exit(0)

        print "\n[{}] removing {} ({}%) low quality regions from hic matrix " \
            "whose length is smaller than {} and have in total less " \
            "than {} interactions to other contigs.\n\nKeeping {} contigs.\n ".format(
            inspect.stack()[0][3], len(mask), 100* float(len(mask))/self.matrix.shape[0],
            min_length, min_int, len(rows_to_keep))
        total_length = sum(length)
        removed_length = sum(length[mask])
        kept_length = sum(length[rows_to_keep])
        print "Total removed length:{} ({:.2f}%)\nTotal " \
            "kept length: {}({:.2f}%)".format(removed_length, 
                                              float(removed_length)/total_length,
                                              kept_length,
                                              float(kept_length)/total_length)
        # remove rows and cols from matrix
        hic.matrix = self.hic.matrix[rows_to_keep, :][:, cols_to_keep]
        hic.cut_intervals = [self.hic.cut_intervals[x] for x in rows_to_keep]
        self.int_per_bp = int_per_bp[rows_to_keep]
        return hic
       
    def compute_distances(self, merge_length=1):
        """
        takes the information from all contigs that are splitted
        and returns three  vectors, one containing distances,
        other containing the number of contacts found for such
        distance and the third one containing the normalized
        contact counts. 

        Also it returns tabulated values per distance.
        """
        print "[{}] computing distances".format(inspect.stack()[0][3])

        dist_list = []
        contact_list = []
        norm_contact_list = []
        contig_length = []
        if len(self.group) == 0:
            message =  "Print contigs not in groups"
            message = "Contigs not long enough to compute a merge " \
                "of length {} ".format(merge_length)
            raise HiCAssemblerException(message)
        contig_parts = self.group.values()
        contig_parts = [x for x in contig_parts if x[1]-x[0] > merge_length]
        if len(contig_parts) > 200:
            # otherwise too many computations will be made
            # but 200 cases are enough to get 
            # an idea of the distributio of values
            contig_parts = contig_parts[0:200]
        if len(contig_parts) == 8:
            message = "Contigs not long enough to compute a merge " \
                "of length {} ".format(merge_length)
            raise HiCAssemblerException(message)
        for g_start, g_end  in contig_parts:
            contig_id, c_start, c_end, extra = \
                zip(*self.hic.cut_intervals[g_start:g_end])

            if c_start[0] > c_start[-1]:
                # swap
                contig_id, c_start, c_end, extra = \
                    zip(*self.hic.cut_intervals[g_start:g_end][::-1])
                
                contig_range = range(g_start, g_end)[::-1]
            else:
                contig_range = range(g_start, g_end)

            sub_m = self.hic.matrix[contig_range,:][:,contig_range]
            sub_mc = self.cmatrix_orig[contig_range,:][:,contig_range]
            length = len(contig_id)
            # find the closest (smaller) number
            # that is a multiple of merge_length                
            length = length - length % merge_length
            merge_list = np.split(np.arange(length), length/merge_length)
            if merge_list > 1:
                sub_m = self.reduce_matrix(
                    sub_m[range(length),:][:,range(length)], merge_list)
                sub_mc = self.reduce_matrix(
                    sub_mc[range(length),:][:,range(length)], merge_list)
                # merge start and end data
                c_start = np.take(c_start, [x[0] for x in merge_list])
                c_end = np.take(c_end, [x[-1] for x in merge_list])
                
            # get the row and col indices of the upper triangle
            # of a square matrix of size M
            row, col = np.triu_indices(len(c_start), k=1)
            data = np.asarray(sub_m.todense()[(row, col)]).flatten()
            data_norm = np.asarray(sub_mc.todense()[(row, col)]).flatten()

            end_row = np.take(c_end, row)
            start_col = np.take(c_start, col) - 1
            dist_list.append(start_col - end_row)
            contact_list.append(data)
            norm_contact_list.append(data_norm)
            contig_length.append(np.array(c_end) - np.array(c_start))

        dist_list = np.hstack(dist_list)

        contact_list = np.hstack(contact_list)
        norm_contact_list = np.hstack(norm_contact_list)
        contig_length = np.hstack(contig_length)

        # get the average contig length
        # approximated to the closest multiple of 10.000
        contig_length_std = np.std(contig_length)
        contig_length = int(round(np.mean(contig_length)/10000))*10000
        ## tabulate the distance information
        tab_dist = dict()
        tab_dist_norm = dict()
        dist_range = range(0, max(dist_list), contig_length) 
        for index in range(len(dist_range)-1) :
            contacts = contact_list[(dist_list >= dist_range[index]) & 
                                    (dist_list < dist_range[index+1])]
            if len(contacts) > 0:
                tab_dist[dist_range[index]] = {'mean': round(np.mean(contacts),2),
                                  'median': np.median(contacts),
                                  'std': round(np.std(contacts),2),
                                  'len': len(contacts),
                                  'min': min(contacts),
                                  'max': max(contacts)}

                norm_contacts = norm_contact_list[(dist_list >= dist_range[index]) & 
                                    (dist_list < dist_range[index+1])]
                tab_dist_norm[dist_range[index]] = {'mean': round(np.mean(norm_contacts),2),
                                  'median': int(np.median(norm_contacts)),
                                  'std': round(np.std(norm_contacts),2),
                                  'len': len(norm_contacts),
                                  'min': int(np.min(norm_contacts)),
                                  'max': int(np.max(norm_contacts))}

        return(contig_length, dist_list, contact_list, tab_dist, tab_dist_norm,
               contig_length_std)

    def reduce_to_flanks_and_center(self, flank_length=20000):
        """
        removes the contigs that lie inside of a path
        keeping only the flanking contigs. The length
        of the contigs left at the flanks tries to be
        close to the tip_length argument
        """
        print "[{}] computing paths merge length {}".format(inspect.stack()[0][3],
                                                            flank_length)

        to_keep = []
        path_list = self.scaffolds.get_all_paths()
        paths_flatten = [] # flattened list of merged_paths
                           # e.g [[1,2],[3,4],[5,6],[7,8]].
                           # This is in contrast to a list
                           # containing splitted paths that
                           # may look like [ [[1,2],[3,4]], [[5,6]] ]
        merged_paths = [] # list to keep the id of the new splitted paths 
                          # e.g. [[0,1], [2,3]]]
                          # which means path [1,2] in paths flatten has id 0
                          # and belongs to same path as [3,4] which has id 1
        i = 0
        
        contig_len = self.scaffolds.get_contigs_length()
        for path in path_list:
            
            split_path = HiCAssembler.get_flanks(path, flank_length, 
                                                 contig_len, 3)
            if self.iteration > 1:
                # skip short paths after iteration 1
                if sum(contig_len[HiCAssembler.flattenList(split_path)]) < flank_length*0.3:
                    continue
            merged_paths.append(range(i, len(split_path)+i))
            i += len(split_path)
            paths_flatten.extend(split_path)

#            print "in {} out {} ".format(path, split_path)
        if len(paths_flatten) == 0:
            print "[{}] Nothing to reduce.".format(inspect.stack()[0][3])
            return()

        to_keep = HiCAssembler.flattenList(paths_flatten)
        to_remove = np.delete(np.arange(self.hic.matrix.shape[0]),
                              to_keep)

        reduce_paths = paths_flatten[:]
        # the matrix is to be reduced
        # but all original rows should be referenced
        # that is why i append the to remove to the
        # reduce_paths
        reduce_paths.append(to_remove.tolist())
        if self.hic.matrix.shape[0] != len(HiCAssembler.flattenList(reduce_paths)):
            import pdb;pdb.set_trace()
        self.matrix = self.reduce_matrix(self.hic.matrix, reduce_paths).tolil()
        self.matrix = self.matrix[0:-1,:][:,0:-1]
#        self.matrix[:,-1] = 0
#        self.matrix[-1,:] = 0
        self.cmatrix = iterativeCorrection(self.matrix, M=1000)[0]
        # put a high value to all edges belonging to an original path
        max_int = self.cmatrix.data.max()+1
        for path in merged_paths:
            if len(path) > 1:
                # take pairs and replace the respective value
                # in the matrix by the masx int
#                import ipdb;ipdb.set_trace()
                for idx in range(len(path)-1):
                    # doing [(idx,idx+1),(idx+1,idx)]
                    # to keep the symmetry of the matrix.
                    # i.e. adding [1,2] and [2,1]
                    for c,d in [(idx,idx+1),(idx+1,idx)]:
#                        print "adding {},{}={}".format(path[c], path[d], max_int)
                        self.cmatrix[path[c], path[d]] = max_int

        self.paths = paths_flatten
        self.merged_paths = merged_paths
            
        return max_int

    @staticmethod
    def reduce_matrix(matrix, scaffolds):
        """
        This function sums the rows and colums corresponding
        to the scaffolds, returning a new sparse
        matrix of size len(scaffolds).

        The function uses sparse matrices tricks to work very fast.
        The idea is that all the cells in the new reduced matrix
        whose sum needs to be computed are expressed as a vector
        of bins.  Using the bincount function the sum of each bin
        is obtained. Then this sum vector is converted to a
        sparse matrix.


        Parameters
        ----------

        scaffolds : A list of lists. The values of the lists should
            correspond to the indices of the matrix.

        Returns
        -------

        A sparse matrix.

        >>> from scipy.sparse import csr_matrix
        >>> A = csr_matrix(np.array([[1,0],[0,1]]))
        >>> HiCAssembler.reduce_matrix(A, [(0,1)]).todense()
        matrix([[2]])
        >>> A = csr_matrix(np.array([[1,0,0],[0,1,0],[0,0,0]]))
        >>> HiCAssembler.reduce_matrix(A, [(0,1), (2,)]).todense()
        matrix([[2, 0],
                [0, 0]])
        >>> A = csr_matrix(np.array([[12,5,3,2,0],[0,11,4,1,1],
        ... [0,0,9,6,0], [0,0,0,10,0], [0,0,0,0,0]]))
        >>> A.todense()
        matrix([[12,  5,  3,  2,  0],
                [ 0, 11,  4,  1,  1],
                [ 0,  0,  9,  6,  0],
                [ 0,  0,  0, 10,  0],
                [ 0,  0,  0,  0,  0]])
        >>> ll = [(0,2), (1,3), (4,)]
        >>> HiCAssembler.reduce_matrix(A, ll).todense()
        matrix([[24, 17,  0],
                [17, 22,  1],
                [ 0,  1,  0]])
        >>> ll = [(0,2,4), (1,3)]
        >>> HiCAssembler.reduce_matrix(A, ll).todense()
        matrix([[24, 18],
                [18, 22]])
        """

        
        #use only the upper triangle of the matrix
        # and convert to coo
#        print "[{}] reducing matrix".format(inspect.stack()[0][3])
        if sum([len(x) for x in scaffolds]) != matrix.shape[0]:
            raise Exception("scaffolds length different than "
                            "matrix length")
        
        ma = triu(matrix, k=0, format='coo')
        M = len(scaffolds)

        # place holder for the new row and col
        # vectors
        new_row = np.zeros(len(ma.row))
        new_row[:] = np.nan
        new_col = np.zeros(len(ma.col))
        new_col[:] = np.nan

        # each original col and row index is converted
        # to a new index based on the scaffolds.
        # For example, if rows 1 and 10 are to be merged
        # then all rows whose value is 1 or 10 are given
        # as new value the index in the scaffolds list.
#        import pdb;pdb.set_trace()
        for index in range(M):
            for value in scaffolds[index]:
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
#        sum_array = sum_array[sum_array > 0]
        # To reconstruct the new matrix the row and col
        # positions need to be obtained. They correspond
        # to the positions of the unique values in the bin_array.
        uniq, ind = np.unique(bin_array, return_index=True)
        new_row_ = new_row[ind]
        new_col_ = new_col[ind]

        result = coo_matrix((sum_array, (new_row_, new_col_)),
                            shape=(M, M), dtype='int')

        diagmatrix = dia_matrix(([result.diagonal()], [0]),
                                shape=(M, M), dtype='int')

        # to make set the main diagonal to zero I
        # multiply the diagonal by 2
        diagmatrix *= 2

        # make result symmetric
        matrix = result + result.T - diagmatrix 
        matrix.eliminate_zeros()
        return matrix


    def test_overlap(self, u,v,**attr):
        id2name = self.scaffolds.id2contig_name 
        if id2name[u] != id2name[v]:
            s_path = None
            try:
                s_path = nx.shortest_path(self.overlap_graph, 
                                          id2name[u], id2name[v])
            except nx.NetworkXNoPath:
                pass
            except nx.NetworkXError:
                pass
            except:
                pass
            if s_path is not None:
                if len(s_path) == 2:
                    # the two contigs touch is other
                    # high evidence for merge
                    attr['overlap'] = True
                    overlap_data = self.overlap_graph.edge[id2name[u]][id2name[v]]
                    contig_b = self.hic.cut_intervals[v]
                    # find out in the overlap which contig is a and which is b
                    if overlap_data['length_a'] == contig_b[2]:
                        # swap u, and v
                        u,v = v,u
                    attr['source_direction'] = 0 if overlap_data['start_a'] == 0 else 1
                    attr['target_direction'] = 0 if overlap_data['start_b'] == 0 else 1
                    print "direct overlap between {}, {} found.".format(u,v)
                if len(s_path) == 3:
                    attr['shared_neighbor'] = True
                    print "indirect overlap between {}, {} {} found.".format(u,v, s_path)
                    # this case is complicate unless there is only 
                    # one short path, but even though it is still
                    # possible to assume that the shortest path
                    # is the one joing the two contings.
                    # Probably for some cases that assumption
                    # holds.
                    """
                    paths = [p for p in nx.all_shortest_paths(self.overlap_graph,
                                                              id2name[u], id2name[v])]
                    """

        return attr

    def add_edge(self, u,v, **attr):
        """
        Does several checks before commiting to add an edge.
        
        First it check whether the contigs to be joined share
        a significant number of contacts. Spurious
        interactions are discarted.

        Then tries to check in the overlap graph
        for evidence that may indicate 
        if two contigs may be together or
        one distance appart
        """
        try:
            self.scaffolds.check_edge(u,v)
        except HiCAssemblerException, e:
#            print "edge exception {}".format(e)
            return

        """
        if u not in self.G3.neighbors(v):
            print "{} is not close neighbor to {} ({})".format(u,v,
                                                             self.G3.neighbors(v))
            return
        if v not in self.G3.neighbors(u):
            print "{} is not close neighbor to {} ({})".format(v,u,
                                                             self.G3.neighbors(u))
            return
        """
        """
        if self.hic.matrix[u,v] <= 5:
            message = "number of shared pairs to join {} and {} "\
                  "too low {}, "\
                  "skipping. ".format(u, v, self.hic.matrix[u,v])
            raise HiCAssemblerException(message)
        """
        ##### DEBUG LINES
        if abs(u - v) != 1:
#            if u == 87:
#                import pdb;pdb.set_trace()
            print "[{}] an error joining {} and {} has been made\n {} \n{}"\
                "".format(inspect.stack()[0][3], u, v, attr, inspect.stack()[1][3])
        if abs(u - v) > 20:
            print "BAD error made {},{}".format(u,v)
#            import ipdb; ipdb.set_trace()
        """
            print "neighbors u {}, neighbors v {}".format(self.G3[u], self.G3[v])
            def print_part_pat(v):
                path_v = self.scaffolds.get_path_containing_source(v)
                v_index = path_v.index(v)
                if len(path_v)>2:
                    if v_index == 0:
                        v_nei = v_index + 2
                    else:
                        v_nei =  v_index
                        v_index -= 2
                    pp = path_v[v_index:v_nei]
                else:
                    pp = path_v
                try: 
                    print "path {}: {}".format(v, pp)
                except:
                    pass
            print_part_pat(u)
            print_part_pat(v)
#            import ipdb;ipdb.set_trace()
        """
        ##### END DEBUG LINES

        # checks if an edge may be solved/refined by looking at the 
        # overlap graph
        attr = self.test_overlap(u,v, **attr)
        self.scaffolds.add_edge(u, v, **attr)

        print "[{}] adding edge {} {}".format(inspect.stack()[0][3], u, v)

    def resolve_ambiguity(self, paths, pairs_to_evaluate):
        """ 
        Attempts to resolve merge cases
        that are ambiguous.
        When an edge is going to be created between
        two contigs, the first and second neighbors
        are evaluated. If they are too similar
        this code is called.
        
        The idea is to normalize a local copy
        of the matrix.
        """
        paths = HiCAssembler.flattenList(paths)
        map_id = np.zeros(max(paths)+1)
        for p in paths:
            map_id[p] = paths.index(p)

        res = self.hic.matrix[paths,:][:,paths]
        resc = iterativeCorrection(res)[0]
        pairs_contacts = []
        for pair in pairs_to_evaluate:
            # translate pair id to this matrix id
            t = (map_id[pair[0]], map_id[pair[1]])
            pairs_contacts.append(np.array([resc[t[0],t[1]]]))

        
        print pairs_contacts
        print pairs_to_evaluate
        return pairs_contacts
        
    @staticmethod
    def get_overlap_graph(overlap_file):
        """
        This is based on the SGA format stored
        in files ending with asqg.gz
        It contains, both the sequences and the
        network at the end of the file.
        The network part is recognized
        by the ED prefix.

        The format is
        ED      contig-46260 contig-5624 11103 11200 11201 73 170 171 1 -1

        where:
        11103  = start contig_a
        11200  = end contig_a
        11201 = len contig_a

        73  = start contig_a
        170  = end contig_a
        171 = len contig_a

        1 = direction (0 -> same direction, 1 -> contig_b needs to be flipped)
        -1 = no idea, same for all overlaps
        """
        if save_time:
            from os import path
            basename = path.basename(overlap_file)
            filename = '{}{}.gpickle'.format(TEMP_FOLDER, basename)
            try:
                print "loading pickled overlap {}".format(filename)
                G = nx.read_gpickle(filename)
                return G
            except:
                print "no saved pickled overlap found"
                pass

        
        print "[{}] reading overlap graph {} ".format(
            inspect.stack()[0][3], overlap_file)

        if overlap_file.endswith(".gz"):
            fh = gzip.open(overlap_file, 'rb')
        else:
            fh = open(overlap_file, 'r')
        G = nx.Graph()

        for line in fh:
            if line.startswith("ED"):
                node_a, node_b, start_a, end_a, len_a, \
                    start_b, end_b, len_b, direction, num = \
                    line.split('\t')[1].split(' ')
                for node in [node_a, node_b]:
                    if node == node_a:
                        length = int(len_a)
                    else:
                        length = int(len_b)
                    G.add_node(node, 
                               label=node,
                               length=length)

                if len_a > 1000 and len_b > 1000:
                    G.add_edge(
                        node_a, node_b,
                        start_a=int(start_a),
                        end_a=int(end_a),
                        length_a=int(len_a),
                        start_b=int(start_b),
                        end_b=int(end_b),
                        length_b=int(len_b),
                        direction=int(direction))
        if save_time:
            nx.write_gpickle(G, filename)
            nx.write_gml(G, TEMP_FOLDER+'{}.gml'.format(basename))

        return G

    def join_nearest_neighbors(self, paths, threshold='auto'):
        """ Wed, 09 Oct 2013 12:13:34 
        The idea is to order the matrix values
        and start merging neighbors until a threshold is 
        reached.

        The algorithm is as follows:

        1. identify the cell with  highest number of shared pairs and
        save the pair of rows that corresponds to that cell.
        2. merge the contigs (nodes) that correspond to such
        row, col combination
        3. Stop if the number of contacts falls below a threshold


        Parameters:
        ----------
        threshold: minimun number of contacts required to merge
                   two contigs.
        """


        """
        if paths:
            current_paths = self.scaffolds.get_all_paths()
            if len(current_paths) != self.matrix.shape[0]:
                self.matrix = self.reduce_matrix(self.hic.matrix,
                                                 current_paths)
        """
        # normalize the matrix
        self.cmatrix = iterativeCorrection(self.matrix, M=1000)[0]
        
        # consider only the upper triangle of the
        # matrix and convert it to COO for quick
        # operations
        ma = triu(self.cmatrix, k=1, format='coo')

        order_index = np.argsort(ma.data)[::-1]

        if threshold == 'auto':
            # set the threshold to be
            # the value corresponding to
            # length of the diagonal
            threshold = ma.data[order_index[ma.shape[0]]]
            print "[{}] threshold set to {}".format(inspect.stack()[0][3], threshold)

        for index in order_index:
            if ma.data[index] < threshold:
                break
            
            row = ma.row[index]
            col = ma.col[index]
            ma_val = ma.data[index]
            if col == row:
                continue

            u, v = [paths[x][0] for x in [row, col]]

            if self.scaffolds.has_edge(u, v):
                continue
            # if the col and row refer to a part
            # of the same contig, continue
            if self.scaffolds.id2contig_name[u] == \
               self.scaffolds.id2contig_name[v]:
                continue
            # skip very low unnormalized counts
            if self.matrix[row,col] <=5:
                if self.matrix[row,col] == 0.0:
                    import pdb;pdb.set_trace()
                message = "number of shared pairs to join {} and {} "\
                          "too low {} {} ({}), "\
                          "skipping. ".format(u, v,
                                              self.matrix[row,col],
                                              self.cmatrix[row,col],
                                              self.hic.matrix[u,v])
                print message
                continue
            
            # check close tie with nearest neighbors
            # get sorted list of neighbors for u and v

            def test_nei(u,v):
                if self.scaffolds.contig_G.degree(u) != 1:
                    return False
                nei_u = np.sort([x['weight']
                                 for x in self.G[u].values()
                                 if x['weight'] <= ma_val])[::-1]
                if len(nei_u) >1 and ma_val-nei_u[1] <= 0.1*ma_val:
                    print "Contig {} has a very close neighbor. " \
                          "Edge with {} ambiguous. {} {}.".format(u,v,
                                                                  ma_val,
                                                                  nei_u[1])
                    return True
                else:
                    return False
                
            if test_nei(u,v) or test_nei(v,u):
                continue

            self.add_edge(u,v,
                          iteration=self.iteration,
                          shared_pairs_merge=self.matrix[row,col],
                          shared_pairs=self.hic.matrix[u,v],
                          normalized_contacts=ma_val)
                          
            """ 
            self.arrange_and_merge(trans_path,
                                   iteration=self.iteration,
                                   shared_pairs=self.hic.matrix[row,col],
                                   normalized_contacts=ma_val)
            
            """ 
            """
            if len(neighbors[row]) < min_neigh or len(neighbors[col]) < min_neigh:
                neighbors[row].append(col)
                neighbors[col].append(row)
                net[row, col] = ma.data[index]

        return net
             """

        return

    def get_nearest_neighbors(self, paths, min_neigh=1, trans=True, threshold=0):
        """ Thu, 23 May 2013 16:14:51
        The idea is to take the matrix and order it
        such that neighbors are placed next to each other.

        The algorithm is as follows:

        1. identify the cell with  highest number of shared pairs and
        save the pair of rows that corresponds to that cell.
        2. remove that number from the matrix.
        3. Quit if all nodes already have 'min_neigh' neighbors,
           otherwise repeat.

        In theory, if everything is consistent, at the end of
        the for loop each node should have *only* two
        neighbors. This is rarely the case and some of the nodes
        end up with more than two neighbors. However, a large
        fraction of the nodes only have two neighbors and they
        can be chained one after the other to form a super
        contig.

        Parameters:
        ----------
        min_neigh: minimun number of neighbors to consider. 
                   If set to two, the function exists when
                   all contigs have at least two neighbors.
        """
        print "[{}]".format(inspect.stack()[0][3])

        # consider only the upper triangle of the
        # matrix and convert it to COO for quick
        # operations
        try:
            ma = triu(self.cmatrix, k=1, format='coo')
        except:
            import pdb;pdb.set_trace()
        order_index = np.argsort(ma.data)[::-1]
        # neighbors dictionary
        # holds, for each node the list of neighbors
        # using a sparse matrix is much faster
        # than creating a network and populating it
        net = lil_matrix(ma.shape, dtype='float64')

        # initialize neighbors dict
        neighbors = {}
        for index in range(ma.shape[0]):
            neighbors[index] = (None,0)

        counter = 0
        for index in order_index:
            counter += 1
            if counter % 100000 == 0:
                print "[{}] {}".format(inspect.stack()[0][3], counter)
            row = ma.row[index]
            col = ma.col[index]
            if col == row:
                continue
            if ma.data[index] < threshold:
                break
            # ignore neighbors that already
            # have two defined neighbors in the scaffolds
            """
            u, v = [paths[x][0] for x in [row, col]]
            if self.scaffolds.contig_G.degree(u) >= 2 or \
                    self.scaffolds.contig_G.degree(v) >= 2:
                continue
            """
            

            # add an edge if the number of neighbors 
            # is below min_neigh of if another
            # close value exists
            if neighbors[row][1] < min_neigh or \
                    neighbors[col][1] < min_neigh or\
                    neighbors[row][0] < ma.data[index]*1.1 or \
                    neighbors[col][0] < ma.data[index]*1.1:

                neighbors[row] = (ma.data[index], neighbors[row][1]+1)
                neighbors[col] = (ma.data[index], neighbors[col][1]+1)
                net[row, col] = ma.data[index]

        G = nx.from_scipy_sparse_matrix(net, create_using=nx.Graph())
        if trans:
            # remap ids 
            mapping = dict([(x,paths[x][0]) for x in range(len(paths))])
            G = nx.relabel_nodes(G, mapping)            

        # remove all edges not connected to flanks
        # the idea is that if a path already exist
        # no edges should point to it unless
        # is they are the flanks
        """
        if self.iteration==2:
            import ipdb;ipdb.set_trace()
        if self.merged_paths:
            flanks = set(HiCAssembler.flattenList(
                    [[x[0],x[-1]] for x in self.merged_paths]))
            for edge in G.edges():
                if len(flanks.intersection(edge)) == 0:
                    G.remove_edge(*edge)
        """
        return G

    @staticmethod
    def argsort(seq):
        """
        returns the indeces of an ordered python list
        """
        return sorted(range(len(seq)), key=seq.__getitem__)



    def assemble_super_contigs(self, G, paths, max_int, add_first_neighbors=True):
        """Mon, 14 Oct 2013 22:10:46 +0200
        Uses networkx to find shortest path
        joining connected - components

        Params:
        ------
        G: a networkx object

        Returns:
        -------

        super_contigs: list of lists. Each list member
        contains the sequence of sequential contigs
        """
        # debug line, should be removed
        GG = G.copy()
        print "[{}] Assembling contigs".format(inspect.stack()[0][3])
        for node in G.nodes(data=True):
            G.add_node(node[0], label="{}({})".format(paths[node[0]],node[0]), 
                       id=node[0])
        nx.write_gml(G,
                     "./prepros_g_{}.gml".format(self.iteration))

        cen = nx.degree(G)
        # high degree nodes are those with
        # more than two neighbors. 
        # more effort needs to be put on those cases
        # to identify the right connections
        high_deg = [k for k, v in cen.iteritems() if v > -2]
        prev_node = None
        while len(high_deg) > 0:
            if prev_node is not None and G.degree(prev_node)>2:
                import ipdb;ipdb.set_trace()
            node = high_deg.pop(0)
            prev_node = node
            # while resolving other nodes,
            # the current node may have now
            # degree of 2 or less and is not
            # neccesary to continue
            if G.degree(node) <=2:
                continue
            weights, nodes = zip(*[(v['weight'], k)
                                   for k, v in G[node].iteritems()])
            order = HiCAssembler.argsort(weights)[::-1]
            max_nodes = len([x for x in weights if x==max_int])
            nodes = list(nodes)
            # if the node already has two max_int neighbors
            # discard the rest
            if max_nodes == 2:
                G.remove_edges_from([(node, nodes[x]) for x in order[2:] ])
                continue
            if max_nodes == 1:
                order.pop(0)
            # keep_highest_edge if this is 
            # at least the second largest * 1.5
            # edges that have the highest value are skipped
            # This is a clear case and permutation is not needed
            if weights[order[1]]*1.6 < weights[order[0]]:
                print "highest neighbor of {} is {} with "\
                    "value {:.2f}, second best {}, {:.2f}".format(node,
                                                                  nodes[order[0]],
                                                                  weights[order[0]],
                                                                  nodes[order[1]],
                                                                  weights[order[1]])

                G.remove_edges_from([(node, nodes[y]) for y in order[1:]])
            else:
                direct_neighbors = G[node].keys()
                # remove from the list of neighors
                # the nodes that are not flanks
    #            neighbors.append(node)
                if add_first_neighbors:
                    first_neighbors =HiCAssembler.flattenList([G[x].keys() for x in direct_neighbors])
                    neighbors = np.unique(direct_neighbors + first_neighbors)
                else:
                    neighbors = direct_neighbors + [node]
                if len(neighbors)>7:
                    print "node {} has too many neighbors {}\n{}\n{}".format(
                        node,neighbors,
                        [self.paths[x] for x in neighbors],
                        [int(self.cmatrix[neighbors[x], neighbors[x+1]]) for x in range(len(neighbors)-1)])

                    G.remove_edges_from([(node, y) for y in direct_neighbors])
                else:
                    bw_order = HiCAssembler.permute(self.cmatrix, neighbors)
                    print "bw permutation of node: {} is: {}\n{}\n{}\n{}".format(
                        node,
                        bw_order,
                        [self.paths[x] for x in bw_order],
                        [int(self.cmatrix[bw_order[x], bw_order[x+1]]) for x in range(len(bw_order)-1)],
                        [int(self.matrix[bw_order[x], bw_order[x+1]]) for x in range(len(bw_order)-1)])
                    # remove from hig_deg

                    # remove from G
                    node_idx = bw_order.index(node)
                    true_neigh = []
                    if node_idx > 0:
                        true_neigh.append(bw_order[node_idx-1])
                    if node_idx < len(bw_order) - 1:
                        true_neigh.append(bw_order[node_idx+1])

                    G.remove_edges_from([(node, y) for y in direct_neighbors
                                         if y not in true_neigh])
            print "the nei left for {} are {}".format(node,
                                                      G[node].keys())


        cen = nx.degree(G)
        high_deg2 = [k for k, v in cen.iteritems() if v > 2]
        if len(high_deg2):
            print "not all hubs were flattened {}".format(high_deg)
            import pdb;pdb.set_trace()

        # break self loops
        conn = nx.connected_components(G)
        for nodes in conn:
            if len(nodes)==1:
                continue
            # get all nodes with degree 1.
            # This should be the nodes at the
            # opposite sides. All other nodes
            # in between should have a degree equal to 2
            deg_one = [x for x in nodes if G.degree(x) == 1]
            if len(deg_one) != 2:
                print '[{}] The nodes form a closed loop' \
                    'because no opposite sides exist' \
                    '{}'.format(inspect.stack()[0][3], nodes)
                if len(nodes) <= 7:
                    bw_order = HiCAssembler.permute(self.matrix, nodes)
                    # break the closed loop by setting the
                    # bw_order as path
                    for edge in G.edges(nodes):
                        G.remove_edge(*edge)
                    G.add_path(bw_order)
                else: 
                    print "closed loop found but is too large for, "\
                        "permutation. Removing weakest link" 
                
        for node in G.nodes(data=True):
            G.add_node(node[0], label="{}({})".format(paths[node[0]],node[0]), 
                       id=node[0])
        nx.write_gml(G,
                     "./net_g_{}.gml".format(self.iteration))
        # after the while loop
        # only paths should be found and 
        # all edges can be added
        print "the nei left for 1 are {}".format(G[1].keys())
        for edge in G.edges_iter():
            if self.matrix[edge[0],edge[1]] < 10:
                continue
            u,v = [paths[x][0] for x in edge]
            self.add_edge(u,v,
                          iteration=self.iteration,
                          shared_pairs=self.hic.matrix[u,v],
                          normalized_contacts=self.cmatrix_orig[u,v])

        return self.scaffolds.get_all_paths()


    def compute_N50(self):

        length = np.sort(np.array(self.scaffolds.get_paths_length()))
        length = length[length>200]
        cumsum = np.cumsum(length)
        for i in range(len(length)):
            if cumsum[i] >= float(cumsum[-1]) / 2:
                break
        try:
            itera = self.iteration
        except:
            itera = 0

        print "[{}] iteration:{}\tN50: {}\tMax length: {} " \
              "No. scaffolds {}".format(
            inspect.stack()[0][3], itera, length[i],
            length[-1], len(self.scaffolds.get_all_paths()))
                        
        self.N50.append((itera, length[i], self.scaffolds.get_all_paths()))

    @staticmethod
    def flattenList(alist):
        """
        given a list of list of list, returns a list
        For example: given [1,[[2]], [3,4]]
        returns [1, 2, 3 4]
        This is a recursive function.

        >>> HiCAssembler.flattenList([1,[[2]], [3,4]])
        [1, 2, 3, 4]
        """
        ret = []
        for values in alist:
            if type(values) != list:
                ret.append(values)
            else:
                ret.extend(HiCAssembler.flattenList(values))
        return ret

    @staticmethod
    def get_groups(contig_list):
        """
        Takes a list of contigs in the format
        of the HiCMatrix object (HiCMatrix.cut_intervals) and
        returns a dictionary contaning the range of
        contigs that span in the list

        Params:
        ======
        contig_list: The format is [(contig_id, start, end, flag), (contig_id2 ....)]

        Return:
        ======

        group: dictionary containing as key the contig_id, and as value
               a duple with the start and end indices of the group.
        """
        contig_id, c_start, c_end, extra = zip(*contig_list)

        prev = None
        in_group = False
        group = dict()
        for index in range(len(contig_id)):
            if contig_id[index]==prev and in_group is False:
                in_group = True
                group_start=index - 1
            elif contig_id[index]!=prev and in_group is True:
                in_group = False
                group_end = index
                group[contig_id[group_start]]=(group_start, group_end)
            prev = contig_id[index]

        return group

    @staticmethod
    def bw(ma):
        """
        Computes my version of the bandwidth of the matrix
        which is defined as \sum_i\sum_{j=i} log(M(i,j)*(j-i))
        The matrix that minimizes this function should have
        higher values next to the main diagonal and 
        decreasing values far from the main diagonal
        """
        ma = triu(ma, k=1, format='coo')
        ma.data *= np.log10(ma.col - ma.row)
#        ma.data *= ma.col - ma.row
        return ma.sum()

    @staticmethod
    def permute(ma, indices):
        """
        Computes de bw for all permutations of rows (and, because
        the matrix is symetric of cols as well).
        Returns the permutation having the minumun bw.
        
        """
        import itertools
        ma = ma[indices,:][:,indices]
#        ma = iterativeCorrection(ma, M=10)[0]
        mappping = dict([(x,indices[x]) for x in range(len(indices))])
        bw_value = []
        perm_list = []
        for perm in itertools.permutations(range(len(indices))):
            mapped_perm = [mappping[x] for x in perm]
            if mapped_perm[::-1] in perm_list:
                continue
            bw_value.append(HiCAssembler.bw(ma[perm,:][:,perm]))
            perm_list.append(mapped_perm)

        min_val = min(bw_value)
        min_indx = bw_value.index(min_val)
#        return (perm_list[min_indx],perm_list,  bw_value)
        return perm_list[min_indx]

    @staticmethod
    def get_flanks(path, flank_length, contig_len,
                   recursive_repetitions, counter=0):
        """
        Takes a path are returns the flanking regions
        plus the inside. This is a recursive function
        and will split the inside as many times 
        as possible, stoping when 'recursive_repetitions'
        have been reached

        The flank lengh is set to 2000, thus, groups of two should be
        selected
        >>> HiCAssembler.get_flanks([1,2,5,3,4], 2000,
        ... np.array([1000,1000,1000,1000,1000,2000]), 3)
        [[1, 2], [5], [4, 3]]

        Same as before, but now I set id 5 to be smaller. 
        Now 5 should be skipped as is not at least flank_length*0.75
        >>> HiCAssembler.get_flanks([1,2,5,3,4], 2000,
        ... np.array([1000,1000,1000,1000,1000,800]), 3)
        [[1, 2], [4, 3]]

        Get the flanks, and do not recursively iterate
        >>> HiCAssembler.get_flanks([1,2,5,3,4], 1000,
        ... np.array([1000,1000,1000,1000,1000,1000]), 1)
        [[1], [4]]

        Get the flanks, and iterate twice
        >>> HiCAssembler.get_flanks([1,2,5,3,4], 1000,
        ... np.array([1000,1000,1000,1000,1000,1000]), 2)
        [[1], [2], [3], [4]]
        """
        counter += 1
        if counter > recursive_repetitions:
            return []

        tolerance_max = flank_length * 1.25
        tolerance_min = flank_length * 0.75
        path_length_sum = sum(contig_len[path])
        interior = []
        flanks = []
        def flank(path):
            flank = []
            for x in path:
                flank_sum = sum(contig_len[x] for x in flank)
                if flank_sum > tolerance_max:
                    break
                elif tolerance_min <= flank_sum <= tolerance_max:
                    break
                flank.append(x)
            return flank

#        if path == [1,2]:
#            import ipdb;ipdb.set_trace()
        if len(path) == 1:
            if contig_len[path[0]]>tolerance_min or counter == 1:
                flanks = [path]
        elif path_length_sum < 2*flank_length*0.75:
            path_half = len(path)/2
            left_flank = path[0:path_half]
            right_flank = path[path_half:][::-1]
            flanks.extend([left_flank, right_flank])
        else:
            left_flank=flank(path)
            right_flank=flank(path[::-1])
            over = set(left_flank).intersection(right_flank)
            if len(over):
                # remove overlap
                left_flank = [x for x in left_flank if x not in over]

            if len(left_flank) == 0 or len(right_flank) == 0:
                path_half = len(path)/2
                left_flank = path[0:path_half]
                right_flank = path[path_half:][::-1]

            interior = [x for x in path 
                        if x not in HiCAssembler.flattenList(left_flank+right_flank)]

            if len(interior):
                interior = HiCAssembler.get_flanks(interior, flank_length, contig_len, 
                                      recursive_repetitions, counter=counter)
            if len(left_flank): flanks.append(left_flank)
            if len(interior): flanks.extend(interior)
            if len(right_flank): flanks.append(right_flank)

        try:
            if len(left_flank) == 0 or len(right_flank) == 0:
                import ipdb;ipdb.set_trace()
        except:
            pass
        return flanks

    def add_PE_scaffolds(self, scaffolds_file, format='sga'):
#        raise Exception("function add_PE_scaffolds has a problem. When joining,"
#                        "contigs that are splitted into groups, is not possible "
#                        "to decide which extremes get together.")
        """
        this code parses the file that contains
        the information to construct PE_scaffolds
        from contigs.

        This is saved in a .scaf file
        The format looks like this
        but I don't have an explanation:
        contig-863220\tcontig-513939,-34,18.1,1,0,D\tcontig-674650,133,34.1,1,0,D
        
        I imagine the format means:

        contig-863220 -> contig-513939 [d=-34, e=18.1, join=end-start]

        The last part, which is 1,0,D in both cases I thing it
        explains how to join the contigs: 

        0,0: start-star,
        0,1: start-end,
        1,0: end-start,
        1,1: end-end

        """
        print "[{}] reading scaffolding data based on PE {} ".format(
            inspect.stack()[0][3], scaffolds_file.name)

        contig_name2id = dict([(self.scaffolds.id2contig_name[x],x) 
                               for x in range(len(self.scaffolds.id2contig_name))])

        def get_contig_id(contig_name, direction):
            if contig_name in self.group:
                # need to decide if the link should
                # be made with the first or with the
                # last member of the group
                first_group, last_group = self.group[contig_name]
                last_group -=1 # the last in the group is always the +1 id
                               # such that doing [first_group:last_group] 
                               # returns all group members
                if first_group == 35:
                    import ipdb;ipdb.set_trace()
                # This check is needed because the contig can be 
                # inverted
                # cut_intervals format is:
                # (contig_id, start, end, coverage)
                if self.hic.cut_intervals[first_group][1] > \
                        self.hic.cut_intervals[last_group][1]:
                    # invert the order if the group members
                    # are ordered from last to first
                    first_group, last_group = last_group,first_group

                if direction == 0: # 0 means start
                        contig_id = first_group
                el