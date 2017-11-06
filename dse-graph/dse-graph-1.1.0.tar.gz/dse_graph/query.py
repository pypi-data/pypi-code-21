# Copyright 2017 DataStax, Inc.
#
# Licensed under the DataStax DSE Driver License;
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#
# http://www.datastax.com/terms/datastax-dse-driver-license-terms

import logging

from dse.graph import SimpleGraphStatement
from dse.cluster import EXEC_PROFILE_GRAPH_DEFAULT

from gremlin_python.process.graph_traversal import GraphTraversal
from gremlin_python.structure.io.graphson import GraphSONWriter

from dse_graph.serializers import serializers

log = logging.getLogger(__name__)

graphson_writer = GraphSONWriter(serializer_map=serializers)


def _query_from_traversal(traversal):
    """
    From a GraphTraversal, return a query string.

    :param traversal: The GraphTraversal object
    """
    try:
        query = graphson_writer.writeObject(traversal)
    except Exception:
        log.exception("Error preparing graphson traversal query:")
        raise

    return query
