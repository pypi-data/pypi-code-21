from logilab.common.shellutils import ProgressBar

from cubes.datacat import cwsource_pull_data, vocabularies


vocabularies.media_types_import(cnx)
commit(ask_confirm=False)

# Add SKOS sources and trigger synchronization
sources = [vocabularies.add_source(cnx, name, url)
           for name, url in vocabularies.DCAT_SCHEMES]
commit(ask_confirm=False)
adms_source_eid = cnx.find('CWSource', url=u'https://joinup.ec.europa.eu/svn/adms/ADMS_v1.00/'
                           u'ADMS_SKOS_v1.00.rdf').one().eid
# Set correct source on concept schemes
sql("UPDATE cw_source_relation SET eid_to={0} WHERE eid_from IN ("
    "SELECT cw_eid FROM cw_conceptscheme WHERE cw_cwuri LIKE 'http://purl.org/adms/%'"
    ")".format(adms_source_eid))
# Set correct source on concepts
sql("UPDATE cw_source_relation SET eid_to={0} WHERE eid_from IN ("
    "SELECT eid_from FROM in_scheme_relation "
    "JOIN cw_conceptscheme ON eid_to = cw_eid WHERE cw_cwuri LIKE 'http://purl.org/adms/%'"
    ")".format(adms_source_eid))
# Set correct source on labels
sql("UPDATE cw_source_relation SET eid_to={0} WHERE eid_from IN ("
    "SELECT cw_label.cw_eid FROM cw_label "
    "JOIN in_scheme_relation ON cw_label.cw_label_of = in_scheme_relation.eid_from "
    "JOIN cw_conceptscheme ON in_scheme_relation.eid_to = cw_conceptscheme.cw_eid "
    "WHERE cw_conceptscheme.cw_cwuri LIKE 'http://purl.org/adms/%'"
    ")".format(adms_source_eid))
commit(ask_confirm=False)
pb = ProgressBar(len(sources), title='synchronizing SKOS sources')
for src in sources:
    cwsource_pull_data(repo, src.through_cw_source[0].eid)
    pb.update()
print('')

# Try to move format attribute into distribution_format relation for distributions
add_relation_type('distribution_media_type')
add_relation_type('distribution_format')
formats = dict(rql('Any LOWER(LL),C WHERE C is Concept, C in_scheme S, S cwuri %(source)s, '
                   'L label_of C, L kind "preferred", L label LL',
                   {'source': 'http://publications.europa.eu/resource/authority/file-type'}))
mediatypes = dict(rql('Any LOWER(LL),C WHERE C is Concept, C in_scheme S, S cwuri %(source)s, '
                      'L label_of C, L kind "preferred", L label LL',
                      {'source': 'http://www.iana.org/assignments/media-types/media-types.xml'}))
rset = rql('Any LOWER(F),D WHERE D is Distribution, D format F')
for format_, dist in rset:
    concept = mediatypes.get(format_)
    if concept is not None:
        rql('Set D distribution_media_type C WHERE D eid %(dist)s, C eid %(concept)s',
            {'dist': dist, 'concept': concept})
    concept = formats.get(format_)
    if concept is not None:  # XXX: value is lost if cannot find matching concept
        rql('Set D distribution_format C WHERE D eid %(dist)s, C eid %(concept)s',
            {'dist': dist, 'concept': concept})
commit()
drop_attribute('Distribution', 'format')

add_relation_definition('DataCatalog', 'language', 'Concept')

# Some relations are now mandatory: fill them with default values
for cat in rql('Any CAT WHERE CAT is DataCatalog, CAT title NULL').entities():
    cat.cw_set(title=u'<not specified>')
for cat in rql('Any CAT WHERE CAT is DataCatalog, CAT description NULL').entities():
    cat.cw_set(description=u'<not specified>')
for ds in rql('Any DS WHERE DS is Dataset, DS description NULL').entities():
    ds.cw_set(description=u'<not specified>')
sync_schema_props_perms()

# New attributes for LicenseDocument
add_attribute('LicenseDocument', 'title')
add_attribute('LicenseDocument', 'uri')

create_entity('Agent', name=u'admin')
rql('SET C catalog_publisher A WHERE A name "admin", NOT C catalog_publisher P')
commit(ask_confirm=False)
sync_schema_props_perms('catalog_publisher')

for etype in ('DataCatalog', 'Dataset', 'Distribution'):
    change_attribute_type(etype, 'issued', 'TZDatetime', ask_confirm=False)
    change_attribute_type(etype, 'modified', 'TZDatetime', ask_confirm=False)
sync_schema_props_perms('issued')
sync_schema_props_perms('modified')

add_cube('relationwidget')
