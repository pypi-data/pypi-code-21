from ftw.addressblock import _
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.supermodel import model
from zope.interface import provider


@provider(IFormFieldProvider)
class IAddressblockMisc(model.Schema):

    form.fieldset(
        'misc',
        label=_(u'Miscellaneous'),
        fields=[
            'opening_hours',
            'accessibility',
        ]
    )

    opening_hours = RichText(
        title=_(u'label_opening_hours', default=u'Opening Hours'),
        required=False,
        default_mime_type='text/html',
        output_mime_type='text/x-html-safe',
        allowed_mime_types=('text/html',),
    )

    accessibility = RichText(
        title=_(u'label_accessibility', default=u'Accessibility'),
        required=False,
        default_mime_type='text/html',
        output_mime_type='text/x-html-safe',
        allowed_mime_types=('text/html',),
    )

