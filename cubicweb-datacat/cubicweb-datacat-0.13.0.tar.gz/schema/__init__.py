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

"""cubicweb-datacat schema"""

from yams.buildobjs import (
    ComputedRelation,
    EntityType,
    Int,
    RelationDefinition,
    RichString,
    String,
    TZDatetime,
)
from yams import constraints
from cubicweb import _
from cubicweb.schema import (
    ERQLExpression,
    RQLConstraint,
    RQLVocabularyConstraint,
    RRQLExpression,
)

from cubes.file.schema import File
from cubes.skos.schema import SKOSSource
from cubes.dataprocessing import schema as dataprocessing


# Until https://www.cubicweb.org/ticket/12437063 gets done.
SKOSSource.__permissions__ = SKOSSource.__permissions__.copy()
SKOSSource.__permissions__['read'] = ('managers', 'users')


def publication_metadata(cls):
    """Class decorator that adds publication metadata to an entity type."""
    cls.add_relation(TZDatetime(description=_('publication date')),
                     name='issued')
    cls.add_relation(TZDatetime(description=_('modification date')),
                     name='modified')
    return cls


def in_scheme_constraint(*scheme_uris):
    qs = ' OR '.join('EXISTS(O in_scheme CS{0:d}, CS{0:d} cwuri "{1}")'.format(
        idx, uri) for idx, uri in enumerate(scheme_uris))
    return RQLVocabularyConstraint(qs)


class scheme_relation(RelationDefinition):
    """Special relation from a concept scheme to a relation type, that may be used to restrict
    possible concept of a particular relation without depending on the scheme's name or other weak
    mecanism.
    """
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': ('managers',),
                       'delete': ('managers',)}
    subject = 'ConceptScheme'
    object = 'CWRType'
    cardinality = '**'
    constraints = [
        RQLVocabularyConstraint('NOT EXISTS(C theme_taxonomy S)'),
        RQLVocabularyConstraint('O name "license_type"'),
    ]


class Agent(EntityType):
    name = String(required=True, fulltextindexed=True)
    email = String()
    description = _(
        'An agent (eg. person, group, software or physical artifact).')


class publisher_type(RelationDefinition):
    subject = 'Agent'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    description = _("type of publisher (if unspecified agent is not a publisher)")
    constraints = [
        in_scheme_constraint('http://purl.org/adms/publishertype/1.0'),
    ]


@publication_metadata
class DataCatalog(EntityType):
    """A data catalog is a curated collection of metadata about datasets."""
    title = String(required=True, fulltextindexed=True)
    description = RichString(fulltextindexed=True)
    homepage = String(description=_('URL to the catalog home page'))


class language(RelationDefinition):
    subject = 'DataCatalog'
    object = 'Concept'
    description = _('languages used in the catalog')
    constraints = [
        in_scheme_constraint('http://publications.europa.eu/resource/authority/language'),
    ]


class theme_taxonomy(RelationDefinition):
    subject = 'DataCatalog'
    object = 'ConceptScheme'
    description = _(
        'vocabulary or thesaurus containing a list of themes for datasets in this catalog')


class catalog_publisher(RelationDefinition):
    subject = 'DataCatalog'
    object = 'Agent'
    inlined = True
    cardinality = '?*'
    description = _(
        'agent responsible for making the catalog available')


class spatial_coverage(RelationDefinition):
    subject = ('DataCatalog', 'Dataset')
    object = 'Concept'
    cardinality = '**'
    description = _('a geographical area covered by the entity')
    constraints = [
        in_scheme_constraint(
            'http://publications.europa.eu/resource/authority/country',
            'http://publications.europa.eu/resource/authority/place',
            'http://publications.europa.eu/resource/authority/continent',
            'http://sws.geonames.org/',
        ),
    ]


@publication_metadata
class Dataset(EntityType):
    # DCAT attributes.
    identifier = String(fulltextindexed=True)
    title = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)
    keyword = String(fulltextindexed=True,
                     description=_(
                         'comma-separated list of keywords or tags describing the dataset'))
    landing_page = String(
        description=_('web page providing access to the dataset, its '
                      'distributions and/or additional information'))
    provenance = String(fulltextindexed=True,  # Not in DCAT-AP spec.
                        description=_('source from which this dataset has been produced or '
                                      'extracted'))


class dataset_frequency(RelationDefinition):
    subject = 'Dataset'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    description = _('frequency at which a dataset is updated')
    constraints = [
        in_scheme_constraint(
            'http://publications.europa.eu/resource/authority/frequency'),
    ]


class dataset_type(RelationDefinition):
    subject = 'Dataset'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    description = _('type of dataset')
    constraints = [
        RQLVocabularyConstraint(
            'O in_scheme CS, CS scheme_relation RT, RT name "dataset_type"'),
    ]


class in_catalog(RelationDefinition):
    subject = 'Dataset'
    object = 'DataCatalog'
    cardinality = '1*'
    inlined = True
    description = _('catalog to which the dataset belongs')


class of_dataset(RelationDefinition):
    subject = 'Distribution'
    object = 'Dataset'
    cardinality = '1*'
    composite = 'object'
    inlined = True
    description = _('dataset to which the distribution is related')


class dataset_contact_point(RelationDefinition):
    subject = 'Dataset'
    object = 'Agent'
    cardinality = '?*'
    description = _('contact information that can be used for flagging '
                    'errors in the dataset or sending comments')
    constraints = [RQLVocabularyConstraint('NOT EXISTS(O publisher_type T)')]


class dataset_publisher(RelationDefinition):
    subject = 'Dataset'
    object = 'Agent'
    cardinality = '?*'
    description = _('agent responsible for making the dataset available')
    constraints = [RQLVocabularyConstraint('S in_catalog C, C catalog_publisher O')]


class dataset_contributors(RelationDefinition):
    subject = 'Dataset'
    object = 'Agent'
    cardinality = '**'
    description = _("agent(s) contributing to the dataset's production")


class dcat_theme(RelationDefinition):
    subject = 'Dataset'
    object = 'Concept'
    constraints = [RQLConstraint('O in_scheme CS, S in_catalog C, C theme_taxonomy CS',
                                 msg=_("Theme must belong to a dataset's catalog vocabulary"))]


class license_type(RelationDefinition):
    subject = 'Concept'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    constraints = [
        RQLConstraint('S in_scheme CS, CS scheme_relation RT, RT name "license_type"',
                      msg=_('Only concepts in licenses scheme can have a license type')),
        in_scheme_constraint('http://purl.org/adms/licencetype/1.0'),
    ]


class license(RelationDefinition):
    subject = ('DataCatalog', 'Distribution')
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    composite = 'subject'
    description = _('the licence under which the entity is made available')
    constraints = [RQLVocabularyConstraint('O in_scheme CS, CS scheme_relation RT, '
                                           'RT name "license_type"')]


class catalog_license(ComputedRelation):
    rule = 'S of_dataset D, D in_catalog C, C license O'


class PeriodOfTime(EntityType):
    start = TZDatetime(
        description=_('start of the period'),
    )
    end = TZDatetime(
        description=_('end of the period'),
        constraints=[
            constraints.BoundaryConstraint(
                '>=', constraints.Attribute('start'),
                msg=_('end date must be greater than start date')),
        ],
    )


class temporal_coverage(RelationDefinition):
    subject = 'Dataset'
    object = 'PeriodOfTime'
    cardinality = '*1'
    composite = 'subject'
    description = _('the temporal period that the dataset covers')


@publication_metadata
class Distribution(EntityType):
    title = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)
    documentation = String(
        description=_('a page or document about this Distribution'))
    access_url = String(
        description=_('A URL that gives access to a distribution of the '
                      'dataset. The resource at the access URL may contain '
                      'information about how to get the dataset.')
    )
    download_url = String(
        description=_('URL to directly download the distribution. '
                      '(Usually unspecified if the distribution is associated '
                      'with a file in the catalog.)')
    )
    byte_size = Int()


class distribution_media_type(RelationDefinition):
    name = 'media_type'
    subject = 'Distribution'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    description = _('The media type of the distribution as defined in the official register of '
                    'media types managed by IANA')


class distribution_format(RelationDefinition):
    subject = 'Distribution'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    description = _('The file format of the distribution')


class file_distribution(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (RRQLExpression('U has_update_permission O'), ),
        'delete': (RRQLExpression('U has_update_permission O, '
                                  'NOT EXISTS(S produced_by R)'), ),
    }
    subject = 'File'
    object = 'Distribution'
    cardinality = '??'
    inlined = True
    composite = 'object'
    constraints = [
        RQLVocabularyConstraint('NOT EXISTS(SC implemented_by S)'),
    ]


class replaces(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (),
        'delete': (
            RRQLExpression(
                'U has_update_permission O, U has_update_permission S, '
                'NOT EXISTS(S produced_by P), NOT EXISTS(O produced_by P1)'),
        ),
    }
    subject = 'File'
    object = 'File'
    cardinality = '??'
    inlined = True
    composite = 'subject'
    constraints = [
        RQLConstraint('EXISTS(S file_distribution D)',
                      msg=_('replacement file must be related to a distribution')),
    ]


class ResourceFeed(EntityType):
    """A resource feed is associated to a dataset distribution. It regularly
    fetches files from the specified URL and attached them to this
    distribution.
    """
    __permissions__ = {
        'read': ('managers', ERQLExpression('X owned_by U')),
        'update': (
            'managers',
            ERQLExpression('X owned_by U,'
                           ' NOT EXISTS(X resourcefeed_distribution D, F file_distribution D)')),
        'delete': ('managers', ERQLExpression('X owned_by U')),
        'add': ('managers', 'users')
    }
    title = String(
        description=_('this title will be used to set the title '
                      'of the associated distribution'))
    url = String(required=True)
    processes_to_keep = Int(required=True, default=10,
                            description=_('number of processes data (logs) to keep'))
    versions_to_keep = Int(required=True, default=0,
                           description=_('number of file versions to keep'))
    __unique_toguether__ = [('url', 'resource_feed_of')]


class resourcefeed_media_type(RelationDefinition):
    name = 'media_type'
    subject = 'ResourceFeed'
    object = 'Concept'
    cardinality = '1*'
    inlined = True
    description = _('MIME type of files served by the resource feed.')


class resource_feed_of(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U has_update_permission O')),
        'delete': ('managers', RRQLExpression('U has_update_permission O')),
    }
    subject = 'ResourceFeed'
    object = 'Dataset'
    cardinality = '1*'
    composite = 'object'
    inlined = True


class resourcefeed_distribution(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (),
        'delete': (),
    }
    subject = 'ResourceFeed'
    object = 'Distribution'
    cardinality = '1*'
    inlined = True


class resource_feed_source(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (),
        'delete': (),
    }
    subject = 'ResourceFeed'
    object = 'CWSource'
    cardinality = '1?'
    inlined = True
    composite = 'subject'
    # TODO a constraint checking compatibility of data_format between resource
    # feeds sharing the same CWSource.


# Set File permissions:
#  * use `produced_by` relation to prevent modification of generated files
#  * use relative permissions on the Distribution which the file may be a resource
#    of
#  * bind the update permissions on the _Script which uses the File as
#    implementation if any
# XXX Overrides cubicweb-dataprocessing (but we have no obvious way to
# extend ERQLExpression, so...).
_update_file_perms = ('managers', ERQLExpression(
    'NOT EXISTS(X produced_by Y), '
    'NOT EXISTS(X file_distribution D1)'
    ' OR EXISTS(X file_distribution D, U has_update_permission D), '
    'NOT EXISTS(S1 implemented_by X)'
    ' OR EXISTS(S implemented_by X, U has_update_permission S)'
))
File.__permissions__ = File.__permissions__.copy()
File.__permissions__.update({'update': _update_file_perms,
                             'delete': _update_file_perms})


# Customization of dataprocessing for ResourceFeed

dataprocessing.TransformationScript.remove_relation('output_format')

# TransformationSequence is not exposed, restrict its permissions.
dataprocessing.TransformationSequence.__permissions__ = {
    'read': ('managers', 'users'),
    'add': (),
    'update': (),
    'delete': (),
}


class output_media_type(RelationDefinition):
    subject = 'TransformationScript'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    description = _('MIME type of data generated by the script (if unspecified, '
                    'the input file format will be used)')


class script_media_type(RelationDefinition):
    name = 'media_type'
    subject = ('ValidationScript', 'TransformationScript')
    object = 'Concept'
    cardinality = '1*'
    inlined = True
    description = _('MIME type of files handled by the script (use '
                    '"application/octet-stream" for a generic script)')


class _resourcefeed_script(RelationDefinition):
    __abstract__ = True
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users'),
        'delete': (RRQLExpression('U has_update_permission S'), )
    }
    subject = 'ResourceFeed'
    cardinality = '?*'
    inlined = True
    constraints = [
        RQLConstraint(
            'O media_type C, '
            '(L label_of C, L label "application/octet-stream") OR S media_type C',
            msg=_('script does not handle resource feed data format')),
    ]


class validation_script(_resourcefeed_script):
    description = u'a Script used to validated files from this resource'
    object = 'ValidationScript'


class transformation_script(_resourcefeed_script):
    description = u'a Script used to transform files from this resource'
    object = 'TransformationScript'


class process_for_resourcefeed(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U has_update_permission O')),
        'delete': ('managers', RRQLExpression('U has_update_permission O')),
    }
    subject = ('DataTransformationProcess', 'DataValidationProcess')
    object = 'ResourceFeed'
    cardinality = '1*'
    composite = 'object'


dataprocessing.process_depends_on.__permissions__ = {
    'read': ('managers', 'users', 'guests'),
    'add': ('managers', RRQLExpression(
        'NOT EXISTS(S process_for_resourcefeed RF1) '
        'OR (S process_for_resourcefeed RF, U has_update_permission RF)')),
    'delete': ('managers', RRQLExpression(
        'NOT EXISTS(S process_for_resourcefeed RF1) '
        'OR (S process_for_resourcefeed RF, U has_update_permission RF)')),
}


dataprocessing.process_depends_on.constraints = [
    RQLConstraint(
        'NOT EXISTS(S process_for_resourcefeed RF1,'
        '           S process_for_resourcefeed RF2) '
        'OR EXISTS(S process_for_resourcefeed RF,'
        '          O process_for_resourcefeed RF)',
        msg=_('dependency between data process must be within the same '
              'resource feed')),
]


dataprocessing.implemented_by.constraints = [
    RQLVocabularyConstraint(
        'NOT EXISTS(O file_distribution DI, DI of_dataset D)'),
]


dataprocessing.DataTransformationProcess.__permissions__['add'] = ()
dataprocessing.DataTransformationProcess.__permissions__['update'] = ()
dataprocessing.DataValidationProcess.__permissions__['add'] = ()
dataprocessing.DataValidationProcess.__permissions__['update'] = ()
