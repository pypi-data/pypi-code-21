from ftw.addressblock import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.supermodel import model
from z3c.schema import email as emailfield
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IAddressblockCommunication(model.Schema):

    form.fieldset(
        'communication',
        label=_(u'Communication'),
        fields=[
            'phone',
            'fax',
            'show_email',
            'email',
            'www',
        ]
    )

    phone = schema.TextLine(
        title=_(u'label_phone', default=u'Phone'),
        required=False,
        missing_value=u'',
    )

    fax = schema.TextLine(
        title=_(u'label_fax', default=u'Fax'),
        required=False,
        missing_value=u'',
    )

    show_email = schema.Bool(
        title=_(u'label_show_email', default=u'Show email'),
        description=_(
            u'description_show_email',
            default=u'Defines if the email address should be shown on the '
                    u'detail view of the address block.'
        ),
        default=True,
        required=False,
    )

    email = emailfield.RFC822MailAddress(
        title=_(u'label_email', default=u'Email'),
        description=_(
            u'description_email',
            default=u'A link to the contact form will be shown in the '
                    u'block if an email address is entered.'
        ),
        required=False,
    )

    www = schema.URI(
        title=_(u'label_www', default=u'WWW'),
        required=False,
    )


