from cubes.datacat import cwsource_pull_data
from cubes.datacat.vocabularies import add_source

sync_schema_props_perms('Dataset')
sync_schema_props_perms('dataset_contact_point')
sync_schema_props_perms('dataset_publisher')
sync_schema_props_perms('license_type')
sync_schema_props_perms('license')

# Since in_catalog in now mandatory, put orphan datasets into a default catalog
rset = rql('Agent A WHERE A name "admin"')  # Ensure there is a default publisher
if not rset:
    admin = cnx.create_entity('Agent', name=u'admin')
else:
    admin = rset.one()
cat = cnx.create_entity('DataCatalog', title=u'System Catalog',  # Create the default catalog
                        description=u'Default catalog for orphan datasets',
                        catalog_publisher=admin)
commit(ask_confirm=False)
rql('SET DSET in_catalog CAT WHERE NOT EXISTS(DSET in_catalog C), CAT eid %(cat_eid)s',
    {'cat_eid': cat.eid})
commit(ask_confirm=False)

# French translations
print('In order to have french translations, please synchronize again using '
      '"cubicweb-ctl sync-schemes <instance>" command')

# Synchronize licenses
print('-> creating SKOS source for licenses and importing licenses')
lic_skos_source = add_source(cnx, u'European Licences Named Authority List',
                             u'http://publications.europa.eu/mdr/resource/authority/'
                             u'licence/skos/licences-skos.rdf')
commit(ask_confirm=False)
cwsource_pull_data(repo, lic_skos_source.through_cw_source[0].eid)
print('')

add_relation_type('scheme_relation')
# Licenses are now concepts: convert LicenseDocument entities to Concept entities
lic_scheme = cnx.find('ConceptScheme',
                      cwuri=u'http://publications.europa.eu/resource/authority/licence').one()
rql('SET CS scheme_relation RT WHERE CS eid %(cs)s, RT name "license_type"',
    {'cs': lic_scheme.eid})
commit(ask_confirm=False)
uri2concept = dict(  # Build some mappings to match existing concepts
    rql('(Any U,C WHERE C in_scheme S, S eid %(scheme_eid)s, C cwuri U) UNION '
        '(Any U,C2 WHERE C2 in_scheme S, S eid %(scheme_eid)s, C2 exact_match C, C cwuri U)',
        {'scheme_eid': lic_scheme.eid})
)
title2concept = dict(
    rql('Any LL,C WHERE C in_scheme S, S eid %(scheme_eid)s, L label_of C, L label LL',
        {'scheme_eid': lic_scheme.eid})
)
add_relation_definition('DataCatalog', 'license', 'Concept')  # Actual migration
add_relation_definition('Distribution', 'license', 'Concept')
add_relation_definition('Concept', 'license_type', 'Concept')
for license in cnx.find('LicenseDocument').entities():
    # Look for existing concept: match URI first, then title
    lic_concept_eid = uri2concept.get(license.uri) or title2concept.get(license.title)
    if lic_concept_eid:
        rql('SET X license C WHERE X license L, C is Concept, L is LicenseDocument, '
            'C eid %(concept_eid)s, L eid %(license_eid)s',
            {'concept_eid': lic_concept_eid, 'license_eid': license.eid})
    else:  # No existing concept found, create a new one
        kwargs = {}
        if license.uri:
            kwargs['cwuri'] = license.uri
        if license.license_type:
            kwargs['license_type'] = license.license_type[0]
        lic_concept = cnx.create_entity('Concept', in_scheme=lic_scheme, **kwargs)
        cnx.create_entity('Label', label_of=lic_concept, label=license.title,
                          kind=u"preferred",
                          language_code=unicode(cnx.vreg.property_value('ui.language')))
        commit(ask_confirm=False)
        rql('SET X license C WHERE C is Concept, C eid %(concept_eid)s',
            {'concept_eid': lic_concept.eid})
        commit(ask_confirm=False)
drop_entity_type('LicenseDocument')
