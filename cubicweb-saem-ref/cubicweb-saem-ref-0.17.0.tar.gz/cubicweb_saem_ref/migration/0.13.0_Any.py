from cubicweb_seda.dataimport import LCSV_FILES
from cubicweb_saem_ref import workflows

for etype in ('SEDAProfile', 'ProfileDocument', 'ProfileArchiveObject'):
    rql('DELETE %s X' % etype)
    commit()

for etype in schema.entities():
    if etype.type.startswith('SEDA') or etype.type in ('ProfileDocument', 'ProfileArchiveObject'):
        drop_entity_type(str(etype))

# delete preexisting concept schemes with the same name: they have been refactored in seda cube
# (added seda 1/seda 2 labels, etc)
for data_descr in LCSV_FILES:
    title = data_descr[0]
    rset = cnx.find('ConceptScheme', title=title)
    if rset:
        rset.one().cw_delete()
        commit()

add_cube('seda')

workflows.define_publication_workflow(add_workflow, 'SEDAArchiveTransfer')

add_cube('eac')
