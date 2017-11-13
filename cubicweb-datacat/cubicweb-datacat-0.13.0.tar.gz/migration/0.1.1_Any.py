from cubicweb import NoResultError

add_attribute('Dataset', 'ckan_organization')
# Move ckan_organization from Application to Dataset.
rql('SET X ckan_organization O '
    'WHERE X is Dataset, X application A, A ckan_organization O')
commit()
# Convert Application application_maintainer to Dataset contact_point.
rset = rql('Any X,U WHERE X application A, A application_maintainer U')
for dataset, user in zip(rset.entities(0), rset.entities(1)):
    dataset.cw_set(contact_point=user.dc_title())
commit()
drop_entity_type('Application')
sync_schema_props_perms('Dataset')

add_attribute('Dataset', 'landing_page')
add_attribute('Dataset', 'frequency')
add_attribute('Dataset', 'spatial_coverage')
add_attribute('Dataset', 'provenance')
add_attribute('Dataset', 'theme')

add_attribute('Agent', 'email')
sync_schema_props_perms('Agent')
add_relation_definition('Dataset', 'dataset_contact_point', 'Agent')
add_relation_definition('Dataset', 'dataset_contributors', 'Agent')

rset = rql('Any X,A WHERE NOT X contact_point NULL, X contact_point A')
for eid, name in rset.rows:
    try:
        cpoint = find_one_entity('Agent', name=name)
    except NoResultError:
        _ = create_entity('Agent', name=name,
                          reverse_dataset_contact_point=eid)
    else:
        cpoint.cw_set(reverse_dataset_contact_point=eid)
commit()
drop_attribute('Dataset', 'contact_point')

drop_attribute('Agent', 'publisher_type')
