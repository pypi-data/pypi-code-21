# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-datacat postcreate script, executed at instance creation time or when
the cube is added to an existing instance.
"""

from cubes.datacat import cwsource_pull_data, vocabularies


TEST_MODE = config.mode == 'test'

print('-> creating SKOS sources')
for name, url in vocabularies.DCAT_SCHEMES:
    print('   ', name)
    vocabularies.add_source(cnx, name, url)
commit(ask_confirm=False)
if not TEST_MODE:
    print('{0} SKOS sources created, synchronize using "cubicweb-ctl '
          ' sync-schemes <instance>" command'.format(
              len(vocabularies.DCAT_SCHEMES)))
    print('-> importing IANA Media Types')
    vocabularies.media_types_import(cnx)
    commit(ask_confirm=False)

print('-> creating Eurovoc Source')
source = cnx.create_entity('CWSource', name=u'Eurovoc', url=vocabularies.EUROVOC_URI,
                           type=u'datafeed', parser=u'rdf.skos.zip',  # XXX parser does not exists
                           config=u'synchronize=no\nuse-cwuri-as-url=no')
commit(ask_confirm=False)
