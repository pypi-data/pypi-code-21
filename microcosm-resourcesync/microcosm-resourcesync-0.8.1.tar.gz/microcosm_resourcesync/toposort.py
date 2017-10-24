"""
Topological sort.

"""
from collections import defaultdict


def toposorted(resources):
    """
    Perform a topological sort on the input resources.

    Resources are first sorted by type and id to generate a deterministic ordering and to group
    resouces of the same type together (which minimizes the number of write operations required
    when batching together writes of the same type).

    The topological sort uses Kahn's algorithm, which is a stable sort and will preserve this
    ordering; note that a DFS will produce a worst case ordering from the perspective of batching.

    """
    # sort resources first so we have a deterministic order of nodes with the same partial order
    resources = sorted(
        resources,
        key=lambda resource: (resource.type, resource.id),
    )

    # build incoming and outgoing edges
    nodes = {
        resource.uri
        for resource in resources
    }

    incoming = defaultdict(set)
    outgoing = defaultdict(set)
    for resource in resources:
        for parent in resource.parents:
            if parent not in nodes:
                # ignore references that lead outside of the current graph
                continue
            incoming[resource.uri].add(parent)
            outgoing[parent].add(resource.uri)

    results = []
    while resources:
        remaining = []
        for resource in resources:
            if incoming[resource.uri]:
                # node still has incoming edges
                remaining.append(resource)
                continue

            results.append(resource)
            for child in outgoing[resource.uri]:
                incoming[child].remove(resource.uri)

        if len(resources) == len(remaining):
            raise Exception("Cycle detected")
        resources = remaining

    return results
