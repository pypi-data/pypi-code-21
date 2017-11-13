from logilab.common.shellutils import ProgressBar

from cubes.datacat import cwsource_pull_data, vocabularies

sync_schema_props_perms('resource_feed_source')
sync_schema_props_perms('replaces')

for etype in ('DataCatalog', 'Dataset'):
    for attrtype in ('title', 'description'):
        sync_schema_props_perms((etype, attrtype, 'String'), syncperms=False)
sync_schema_props_perms('catalog_publisher', syncperms=False)

add_attribute('Distribution', 'documentation')
add_attribute('ResourceFeed', 'versions_to_keep')
add_relation_type('dataset_type')

rql('DELETE File F WHERE NOT EXISTS(N replaces F),'
    '                    NOT EXISTS(S implemented_by F),'
    '                    NOT EXISTS(F file_distribution D),'
    '                    NOT EXISTS(P process_stderr F)')
add_entity_type('PeriodOfTime')

add_relation_type('spatial_coverage')

sources = [vocabularies.add_source(cnx, name, url)
           for name, url in vocabularies.DCAT_SCHEMES[-3:]]
commit(ask_confirm=False)
pb = ProgressBar(len(sources),
                 title='synchronizing %d new SKOS sources' % len(sources))
for src in sources:
    cwsource_pull_data(repo, src.through_cw_source[0].eid)
    pb.update()
print('')

add_cubes('leaflet')
add_cubes('postgis')
add_entity_type('Location')
