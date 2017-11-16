"""
A numba class representing a graph data structure, with
an implementation of an efficient algorithm for computing
the minimum spanning tree.

"""
import numpy as np
import numba as nb


BEGIN = 0
SIZE = 1
EDGE_ID = 0
NEXT = 1
MAX_LOW_DEGREE = 8


_graph_spec = [
    ('_nedges', nb.intp),
    ('_nnodes', nb.intp),
    ('_edges', nb.intp[:, :]),
    ('_edges_weight', nb.float64[:]),
    ('_adjacency', nb.intp[:, :]),
    ('_low_degrees', nb.intp[:]),
    ('_large_degrees', nb.intp[:]),
    ('_low_degrees_size', nb.intp),
    ('_large_degrees_size', nb.intp),
    ('_edge_bucket', nb.intp[:]),
    ('_edges_in_bucket', nb.intp[:]),
    ('_edges_in_bucket_size', nb.intp),
    ('_adjacency_list', nb.intp[:, :]),
    ('_tmp', nb.intp),
    ('_profile_op_main', nb.intp),
    ('_profile_op_collapse', nb.intp),
    ('_profile_op_clean', nb.intp),
]


@nb.jitclass(_graph_spec)
class Graph(object):

    def __init__(self, edges, edges_w, nnodes):

        # -- create the internal structures:
        self._nedges = edges.shape[0]
        self._nnodes = nnodes

        # copy of edges
        self._edges = edges.copy()

        # reference to edges weight
        self._edges_weight = edges_w

        # pointers to adjacency data for each type (begin, size)
        self._adjacency = np.zeros((nnodes, 2), np.intp)

        # arrays of large and low degrees nodes
        self._low_degrees = np.empty(nnodes, np.intp)
        self._large_degrees = np.empty(nnodes, np.intp)
        self._low_degrees_size = 0
        self._large_degrees_size = 0

        # buckets for graph cleaning
        self._edge_bucket = np.full(nnodes, -1, np.intp)
        self._edges_in_bucket = np.empty(nnodes, np.intp)
        self._edges_in_bucket_size = 0

        # -- compute adjacency:

        # first pass: create edge vector and compute adjacency size
        for edge_id in range(self._nedges):
            node1_id = self._edges[edge_id, 0]
            node2_id = self._edges[edge_id, 1]

            # update adjacency size
            self._adjacency[node1_id, SIZE] += 1
            self._adjacency[node2_id, SIZE] += 1

        # compute adjacency pointers
        self._adjacency[0, BEGIN] = 0
        for node_id in range(1, self._nnodes):
            self._adjacency[node_id, BEGIN] = (
                self._adjacency[node_id - 1, BEGIN] +
                self._adjacency[node_id - 1, SIZE])
            self._adjacency[node_id - 1, SIZE] = 0

        # init adjacency list
        adjacency_list_size = (self._adjacency[-1, BEGIN] +
                               self._adjacency[-1, SIZE])
        # (list of edge_id, next)
        self._adjacency_list = np.empty((adjacency_list_size, 2), np.intp)

        self._adjacency[-1, SIZE] = 0

        for adj_data_i in range(adjacency_list_size):
            self._adjacency_list[adj_data_i, NEXT] = adj_data_i + 1

        # second pass on edges: fill adjacency list
        for edge_id in range(self._nedges):
            n1 = self._edges[edge_id, 0]
            n2 = self._edges[edge_id, 1]

            row1 = self._adjacency[n1, BEGIN] + self._adjacency[n1, SIZE]
            row2 = self._adjacency[n2, BEGIN] + self._adjacency[n2, SIZE]

            self._adjacency_list[row1, EDGE_ID] = edge_id
            self._adjacency_list[row2, EDGE_ID] = edge_id

            self._adjacency[n1, SIZE] += 1
            self._adjacency[n2, SIZE] += 1

        # -- cluster nodes by degree:
        for node_id in range(self._nnodes):

            # if degree is low enough
            if self._adjacency[node_id, SIZE] <= MAX_LOW_DEGREE:

                # update position of node in low degree vector
                self._low_degrees[self._low_degrees_size] = node_id
                self._low_degrees_size += 1

            else:

                # add it to the large degree list
                self._large_degrees[self._large_degrees_size] = node_id
                self._large_degrees_size += 1

        self._profile_op_main = 0
        self._profile_op_collapse = 0
        self._profile_op_clean = 0

    def profile(self):
        return (self._profile_op_main,
                self._profile_op_collapse,
                self._profile_op_clean)

    def use(self):
        """fonction to force usage of the class.

        Numba will not call the constructor before.
        """
        self._tmp = 0

    def test_connect(self):
        """Check if the input is a fully connected graph.

        Not used for mst algorithm, only for debugging.
        """
        visited = np.full(self._nnodes, False, np.bool)
        stack = np.empty(self._adjacency_list.size, np.intp)
        stack_size = 1
        stack[0] = 0   # start from node 0

        while stack_size > 0:
            stack_size -= 1
            n = stack[stack_size]
            if(visited[n]):
                continue
            visited[n] = True

            adjacency_data_ptr = self._adjacency[n, BEGIN]
            for step in range(self._adjacency[n, SIZE]):

                parsed_edge_id = self._adjacency_list[adjacency_data_ptr, EDGE_ID]
                adjacency_data_ptr = self._adjacency_list[adjacency_data_ptr, NEXT]

                n2 = self._edges[parsed_edge_id, 0]
                n22 = self._edges[parsed_edge_id, 1]
                if n2 == n:
                    n2 = n22

                stack[stack_size] = n2
                stack_size += 1

        for r in visited:
            if not r:
                return False
        return True

    def get_min_span_tree(self):
        """Fill the minimal spanning tree into the tree structure."""

        # the tree is spaning, so it has same number of node as the graph
        # its number of edges is then n_nodes-1
        mstree = np.empty(self._nnodes - 1, np.intp)
        mstree_size = 0

        # loop while there are remaining vertices
        while self._low_degrees_size > 0:

            # parse all low degree nodes
            for inode in range(self._low_degrees_size):

                # choose a low degree node
                node_id = self._low_degrees[inode]

                # the node may have large degree after collapse
                if self._adjacency[node_id, SIZE] > MAX_LOW_DEGREE:
                    self._large_degrees[self._large_degrees_size] = node_id
                    self._large_degrees_size += 1
                    continue

                # get the minimal weight edge that leaves that node
                found_edge = -1
                found_edge_weight = np.finfo(np.float64).max

                adjacency_data_ptr = self._adjacency[node_id, BEGIN]
                for step in range(self._adjacency[node_id, SIZE]):

                    # find next adjacent edge in the list
                    parsed_edge_id = self._adjacency_list[adjacency_data_ptr, EDGE_ID]
                    adjacency_data_ptr = self._adjacency_list[adjacency_data_ptr, NEXT]

                    # check if the edge is valid (connected to a existing node)
                    # and if the weight is better than the previously found one
                    opp_node = self._edges[parsed_edge_id, 0]
                    opp_node2 = self._edges[parsed_edge_id, 1]
                    if opp_node == node_id:
                        opp_node = opp_node2
                    if (opp_node != node_id and self._adjacency[opp_node, SIZE] > 0 and
                        self._edges_weight[parsed_edge_id] < found_edge_weight):

                        # update found information
                        found_edge = parsed_edge_id
                        found_edge_weight = self._edges_weight[parsed_edge_id]

                    self._profile_op_main += 1

                # if not found, continue
                if found_edge == -1:
                    continue

                # else add the edge to the tree
                mstree[mstree_size] = found_edge
                mstree_size += 1

                # and collapse it toward opposite node

                # find connected node B
                node_B_id = self._edges[found_edge, 0]
                node_B_id2 = self._edges[found_edge, 1]
                if node_B_id == node_id:
                    node_B_id = node_B_id2

                # rename all A to B in adjacency of A
                adjacency_data_ptr = self._adjacency[node_id, BEGIN]
                for step in range(self._adjacency[node_id, SIZE]):

                    edge_AC_id = self._adjacency_list[adjacency_data_ptr, EDGE_ID]
                    if step != self._adjacency[node_id, SIZE] - 1:
                        adjacency_data_ptr = self._adjacency_list[adjacency_data_ptr, NEXT]

                    # avoid self loop. A doesn't exist anymore, so edge AB
                    # will be discarded
                    if self._edges[edge_AC_id, 0] == node_id:
                        self._edges[edge_AC_id, 0] = node_B_id
                    else:
                        self._edges[edge_AC_id, 1] = node_B_id

                    self._profile_op_collapse += 1

                # Append adjacency of B at the end of A
                self._adjacency_list[adjacency_data_ptr, NEXT] = (
                    self._adjacency[node_B_id, BEGIN])

                # And collapse A into B
                self._adjacency[node_B_id, BEGIN] = self._adjacency[node_id, BEGIN]
                self._adjacency[node_B_id, SIZE] += self._adjacency[node_id, SIZE]

                # Remove the node from the graph
                self._adjacency[node_id, SIZE] = 0

            #  clean the graph if there is no more low degrees nodes
            self._low_degrees_size = 0
            self.clean()

        return mstree

    def clean(self):
        """Clean up graph (many edges are duplicates or self loops)."""

        # parse large degree in reverse order (easier to remove items)
        nlarge = self._large_degrees_size
        self._large_degrees_size = 0
        for i in range(nlarge):

            # current parsed node
            node_A_id = self._large_degrees[i]

            # we will store all edges from A in the bucket, so that each edge
            # can appear only once
            self._edges_in_bucket_size = 0

            adjacency_data_ptr = self._adjacency[node_A_id, BEGIN]
            for step in range(self._adjacency[node_A_id, SIZE]):

                edge_AB_id = self._adjacency_list[adjacency_data_ptr, EDGE_ID]
                adjacency_data_ptr = self._adjacency_list[adjacency_data_ptr, NEXT]

                # find node B
                node_B_id = self._edges[edge_AB_id, 0]
                node_B_id2 = self._edges[edge_AB_id, 1]
                if node_B_id == node_A_id:
                    node_B_id = node_B_id2

                self._profile_op_clean += 1

                if (self._adjacency[node_B_id, SIZE] > 0 and
                    node_B_id != node_A_id):

                    # edge_bucket contain the edge_id connecting to opp_node_id
                    # or NodeId(-1)) if this is the first time we see it
                    edge_AB_id_in_bucket = self._edge_bucket[node_B_id]

                    # first time we see
                    if(edge_AB_id_in_bucket == -1):
                        self._edge_bucket[node_B_id] = edge_AB_id
                        self._edges_in_bucket[self._edges_in_bucket_size] = node_B_id
                        self._edges_in_bucket_size += 1

                    else:
                        # get weight of AB and of previously stored weight
                        weight_in_bucket = self._edges_weight[edge_AB_id_in_bucket]
                        weight_AB = self._edges_weight[edge_AB_id]

                        # if both weight are the same, we choose edge
                        # with min id
                        if weight_in_bucket == weight_AB:
                            self._edge_bucket[node_B_id] = min(
                                edge_AB_id_in_bucket, edge_AB_id)
                        # else we store AB only if it has lower weight
                        elif weight_AB < weight_in_bucket:
                            self._edge_bucket[node_B_id] = edge_AB_id

            # recompute connectivity of node A
            cur_ptr = self._adjacency[node_A_id, BEGIN]
            self._adjacency[node_A_id, SIZE] = 0

            for node_B_iter in range(self._edges_in_bucket_size):

                node_B_id = self._edges_in_bucket[node_B_iter]

                self._adjacency_list[cur_ptr, EDGE_ID] = self._edge_bucket[node_B_id]
                cur_ptr = self._adjacency_list[cur_ptr, NEXT]

                # clean occupency of edge_bucket for latter use
                self._edge_bucket[node_B_id] = -1

                self._profile_op_clean += 1

            self._adjacency[node_A_id, SIZE] += self._edges_in_bucket_size

            # update low degree information, if node A has low degree
            if self._adjacency[node_A_id, SIZE] <= MAX_LOW_DEGREE:

                # add the node in low degree list
                if self._adjacency[node_A_id, SIZE] > 0:
                    self._low_degrees[self._low_degrees_size] = node_A_id
                    self._low_degrees_size += 1
            else:
                self._large_degrees[self._large_degrees_size] = node_A_id
                self._large_degrees_size += 1
