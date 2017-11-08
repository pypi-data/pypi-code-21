""" Interfaces
"""
from zope.interface import Interface
from zope import schema
from eea.alchemy.controlpanel import schema as customschema
from eea.alchemy.config import EEAMessageFactory as _

class IAlchemySettings(Interface):
    """ Alchemy settings
    """
    token = schema.TextLine(
        title=_(u"Token"),
        description=_(u"Provide token from "
                      "http://www.alchemyapi.com/api/register.html"),
        required=False,
        default=u""
    )

    autoTagging = schema.Bool(
        title=_(u'Enable auto-tagging'),
        description=_(u"Hyperlink tags within page body"),
        required=False,
        default=False
    )

    onlyExistingKeywords = schema.Bool(
        title=_(u'Discover only existing keywords'),
        description=_(u"Discover keywords that already exists "
                      "in the existing keywords list"
                      "(Token is not required)"),
        required=False,
        default=False
    )

    modalDisplay = schema.Bool(
        title=_(u'Display results in modal window'),
        description=_(u"Display results in modal window"),
        required=False,
        default=False
    )

    autoTaggingFirstOnly = schema.Bool(
        title=_(u'Auto-tagging mark only first occurrence'),
        description=_(u"Hyperlink only the first occurence of a tag "
                      "wihin page body"),
        required=False,
        default=True
    )

    autoTaggingTable = customschema.Table(
        title=_(u"Auto-tagging mapping table (field, link)"),
        description=_("Define pairs of 'schema field' where to lookup tags "
                      "and the link where these tags should point, usually "
                      "a search page. (e.g. "
                      "'subject -> @@search?Subject=' or "
                      "'location -> @@search?getLocation=')"),
        required=False,
        value_type=customschema.TableRow()
    )

    autoTaggingBlackList = schema.List(
        title=_(u'Auto-tagging blacklist'),
        description=_(u"Do not apply auto-tagging if the tag is a child of the "
                      "following HTML elements. "
                      "(use CSS3 selectors like: div.documentByLine) "
                      "By default auto-tagging will not be applied on text "
                      "that is already a child of an <a> HTML tag"),
        required=False,
        default=[u"h1", u"h2", u"h3"],
        value_type=schema.TextLine()
    )

    autoTaggingDelimiter = schema.TextLine(
        title=_(u"Auto-tagging delimiter"),
        description=_(u"If the schema fields define above are of type text "
                      "(not iterable) use this delimiter to split tags. "
                      "If left empty the entire content of the field will be "
                      "considered one tag"),
        required=False,
        default=u","
    )

    autoRelations = schema.Bool(
        title=_(u'Enable auto-relations'),
        description=_(u"Lookup internal links within object content and "
                      "automatically update related items"),
        required=False,
        default=False
    )

    autoRelationsFields = schema.List(
        title=_(u"Auto-relations fields"),
        description=_(u"Lookup these fields for internal links"),
        required=False,
        default=[u'text', u'body'],
        value_type=schema.TextLine()
    )
