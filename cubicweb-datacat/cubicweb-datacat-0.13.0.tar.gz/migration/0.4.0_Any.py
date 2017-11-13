# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""Migration instructions for target version 0.4.0."""

sync_schema_props_perms('Agent')

# New dependencies
add_cube('skos')

# New attributes
add_attribute('Distribution', 'byte_size')
add_attribute('Agent', 'dcat_type')
add_attribute('DataCatalog', 'homepage')
add_attribute('DataCatalog', 'license')

# New relations
add_relation_type('replaces')
add_relation_type('theme_taxonomy')
add_relation_type('dcat_theme')
add_relation_type('catalog_publisher')

sync_schema_props_perms('file_distribution')

# A distribution is now related to at most one file: the most recent one.
# So for each distribution, keep only the last file_distribution relation, drop the other ones, and
# and add replaces relation between files.
for dist_eid, in rql('Any D WHERE D is Distribution, EXISTS(F file_distribution D)'):
    rset = rql('Any F ORDERBY DATE DESC WHERE F file_distribution D, F creation_date DATE, '
               'D eid %(dist_eid)s', {'dist_eid': dist_eid})
    if len(rset) <= 1:
        continue
    newf_eid = rset.rows[0][0]
    for oldf_eid, in rset.rows[1:]:
        rql('DELETE F file_distribution D WHERE F eid %(f)s, D eid %(d)s',
            {'f': oldf_eid, 'd': dist_eid})
        rql('SET NEWF replaces OLDF WHERE NEWF eid %(n)s, OLDF eid %(o)s',
            {'n': newf_eid, 'o': oldf_eid})
        commit(ask_confirm=False)
        newf_eid = oldf_eid

add_cube('squareui')

add_relation_definition('File', 'produced_by', 'DataTransformationProcess')
add_relation_definition('File', 'validated_by', 'DataValidationProcess')
rql('SET F produced_by P WHERE P process_script S, F produced_by S')
commit()
rql('SET F validated_by P WHERE P process_script S, F validated_by S')
commit()
drop_relation_definition('File', 'produced_by', 'Script')
drop_relation_definition('File', 'validated_by', 'Script')
drop_relation_type('produced_from')
sync_schema_props_perms('validated_by')
sync_schema_props_perms('file_distribution')
sync_schema_props_perms('File')

sync_schema_props_perms('Script')
sync_schema_props_perms('process_input_file')
sync_schema_props_perms('validation_script')
sync_schema_props_perms('transformation_script')

for stype in ('validation', 'transformation'):
    for rf in rql('Any R,RF,SF WHERE R data_format RF, S accepted_format SF, NOT S accepted_format RF, '
                  'R {0}_script S'.format(stype)).entities():
        print('WARNING: conflicting format between resource feed '
              'and its {0} script: {0} / {0}'.format(stype))

commit()
