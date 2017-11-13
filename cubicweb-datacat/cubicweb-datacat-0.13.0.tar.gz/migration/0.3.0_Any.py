# New entity Catalog
add_entity_type('DataCatalog')
# More properties on Dataset and Distribution
add_attribute('Dataset', 'issued')
add_attribute('Dataset', 'modified')
rql('SET X title T WHERE X is Dataset, X title NULL, X identifier T')
commit()
sync_schema_props_perms('Dataset')
add_attribute('Distribution', 'title')
add_attribute('Distribution', 'issued')
add_attribute('Distribution', 'modified')
add_attribute('Distribution', 'download_url')
sync_schema_props_perms('Distribution')
# Rename relation between Dataset and Distribution
# Also invert subject and object
add_relation_type('of_dataset')
rql('Set Y of_dataset X WHERE X dataset_distribution Y, X is Dataset, Y is Distribution')
commit()
drop_relation_type('dataset_distribution')

for etype in ('DataTransformationProcess', 'DataValidationProcess'):
    sync_schema_props_perms(etype)
    drop_attribute(etype, 'description')
    drop_attribute(etype, 'description_format')

rename_attribute('ResourceFeed', 'uri', 'url')
add_attribute('ResourceFeed', 'title')
sync_schema_props_perms('ResourceFeed')

add_relation_type('resourcefeed_distribution')
for resourcefeed in find_entities('ResourceFeed'):
    create_entity('Distribution', format=resourcefeed.data_format,
                  reverse_resourcefeed_distribution=resourcefeed,
                  of_dataset=resourcefeed.resource_feed_of[0])
    commit()

add_relation_type('file_distribution')
for f in rql('Any F WHERE EXISTS(F resource_of D)').entities():
    sourceinfo = f.cw_metainformation()['source']
    if sourceinfo['type'] == 'datafeed':
        # Relate file produced by a ResourceFeed to the associated
        # distribution.
        uri = sourceinfo['uri']
        source_eid = repo.sources_by_uri[uri].eid
        rql('SET F file_distribution D WHERE'
            ' RS resource_feed_source S, RS resourcefeed_distribution D,'
            ' S eid %(seid)s, F eid %(feid)s',
            {'seid': source_eid, 'feid': f.eid})
    else:
        # If the file is not from datafeed, create a distribution of it.
        create_entity('Distribution', title=f.title, format=f.data_format,
                      description=f.description,
                      description_format=f.description_format,
                      reverse_file_distribution=f, of_dataset=f.resource_of)
    commit()

drop_relation_type('resource_of')
sync_schema_props_perms('File', syncprops=False)
