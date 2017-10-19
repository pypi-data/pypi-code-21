
print 'create source for data.culture.fr'
create_entity('CWSource', name=u'data.culture.fr', type=u'datafeed', parser=u'rdf.skos',
              url=u'http://data.culture.fr/thesaurus/data/ark:/67717/Matiere?includeSchemes=true\n'
              'http://data.culture.fr/thesaurus/data/ark:/67717/T2?includeSchemes=true\n'
              'http://data.culture.fr/thesaurus/data/ark:/67717/T4?includeSchemes=true\n'
              'http://data.culture.fr/thesaurus/data/ark:/67717/T3?includeSchemes=true\n',
              config=u'synchronize=no\nuse-cwuri-as-url=no')
commit()

print 'importing data.culture.fr vocabularies (takes some time)'
with repo.internal_cnx() as cnx:
    dfsource = repo.sources_by_uri['data.culture.fr']
    stats = dfsource.pull_data(cnx, force=True, raise_on_error=True)
