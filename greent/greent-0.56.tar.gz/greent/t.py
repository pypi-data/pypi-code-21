import json
from pprint import pformat
from pprint import pprint
from greent.client import GraphQL
from collections import namedtuple
translator = GraphQL ("http://localhost:5000/graphql")

Translation = namedtuple ('Translation', [ 'thing', 'domain_a', 'domain_b' ])
translations = [
    Translation ("Imatinib", "http://chem2bio2rdf.org/drugbank/resource/Generic_Name", "http://chem2bio2rdf.org/uniprot/resource/gene"),
    Translation ("CDC25A",   "http://chem2bio2rdf.org/uniprot/resource/gene",          "http://chem2bio2rdf.org/kegg/resource/kegg_pathway"),
    Translation ("CACNA1A",  "http://chem2bio2rdf.org/uniprot/resource/gene",          "http://pharos.nih.gov/identiier/disease/name"),    
]

for translation in translations:
    result = translator.translate (
        thing=translation.thing,
        domain_a=translation.domain_a,
        domain_b=translation.domain_b)
    pprint ("{0} => {1}".format (translation.thing, pformat (result)))
