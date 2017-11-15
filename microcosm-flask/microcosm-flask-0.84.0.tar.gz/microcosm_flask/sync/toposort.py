"""
Topological sort.

"""
from collections import defaultdict
from logging import getLogger

TEMPORARY = object()
VISITED = object()


logger = getLogger("sync.toposort")


def iter_parents(resource):
    for relation, links in resource["_links"].items():
        if relation == "self" or relation.startswith("child:"):
            continue
        if isinstance(links, list):
            for link in links:
                yield link["href"]
        else:
            yield links["href"]


def toposorted(inputs):
    """
    Perform a topological sort on the input (href, resource) tuples.

    Uses a DFS.

    """
    sorted_items = []

    visited = {}

    nodes = {
        href: resource
        for href, resource in inputs
    }

    children = defaultdict(list)
    for href, resource in nodes.items():
        for parent_href in iter_parents(resource):
            children[parent_href].append(href)

    def visit(href, resource):
        if visited.get(href) == VISITED:
            return
        if visited.get(href) == TEMPORARY:
            raise Exception("Found cycle at {}".format(href))

        visited[href] = TEMPORARY
        for child_href in children[href]:
            visit(child_href, nodes[child_href])
        visited[href] = VISITED

        sorted_items.append((href, resource))

    logger.info("Toposorting {} resources".format(len(nodes)))

    for href, resource in nodes.items():
        visit(href, resource)

    return reversed(sorted_items)
