import numba
import numpy as np

from ._union_find import UnionFind
from ._graph_mst import Graph


@numba.njit
def reset_receivers(receivers, nnodes):
    for inode in range(nnodes):
        receivers[inode] = inode


@numba.njit
def compute_receivers_d8(receivers, dist2receivers, elevation,
                         nx, ny, dx, dy):
    # queen (D8) neighbor lookup
    dr = np.array([-1, -1, -1, 0, 0, 1, 1, 1], dtype=np.intp)
    dc = np.array([-1, 0, 1, -1, 1, -1, 0, 1], dtype=np.intp)

    length = np.sqrt((dy * dr)**2 + (dx * dc)**2)

    tiny = np.finfo(elevation.dtype).tiny

    for r in range(1, ny - 1):
        for c in range(1, nx - 1):
            inode = r * nx + c
            slope_max = tiny

            for k in range(8):
                ineighbor = (r + dr[k]) * nx + (c + dc[k])
                slope = (elevation[inode] - elevation[ineighbor]) / length[k]

                if slope > slope_max:
                    slope_max = slope
                    receivers[inode] = ineighbor
                    dist2receivers[inode] = length[k]


@numba.njit
def compute_donors(ndonors, donors, receivers, nnodes):
    ndonors[:] = 0

    for inode in range(nnodes):
        if receivers[inode] != inode:
            irec = receivers[inode]
            donors[irec, ndonors[irec]] = inode
            ndonors[irec] += 1


@numba.njit
def _add2stack(inode, ndonors, donors, stack, istack):
    for k in range(ndonors[inode]):
        idonor = donors[inode, k]
        stack[istack] = idonor
        istack += 1
        istack = _add2stack(idonor, ndonors, donors, stack, istack)

    return istack


@numba.njit
def compute_stack(stack, ndonors, donors, receivers, nnodes):
    istack = 0

    for inode in range(nnodes):
        if receivers[inode] == inode:
            stack[istack] = inode
            istack += 1
            istack = _add2stack(inode, ndonors, donors,
                                stack, istack)


@numba.njit
def propagate_area(area, stack, receiver):
    for inode in stack[-1::-1]:
        if receiver[inode] != inode:
            area[receiver[inode]] += area[inode]


@numba.njit
def compute_basins(basins, outlets, stack, receivers, nnodes):
    ibasin = -1

    for inode in range(nnodes):
        istack = stack[inode]
        irec = receivers[istack]

        if irec == istack:
            ibasin += 1
            outlets[ibasin] = istack

        basins[istack] = ibasin

    nbasins = ibasin + 1

    return nbasins


@numba.njit
def compute_pits(pits, outlets, active_nodes, nbasins):
    ipit = 0

    for ibasin in range(nbasins):
        inode = outlets[ibasin]

        if active_nodes[inode]:
            pits[ipit] = inode
            ipit += 1

    npits = ipit

    return npits


@numba.njit
def _connect_basins(conn_basins, conn_nodes, conn_weights,
                    nbasins, basins, outlets, receivers, stack,
                    active_nodes, elevation, nx, ny):
    """Connect adjacent basins together through their lowest pass.

    Creates an (undirected) graph of basins and their connections.

    The resulting graph is defined by:

    - `conn_basins` (nconn, 2): ids of adjacent basins forming the edges
    - `conn_nodes` (nconn, 2): ids of grid nodes forming the lowest passes
      between two adjacent basins.
    - `conn_weights` (nconn) weights assigned to the edges. It is equal to the
      elevations of the passes, i.e., the highest elevation found for each
      node couples defining the passes.

    The function returns:

    - `nconn` : number of edges.
    - `basin0` : id of one open basin (i.e., where `outlets[id]` is not a
      pit node) given as reference.

    The algorithm parses each grid node of the flow-ordered stack and checks if
    the node and (each of) its neighbors together form the lowest pass between
    two different basins.

    Node neighbor lookup doesn't include diagonals to ensure that the
    resulting graph of connected basins is always planar.

    Connections between open basins are handled differently:

    Instead of finding connections between adjacent basins, virtual
    connections are added between one given basin and all other
    basins.  This may save a lot of uneccessary computation, while it
    ensures a connected graph (i.e., every node has at least an edge),
    as required for applying minimum spanning tree algorithms implemented in
    this package.

    """
    iconn = 0

    basin0 = numba.intp(-1)
    ibasin = numba.intp(0)

    conn_pos = np.full(nbasins, -1, dtype=np.intp)
    conn_pos_used = np.empty(nbasins, dtype=np.intp)
    conn_pos_used_size = 0

    iactive = False

    # king (D4) neighbor lookup
    dr = (0, -1, 1, 0)
    dc = (-1, 0, 0, 1)

    for istack in stack:
        irec = receivers[istack]

        # new basin
        if irec == istack:
            ibasin = basins[istack]
            iactive = active_nodes[istack]

            for iused in conn_pos_used[:conn_pos_used_size]:
                conn_pos[iused] = -1
            conn_pos_used_size = 0

            if not iactive:
                if basin0 == -1:
                    basin0 = ibasin
                else:
                    conn_basins[iconn] = (basin0, ibasin)
                    conn_nodes[iconn] = (-1, -1)
                    conn_weights[iconn] = -np.inf
                    iconn += 1

        if iactive:
            r = istack // nx
            c = istack % nx

            for k in range(4):
                kr = r + dr[k]
                kc = c + dc[k]

                if kr < 0 or kr >= ny or kc < 0 or kc >= nx:
                    continue

                ineighbor = numba.intp(kr * nx + kc)
                ineighbor_basin = basins[ineighbor]
                ineighbor_outlet = outlets[ineighbor_basin]

                # skip same basin or already connected adjacent basin
                # don't skip adjacent basin if it's an open basin
                if ibasin >= ineighbor_basin and active_nodes[ineighbor_outlet]:
                    continue

                weight = max(elevation[istack], elevation[ineighbor])
                conn_idx = conn_pos[ineighbor_basin]

                # add new connection
                if conn_idx == -1:
                    conn_basins[iconn] = (ibasin, ineighbor_basin)
                    conn_nodes[iconn] = (istack, ineighbor)
                    conn_weights[iconn] = weight

                    conn_pos[ineighbor_basin] = iconn
                    iconn += 1

                    conn_pos_used[conn_pos_used_size] = ineighbor_basin
                    conn_pos_used_size += 1

                # update existing connection
                elif weight < conn_weights[conn_idx]:
                    conn_nodes[conn_idx] = (istack, ineighbor)
                    conn_weights[conn_idx] = weight

    nconn = iconn

    return nconn, basin0


@numba.njit
def _compute_mst_linear(conn_basins, conn_weights, nbasins):
    """Compute the minimum spanning tree of the (undirected) basin graph.

    The method used here is an efficient ~ O(m) algorithm, where `m`
    is the number of edges in the graph. This algorithm, adapted from
    Boruvka's algorithm, is valid only for planar graphs.

    See for reference:

    - Mares. M., 2004. Two linear time algorithms for MST on minor
      closed graph classes. Archivum Mathematicum, 40 (3), 315-320.

    """
    g = Graph(conn_basins, conn_weights, nbasins)
    return g.get_min_span_tree()


@numba.njit
def _compute_mst_kruskal(conn_basins, conn_weights, nbasins):
    """Compute the minimum spanning tree of the (undirected) basin graph.

    The method used here is Kruskal's algorithm. Applied to a fully
    connected graph, the complexity of the algorithm is O(m log m)
    where `m` is the number of edges.

    """
    mstree = np.empty(nbasins - 1, np.intp)
    mstree_size = 0

    # sort edges
    sort_id = np.argsort(conn_weights)

    uf = UnionFind(nbasins)

    for eid in sort_id:
        b0 = conn_basins[eid, 0]
        b1 = conn_basins[eid, 1]

        if uf.find(b0) != uf.find(b1):
            mstree[mstree_size] = eid
            mstree_size += 1
            uf.union(b0, b1)

    return mstree


@numba.njit
def _orient_basin_tree(conn_basins, conn_nodes, nbasins, basin0, tree):
    """Orient the graph (tree) of basins so that the edges are directed in
    the inverse of the flow direction.

    If needed, swap values given for each edges (row) in `conn_basins`
    and `conn_nodes`.

    """

    # nodes connections
    nodes_connects_size = np.zeros(nbasins, np.intp)
    nodes_connects_ptr = np.empty(nbasins, np.intp)

    # parse the edges to compute the number of edges per node
    for i in tree:
        nodes_connects_size[conn_basins[i, 0]] += 1
        nodes_connects_size[conn_basins[i, 1]] += 1

    # compute the id of first edge in adjacency table
    nodes_connects_ptr[0] = 0
    for i in range(1, nbasins):
        nodes_connects_ptr[i] = (nodes_connects_ptr[i - 1] +
                                 nodes_connects_size[i - 1])
        nodes_connects_size[i - 1] = 0

    # create the adjacency table
    nodes_adjacency_size = nodes_connects_ptr[-1] + nodes_connects_size[-1]
    nodes_connects_size[-1] = 0
    nodes_adjacency = np.zeros(nodes_adjacency_size, np.intp)

    # parse the edges to update the adjacency
    for i in tree:
        n1 = conn_basins[i, 0]
        n2 = conn_basins[i, 1]
        nodes_adjacency[nodes_connects_ptr[n1] + nodes_connects_size[n1]] = i
        nodes_adjacency[nodes_connects_ptr[n2] + nodes_connects_size[n2]] = i
        nodes_connects_size[n1] += 1
        nodes_connects_size[n2] += 1

    # depth-first parse of the tree, starting from basin0
    # stack of node, parent
    stack = np.empty((nbasins, 2), np.intp)
    stack_size = 1
    stack[0] = (basin0, basin0)

    while stack_size > 0:
        # get parsed node
        stack_size -= 1
        node = stack[stack_size, 0]
        parent = stack[stack_size, 1]

        # for each edge of the graph
        for i in range(nodes_connects_ptr[node],
                       nodes_connects_ptr[node] + nodes_connects_size[node]):
            edge_id = nodes_adjacency[i]

            # the edge comming from the parent node has already been updated.
            # in this case, the edge is (parent, node)
            if conn_basins[edge_id, 0] == parent and node != parent:
                continue

            # we want the edge to be (node, next)
            # we check if the first node of the edge is not "node"
            if(node != conn_basins[edge_id, 0]):
                # swap n1 and n2
                conn_basins[edge_id, 0], conn_basins[edge_id, 1] = (
                    conn_basins[edge_id, 1], conn_basins[edge_id, 0])
                # swap p1 and p2
                conn_nodes[edge_id, 0], conn_nodes[edge_id, 1] = (
                    conn_nodes[edge_id, 1], conn_nodes[edge_id, 0])

            # add the opposite node to the stack
            stack[stack_size] = (conn_basins[edge_id, 1], node)
            stack_size += 1


@numba.njit
def _update_pits_receivers(receivers, dist2receivers, outlets,
                           conn_basins, conn_nodes, mstree,
                           elevation, nx, dx, dy):
    """Update receivers of pit nodes (and possibly lowest pass nodes)
    based on basin connectivity.

    Distances to receivers are also updated. An infinite distance is
    arbitrarily assigned to pit nodes.

    A minimum spanning tree of the basin graph is used here. Edges of
    the graph are also assumed to be oriented in the inverse of flow direction.

    """
    for i in mstree:
        node_to = conn_nodes[i, 0]
        node_from = conn_nodes[i, 1]

        # skip open basins
        if node_from == -1:
            continue

        outlet_from = outlets[conn_basins[i, 1]]

        dist2receivers[outlet_from] = np.inf

        if elevation[node_from] < elevation[node_to]:
            receivers[outlet_from] = node_to
        else:
            receivers[outlet_from] = node_from
            receivers[node_from] = node_to

            # update distance based on king (4D) neighbor lookup
            if node_from % nx == node_to % nx:
                dist2receivers[node_from] = dx
            else:
                dist2receivers[node_from] = dy


def correct_flowrouting(receivers, dist2receivers, ndonors, donors,
                        stack, nbasins, basins, outlets,
                        active_nodes, elevation, nx, ny, dx, dy,
                        method='mst_linear'):
    """Ensure that no flow is captured in sinks.

    If needed, update `receivers`, `dist2receivers`, `ndonors`,
    `donors` and `stack`.

    """
    nnodes = nx * ny

    # theory of planar graph -> max nb. of connections known
    nconn_max = nbasins * 3

    conn_basins = np.empty((nconn_max, 2), dtype=np.intp)
    conn_nodes = np.empty((nconn_max, 2), dtype=np.intp)
    conn_weights = np.empty(nconn_max, dtype=np.float64)

    nconn, basin0 = _connect_basins(
        conn_basins, conn_nodes, conn_weights,
        nbasins, basins, outlets, receivers, stack,
        active_nodes, elevation, nx, ny)

    conn_basins = np.resize(conn_basins, (nconn, 2))
    conn_nodes = np.resize(conn_nodes, (nconn, 2))
    conn_weights = np.resize(conn_weights, nconn)

    if method == 'mst_linear':
        mstree = _compute_mst_linear(conn_basins, conn_weights, nbasins)
    elif method == 'mst_kruskal':
        mstree = _compute_mst_kruskal(conn_basins, conn_weights, nbasins)
    else:
        raise ValueError("invalid flow correction method %r" % method)

    _orient_basin_tree(conn_basins, conn_nodes, nbasins, basin0, mstree)
    _update_pits_receivers(receivers, dist2receivers, outlets,
                           conn_basins, conn_nodes,
                           mstree, elevation, nx, dx, dy)
    compute_donors(ndonors, donors, receivers, nnodes)
    compute_stack(stack, ndonors, donors, receivers, nnodes)
