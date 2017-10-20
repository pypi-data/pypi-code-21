from collections import defaultdict
import pronto
import requests
import os

class HumanPhenotypeOntology (object):
    def __init__(self):
        hpo_data = 'hpo.obo'
        if not os.path.exists (hpo_data):
            url = "http://purl.obolibrary.org/obo/hp.obo"
            print ("Downloading human phenotype ontology: {0}".format (url))
            r = requests.get(url, stream=True)
            with open(hpo_data, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
        print ("Loading human phenotype ontology")
        self.ont = pronto.Ontology (hpo_data)
        ''' print (ont.json) '''

    def get_term (self, term_id):
        return self.ont[term_id]
    

hpo = HumanPhenotypeOntology ()

term = hpo.get_term ('HP:0002099')

def dump_term (t):
    print (t)
    #print (t['def'])
    for c in t.rchildren ():
        print ("  child: {}".format (c))
        #print ("  child: {}".format (c['def']))
        dump_term (c)
    for r in t.relations:
        print ("relation: {}".format (r))
        
        
dump_term (term)

#print (do.doid_to_mesh ["DOID:2841"])
