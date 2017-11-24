"""Definition of the Video content type
"""

from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi
    
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from cs.video import videoMessageFactory as _
from cs.video.interfaces import IVideo
from cs.video.config import PROJECTNAME

from Products.validation import V_REQUIRED

VideoSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.TextField('url',
                    required=1,
                    searchable=0,
                    languageIndependent=True,
                    storage=atapi.AnnotationStorage(),
                    widget=atapi.StringWidget(label=_(u'URL'),
                                              description=_(u'Paste here the URL fo the flash video'),
                                              ),
                    ),

    atapi.BooleanField('panoramic',
                       required=0,
                       searchable=0,
                       default=False,
                       widget=atapi.BooleanWidget(label=_(u'Is panoramic?'),
                                                  description=_(u'Select if this video is in 16:9 format instead on 4:3'),
                                                  ),
                       ),
    

    atapi.ImageField('image',
                     required=1,
                     languageIndependent=True,
                     sizes= {'large'   : (768, 768),
                             'preview' : (400, 400),
                             'mini'    : (200, 200),
                             'thumb'   : (128, 128),
                             'tile'    :  (64, 64),
                             'icon'    :  (32, 32),
                             'listing' :  (16, 16),
                             },
                     widget=atapi.ImageWidget(label=_(u'Image'),
                                              validators = (('isNonEmptyFile', V_REQUIRED),),
                                              ),
                     ),



))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

VideoSchema['title'].storage = atapi.AnnotationStorage()
VideoSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(VideoSchema, moveDiscussion=False)

class Video(base.ATCTContent):
    """An object referring to externally hosted FLV files"""
    implements(IVideo)

    portal_type = "Video"
    schema = VideoSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    url = atapi.ATFieldProperty('url')

    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('image').tag(self, **kwargs)


atapi.registerType(Video, PROJECTNAME)
