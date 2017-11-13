from __future__ import print_function

raise AssertionError('0.7.2 migration is not (completely) implemented')

print('-> creating Eurovoc Source')
source = cnx.create_entity('CWSource', name=u'Eurovoc', url=vocabularies.EUROVOC_URI,
                           type=u'datafeed', parser=u'rdf.skos.zip',  # XXX parser does not exists
                           config=u'synchronize=no\nuse-cwuri-as-url=no')
commit(ask_confirm=False)

sync_schema_props_perms('ResourceFeed')

rename_relation_type('distribution_media_type', 'media_type')

add_relation_definition('ResourceFeed', 'media_type', 'Concept')

mtrql = 'Any X WHERE L label_of X, L label %(label)s'
unspecified_eid = rql(mtrql, {'label': u'application/octet-stream'})[0][0]
for rfeid, df in rql('Any R,F WHERE R is ResourceFeed, R data_format F'):
    rset = rql(mtrql, {'label': df})
    if rset:
        mtype_eid = rset[0][0]
    else:
        print('no matching media type concept for data format {0} of '
              'resource feed #{1}'.format(df, rfeid))
        mtype_eid = unspecified_eid
    rql('SET RF media_type C WHERE RF eid %(rf)s, C eid %(c)s',
        {'rf': rfeid, 'c': mtype_eid})
commit()

drop_attribute('ResourceFeed', 'data_format')

for file_ in rql('Any F WHERE F is File, F cw_source S, NOT S name "system"',
                 ask_confirm=False).entities():
    file_.cw_set(data_sha1hex=file_.compute_sha1hex())
commit(ask_confirm=False)

add_cube('dataprocessing')
sync_schema_props_perms('process_for_resourcefeed')

add_relation_type('output_media_type')
