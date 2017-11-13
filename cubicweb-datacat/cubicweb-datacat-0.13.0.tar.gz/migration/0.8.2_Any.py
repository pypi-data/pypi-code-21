from cubes.datacat.vocabularies import capitalized_eurovoc_domain

sync_schema_props_perms('language')

# Keep only first letter of Eurovoc concept scheme titles uppercase
domains = cnx.execute('ConceptScheme CS WHERE CS cwuri LIKE "%%eurovoc.europa.eu%%"').entities()
for domain in domains:
    domain.cw_set(title=capitalized_eurovoc_domain(domain.title))
commit(ask_confirm=False)
