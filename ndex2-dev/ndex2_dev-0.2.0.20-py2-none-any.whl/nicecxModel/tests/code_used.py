
# coding: utf-8

ndex = __import__("ndex") # ndex code used is the one given in https://github.com/idekerlab/heat-diffusion

import requests
import json
import base64
import networkx as nx
from ndex.networkn import NdexGraph
from networkx.readwrite import json_graph

## Connect to NDEx in order to retrieve a network.
anon_ndex = ndex.client.Ndex("http://public.ndexbio.org")


# Here we grab the "NCI Pathway Interaction Database - Final Revision - Extended Binary SIF" from NDEx, using its UUID.  The NdexGraph object is an extension of the networkx objects, see https://networkx.github.io/ for all the things you can do with it
functional_graph = ndex.networkn.NdexGraph(server='http://public.ndexbio.org', uuid='c0e70804-d848-11e6-86b1-0ac135e8bacf')

nx_read_edgelist_graph = nx.read_edgelist("edge_list_network_adrian.txt")


cx_Cytpscapetransformed_graph = ndex.networkn.NdexGraph("cx_Cytpscapetransformed_network_adrian.cx")
cx_given = ndex.networkn.NdexGraph("my_network.cx")

nx_read_edgelist_graph.nodes()[0] # Return one node
nx_my_grnx_read_edgelist_graphaph = NdexGraph(nx_read_edgelist_graph) # Tranformed
nx_read_edgelist_graph.nodes() # Returns Nothing

# The previous code applies the same with the rest of the networks
# read from a file

my_graph, functional_graph, example_full, nx_my_graph # All are Ndex Objects


for node in nx_read_edgelist_graph:
    print node
    break
for node in cx_given:
    print node
    break
for node in nx_my_graph:
    print node
    break
# this three loops return nothing excepting if nx_read_edgelist_graph 
# is not transformed calling NdexGraph(), in that case it returns the 
# nodes

for node in functional_graph:
    print node
    break
# this loop returns the node ids

print nx_read_edgelist_graph.nodes()[0]
print nx_read_edgelist_graph.node[806]
print nx_read_edgelist_graph.edges()[0]

print nx_my_graph.nodes()[0]
print nx_my_graph.node[1]
print nx_my_graph.edges()[0]

print cx_given.nodes()[0]
print cx_given.node[806]
print cx_given.edges()[0]
# These give an out of index error

print functional_graph.nodes()[0]
print functional_graph.node[806]
print functional_graph.edges()[0]
# this print the first node id,
# the info inside the node of id = 806
# and finally a certain edge

# I hope this code gives u and idea of what it is my problem
# Thank you

