# coding: utf-8
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
"""cubicweb-saem-ref schema"""

from yams.buildobjs import EntityType, RelationDefinition, String, Int, ComputedRelation
from yams.constraints import UniqueConstraint

from cubicweb import _
from cubicweb.schema import (RO_ATTR_PERMS, ERQLExpression, RRQLExpression,
                             RQLConstraint, RQLVocabularyConstraint, WorkflowableEntityType,
                             make_workflowable)
from cubicweb.schemas.base import ExternalUri, EmailAddress

from cubes.skos.schema import ConceptScheme
from cubicweb_prov import schema as prov
from cubicweb_eac import schema as eac
from cubicweb_seda.schema import simplified_profile
from cubicweb_seda.schema.seda2 import SEDAArchiveTransfer
from cubicweb_compound import utils


def publication_permissions(cls, groups=('managers', 'users')):
    """Set __permissions__ of `cls` entity type class preventing modification
    when not in state "draft".
    """
    groups = ', '.join('"{}"'.format(group) for group in groups)
    cls.__permissions__ = cls.__permissions__.copy()
    cls.__permissions__['update'] = (
        ERQLExpression('U in_group G, G name IN ({}), '
                       'X in_state ST, ST name "draft"'.format(groups)),
    )
    cls.__permissions__['delete'] = (
        ERQLExpression('U in_group G, G name IN ({}), '
                       'X in_state ST, ST name "draft"'.format(groups)),
    )
    return cls


def authority_permissions_etype(cls):
    """Set __permissions__ of `cls` entity type class to ensure user can
    update/delete provided its authority is the same as the entity's authority.

    Creation permission is ensured by permission of the authority relation.
    """
    cls.__permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users'),
        'update': ('managers', ERQLExpression('U authority A, X authority A')),
        'delete': ('managers', ERQLExpression('U authority A, X authority A')),
    }
    return cls


def authority_permissions_rdef(cls):
    """Set __permissions__ of `cls` relation definition class to ensure user can
    create/delete provided its authority is the same as the relation subject's
    authority.
    """
    cls.__permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U authority A, S authority A')),
        'delete': ('managers', RRQLExpression('U authority A, S authority A')),
    }
    return cls


def groups_permissions(cls):
    """Set __permissions__ of `cls` entity type class preventing modification
    when user is not in managers or users group.
    """
    cls.__permissions__ = cls.__permissions__.copy()
    cls.__permissions__['update'] = (
        ERQLExpression('U in_group G, G name IN ("managers", "users")', 'U'),
    )
    return cls


# Disable "update" for ExternalUri as these should only come from imported data
# and are meant to only be created or deleted.
ExternalUri.__permissions__ = ExternalUri.__permissions__.copy()
ExternalUri.__permissions__['update'] = ()


# Customization of EmailAddress entity type.
EmailAddress.remove_relation('alias')


# Customization of eac schema.
make_workflowable(eac.AuthorityRecord)
groups_permissions(eac.AuthorityRecord)

eac.agent_kind.__permissions__ = {
    'read': ('managers', 'users', 'guests'),
    'add': ('managers', RRQLExpression('U has_update_permission S')),
    'delete': ('managers', RRQLExpression('U has_update_permission S')),
}
eac.agent_kind.constraints = [
    RQLConstraint('NOT EXISTS(Z authority_record S)'
                  ' OR '
                  'EXISTS(A authority_record S, A is Agent, '
                  '       O name "person")'
                  ' OR '
                  'EXISTS(OU authority_record S, OU is IN (Organization, OrganizationUnit), '
                  '       O name "authority")',
                  msg=_('This record is used by a relation forbidding to change its type')),
]

for etype_def in (eac.ChronologicalRelation,
                  eac.HierarchicalRelation,
                  eac.AssociationRelation):
    etype_def.__permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users'),
        'update': ('managers', 'users'),
        'delete': ('managers', 'users'),
    }


# Customization of skos schema.
make_workflowable(ConceptScheme)
publication_permissions(ConceptScheme, groups=('managers',))
ConceptScheme.__permissions__['add'] = ('managers',)


class Organization(EntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'update': ('managers', ),
        'delete': ('managers', ),
    }
    name = String(required=True, fulltextindexed=True, unique=True)


@authority_permissions_etype
class OrganizationUnit(WorkflowableEntityType):
    __unique_together__ = [('name', 'authority')]
    name = String(required=True, fulltextindexed=True)


@authority_permissions_etype
class Agent(WorkflowableEntityType):
    __unique_together__ = [('name', 'authority')]
    name = String(required=True, fulltextindexed=True)


class user_authority(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': (),
    }
    name = 'authority'
    subject = 'CWUser'
    object = 'Organization'
    cardinality = '?*'
    inlined = True
    constraints = [
        RQLConstraint('NOT EXISTS(A agent_user S) '
                      'OR EXISTS(B agent_user S, B authority O)'),
    ]


class others_authority(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U authority O'),),
        'delete': (),
    }
    name = 'authority'
    subject = ('OrganizationUnit', 'Agent')
    object = 'Organization'
    cardinality = '1*'
    composite = 'object'
    inlined = True


class agent_user(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': ('managers',),
    }
    subject = 'Agent'
    object = 'CWUser'
    cardinality = '??'
    inlined = True
    description = _('the application user related to this agent')
    constraints = [
        RQLConstraint('NOT EXISTS(O authority A) '
                      'OR EXISTS(O authority B, S authority B)'),
    ]


class _authority_record(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U has_update_permission S')),
        'delete': ('managers',),
    }
    name = 'authority_record'
    object = 'AuthorityRecord'
    cardinality = '??'
    inlined = True
    description = _('the authority record describing this agent')


class ou_authority_record(_authority_record):
    subject = 'OrganizationUnit'
    description = _('the authority record describing this organization unit')
    constraints = [
        RQLConstraint('O agent_kind K, K name "authority"'),
    ]


class o_authority_record(ou_authority_record):
    subject = 'Organization'
    description = _('the authority record describing this organization')


class agent_authority_record(_authority_record):
    subject = 'Agent'
    description = _('the authority record describing this agent')
    constraints = [
        RQLConstraint('O agent_kind K, K name "person"'),
    ]


class contact_point(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'Agent'
    cardinality = '?*'
    inlined = True
    constraints = [
        RQLConstraint('S authority A, O authority A'),
        RQLVocabularyConstraint('O in_state ST, ST name "published"'),
    ]
    description = _('set an agent as the contact point of an organization unit')


class archival_unit(RelationDefinition):
    subject = 'Organization'
    object = 'OrganizationUnit'
    cardinality = '?*'
    description = _("the archival unit responsible for dealing with the organization's "
                    "documents")
    constraints = [RQLConstraint('O archival_role AR, AR name "archival"'),
                   RQLVocabularyConstraint('O in_state ST, ST name "published"')]


class archival_authority(ComputedRelation):
    rule = 'S archival_unit OU, OU authority O'


class use_authorityrecord(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'AuthorityRecord'
    cardinality = '**'
    description = _("authority records used by this archival unit")
    constraints = [
        RQLConstraint('S archival_role AR, AR name "archival"'),
    ]


class ArchivalRole(EntityType):
    """An archival role determines the kind of action (e.g. deposit or control)
    an agent may perform on an archive entity.
    """
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'update': ('managers', ),
        'delete': ('managers', ),
    }
    name = String(required=True, unique=True, internationalizable=True)


class archival_role(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'ArchivalRole'
    cardinality = '**'
    description = _("the organization unit's archival role (producer, control, etc.)")


class use_email(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests',),
        'add': ('managers', RRQLExpression('U has_update_permission S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S'),),
    }
    subject = 'Agent'
    object = 'EmailAddress'
    cardinality = '*?'
    composite = 'subject'
    fulltext_container = 'subject'


class phone_number(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests',),
        'add': ('managers', RRQLExpression('U has_update_permission S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S'),),
    }
    subject = 'Agent'
    object = 'PhoneNumber'
    cardinality = '*1'
    composite = 'subject'


@authority_permissions_rdef
class related_concept_scheme(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'ConceptScheme'
    cardinality = '**'
    description = _('concept schemes used by the agent')


# PROV #########################################################################

# we have to let addition permission to managers/users but eac use them for user-land imports but
# empty permission would be better because those are expected to be set by hooks. We could probably
# change eac import to by-pass security for activities?

class generated(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (),
        'delete': (),
    }
    subject = 'Activity'
    object = ('Concept', 'ConceptScheme', 'SEDAArchiveTransfer')


class used(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (),
        'delete': (),
    }
    subject = 'Activity'
    object = ('Concept', 'ConceptScheme', 'SEDAArchiveTransfer')


class associated_with(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': (),
        'delete': (),
    }
    subject = 'Activity'
    object = 'CWUser'


prov.Activity.__permissions__ = {
    'read': ('managers', 'users', 'guests'),
    'add': ('managers', 'users'),
    'update': (),
    'delete': (),
}

eac.used.__permissions__ = eac.generated.__permissions__ = {
    'read': ('managers', 'users', 'guests'),
    'add': (RRQLExpression('U has_update_permission O'),),
    'delete': (),
}


# ARK ##########################################################################

class ark(RelationDefinition):
    __permissions__ = RO_ATTR_PERMS
    subject = (
        'Agent',
        'AuthorityRecord',
        'Concept',
        'ConceptScheme',
        'Organization',
        'OrganizationUnit',
        'SEDAArchiveTransfer',
    )
    object = 'String'
    description = _('ARK Identifier - will be generated if not specified')
    constraints = [UniqueConstraint()]
    cardinality = '11'


class ArkNameAssigningAuthority(EntityType):
    """Name Assigning Authority (NAA) for ARK generation."""
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'update': ('managers', ),
        'delete': ('managers', ),
    }
    who = String(required=True, unique=True,
                 description=_('official organization name'))
    what = Int(required=True, unique=True,
               description=_('Name Assigning Authority Number (NAAN)'))


class _ark_naa(RelationDefinition):
    name = 'ark_naa'
    object = 'ArkNameAssigningAuthority'
    inlined = True


class organization_ark_naa(_ark_naa):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'delete': ('managers', ),
    }
    subject = 'Organization'
    cardinality = '?*'
    description = _("ARK identifier Name Assigning Authority (NAA) - "
                    "you'll need one to start creating objects")


class mandatory_ark_naa(_ark_naa):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users',),
        'delete': (),
    }
    subject = ('AuthorityRecord', 'SEDAArchiveTransfer')
    cardinality = '1*'
    description = _("ARK identifier Name Assigning Authority (NAA)")


class optional_ark_naa(_ark_naa):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users',),
        'delete': (),
    }
    subject = ('ConceptScheme', 'SKOSSource')
    cardinality = '?*'
    description = _("ARK identifier Name Assigning Authority (NAA), "
                    "necessary to create ARK for concepts which don't have one yet.")


# SEDA #######################################################################

make_workflowable(SEDAArchiveTransfer)
publication_permissions(SEDAArchiveTransfer)


simplified_profile.default = True


@authority_permissions_rdef
class use_profile(RelationDefinition):
    subject = 'OrganizationUnit'
    object = 'SEDAArchiveTransfer'
    cardinality = '**'
    constraints = [RQLConstraint('S archival_role R, R name "deposit"'),
                   RQLConstraint('O in_state ST, ST name "published"')]


class new_version_of(RelationDefinition):
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': ('managers', 'users',
                               RRQLExpression('O in_state ST, ST name "published"')),
                       'delete': ()}
    subject = 'SEDAArchiveTransfer'
    object = 'SEDAArchiveTransfer'
    cardinality = '??'
    inlined = True


def post_build_callback(schema):
    schema['simplified_profile'].rdefs['SEDAArchiveTransfer', 'Boolean'].default = True  # XXX
    from . import ConceptSchemeGraph
    graph = ConceptSchemeGraph(schema)
    utils.graph_set_etypes_update_permissions(schema, graph, 'ConceptScheme')
    utils.graph_set_write_rdefs_permissions(schema, graph, 'ConceptScheme')

    # permissions override
    schema['Label'].set_action_permissions('delete', ('managers', 'users'))
    for rtype in ('in_scheme', 'broader_concept', 'label_of'):
        for rdef in schema[rtype].rdefs.values():
            rdef.set_action_permissions('add', ('managers', 'users'))
            if rtype == 'label_of':
                rdef.set_action_permissions('delete', ('managers', 'users'))

    # reset permissions, unexpectedly changed by seda's post_build_callback
    def sync_perms(erdef, permissions):
        for action, permissions in permissions.items():
            erdef.set_action_permissions(action, permissions)

    sync_perms(schema['Activity'], prov.Activity.__permissions__)
    for rdef_def in (generated, used, associated_with):
        objtypes = rdef_def.object if isinstance(rdef_def.object, tuple) else (rdef_def.object,)
        for objtype in objtypes:
            rdef = schema[rdef_def.__name__].rdefs[(rdef_def.subject, objtype)]
            sync_perms(rdef, rdef_def.__permissions__)
