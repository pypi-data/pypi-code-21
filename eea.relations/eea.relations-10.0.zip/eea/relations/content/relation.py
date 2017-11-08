""" EEA Relation
"""
from zope.component import queryAdapter
from zope.interface import implements
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from eea.relations.content.interfaces import IToolAccessor, IRelation

class TitleWidget(atapi.StringWidget):
    """ Auto generate title
    """
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """ Process form
        """
        ct_from = form.get('from', '')
        ct_to = form.get('to', '')
        if not (ct_from and ct_to):
            return '', {}

        tool = queryAdapter(instance, IToolAccessor)
        brains = tool and tool.types(getId=ct_from)
        for brain in brains:
            ct_from = brain.Title
            break

        brains = tool.types(getId=ct_to)
        for brain in brains:
            ct_to = brain.Title
            break

        value = '%s -> %s' % (ct_from, ct_to)
        return value, {}

RelationSchema = atapi.Schema((
    atapi.StringField('from',
        schemata="default",
        vocabulary_factory='eea.relations.voc.ContentTypes',
        required=True,
        widget=atapi.SelectionWidget(
            format='select',
            label='From',
            label_msgid='widget_from_title',
            description='Select content-type',
            description_msgid='widget_from_description',
            i18n_domain="eea"
        )
    ),
    atapi.StringField('to',
        schemata="default",
        vocabulary_factory='eea.relations.voc.ContentTypes',
        required=True,
        widget=atapi.SelectionWidget(
            format='select',
            label='To',
            label_msgid='widget_to_title',
            description='Select content-type',
            description_msgid='widget_to_description',
            i18n_domain="eea"
        )
    ),
    atapi.StringField(
        name='title',
        required=0,
        searchable=1,
        accessor='Title',
        widget=TitleWidget(
            label_msgid='label_title',
            modes=(),
            i18n_domain='plone',
        ),
    ),
    atapi.StringField('forward_label',
        schemata="default",
        widget=atapi.StringWidget(
            size=50,
            label='Forward label',
            label_msgid='widget_forward_label_title',
            description='Label to be used for forward relations',
            description_msgid='widget_forward_label_description',
            i18n_domain="eea"
        )
    ),
    atapi.StringField('backward_label',
        schemata="default",
        widget=atapi.StringWidget(
            size=50,
            label='Backward label',
            label_msgid='widget_backward_label_title',
            description='Label to be used for backward relations',
            description_msgid='widget_forward_label_description',
            i18n_domain="eea"
        )
    ),
    atapi.TextField('description',
        schemata='default',
        searchable=1,
        accessor="Description",
        widget=atapi.TextAreaWidget(
            label='Description',
            description="A short summary of the content",
            label_msgid="label_description",
            description_msgid="help_description",
            i18n_domain="plone"
        )
    ),
    atapi.BooleanField('required',
        schemata='default',
        default=False,
        widget=atapi.BooleanWidget(
            label='Required',
            label_msgid='widget_required_title',
            description=('Select this if you want to make this relation '
                         'mandatory (action: edit)'),
            description_msgid='widget_required_description',
            i18n_domain="eea"
        )
    ),
    atapi.LinesField('required_for',
        schemata='default',
        vocabulary_factory='eea.relations.voc.workflowstates',
        widget=atapi.MultiSelectionWidget(
            format='checkbox',
            label='Required for',
            label_msgid='widget_required_for_title',
            description=('Select workflow states that will require this '
                         'relation before setup (action: change state). '
                         'You will also have to update workflow '
                         'transitions accordingly'),
            description_msgid='widget_required_for_description',
            i18n_domain="eea"
        )
    ),
))

EditSchema = ATFolder.schema.copy() + RelationSchema.copy()
EditSchema.moveField('title', after='to')
EditSchema.moveField('description', after='backward_label')

class EEAPossibleRelation(ATFolder):
    """ Relation
    """
    implements(IRelation)
    portal_type = meta_type = 'EEAPossibleRelation'
    archetypes_name = 'EEA Possible Relation'
    _at_rename_after_creation = True
    schema = EditSchema
