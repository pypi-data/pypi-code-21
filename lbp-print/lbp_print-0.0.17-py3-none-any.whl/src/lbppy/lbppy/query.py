from SPARQLWrapper import SPARQLWrapper, JSON

class Query():
    def __init__(self):
        self.description = "I am a query object"

    def query(self, url):
        new_url = "<" + url + ">"
        sparql = SPARQLWrapper("http://sparql-staging.scta.info/ds/query")
        sparql.setQuery("""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX sctap: <http://scta.info/property/>
            PREFIX sctar: <http://scta.info/resource/>
            SELECT ?p ?o
            WHERE { %s ?p ?o }
        """ % (new_url))
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results
