from ftw.addressblock import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IAddressblockDepartment(model.Schema):

    department = schema.TextLine(
        title=_(u'label_department', default=u'Department'),
        required=False,
        missing_value=u'',
    )
