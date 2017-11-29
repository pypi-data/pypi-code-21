__author__ = 'aarongary'

import ndex2
import pronto
import os
import unittest
from nicecxModel.NiceCXNetwork import NiceCXNetwork

upload_server = 'dev.ndexbio.org'
upload_username = 'scratch'
upload_password = 'scratch'
here = os.path.dirname(__file__)

class TestPronto(unittest.TestCase):
    #@unittest.skip("Temporary skipping")
    def test_pronto_simple(self):
        test_helper = TestHelper()
        print("LOADING PSI-MOD...")
        ontology = pronto.Ontology("fix.obo")
        #ontology = pronto.Ontology("http://purl.obolibrary.org/obo/go/go-basic.obo")
        #clear_output()
        root = ontology['FIX:0000000']


        term_id_to_node_id_map = {}
        niceG = NiceCXNetwork()
        niceG.set_name("Food Web")
        fox_node = niceG.create_node(node_name='Fox')
        mouse_node = niceG.create_node(node_name='Mouse')

        print("adding nodes")
        # create all the nodes under root in ontology and add attributes, if any
        test_helper.add_nodes(root, niceG, term_map, term_id_to_node_id_map)

        print("added " + str(len(term_id_to_node_id_map)) + " nodes")
        print("network now has  " + str(len(G.nodes())) + " nodes")

        print("adding edges")
        add_edges(root, G, term_id_to_node_id_map)
        print("network now has  " + str(len(G.edges())) + " edges")
        return G




        #print(ontology.json)
        print("DONE!")


class TestHelper(object):
    def add_nodes(self, parent_term, network, term_map, term_id_to_node_id_map):

        # check to see if this term has already been added to the id->node_id map
        if parent_term.id in term_id_to_node_id_map:
            return

        # only traverse nodes in the term_map
        if parent_term.id not in term_map:
            return

        attributes = term_map[parent_term.id]

        # dont include this term if it has no propagated or directly annotated genes
        if "genes" not in attributes or len(attributes["genes"]) is 0:
            return

        att_dict = {}
        att_dict["represents"] = parent_term.id
        # prune empty lists from attributes
        for att in attributes:
            val = attributes[att]
            if not (type(val) is list and len(val) is 0):
                att_dict[att] = val
        node_id = network.add_new_node(parent_term.name, att_dict)
        term_id_to_node_id_map[parent_term.id] = node_id

        for child_term in parent_term.children:
            self.add_nodes(child_term, network, term_map, term_id_to_node_id_map)

    def add_edges(self, parent_term, network, term_id_to_node_id_map):
        if parent_term.id in term_id_to_node_id_map:
            parent_node_id = term_id_to_node_id_map.get(parent_term.id)
            for child_term in parent_term.children:
                if child_term.id in term_id_to_node_id_map:
                    child_node_id = term_id_to_node_id_map.get(child_term.id)
                    if child_node_id == parent_node_id:
                        print("self loop : " + parent_term.name)
                    else:
                        edge_count = network.number_of_edges(child_node_id, parent_node_id)
                        if edge_count is 0:
                            network.add_edge_between(child_node_id, parent_node_id, "hasParent")
                            # print child_term.name + " -> " + parent_term.name
                        self.add_edges(child_term, network, term_id_to_node_id_map)
