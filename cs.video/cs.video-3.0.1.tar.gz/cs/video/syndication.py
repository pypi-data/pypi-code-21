"""
Syndication module
"""
from zope.interface import implements

from Products.fatsyndication.adapters import BaseFeed, BaseFeedSource, BaseFeedEntry

from Products.basesyndication.interfaces import IFeedSource, IFeedEntry, IEnclosure

class VideoFeed(BaseFeed):
    """ Adapter for VideoFolder to IFeed """

    def getTitle(self):
        return self.context.Title()

class VideoFeedSource(BaseFeedSource):
    """ Adapter for VideoFolder to IFeedSource """
    implements(IFeedSource)

    VIDEO_TYPES = ['Video']

    def getFeedEntries(self, max_only=True):
        cf = {'portal_type': self.VIDEO_TYPES,
              'sort_on': 'created',
              'sort_order': 'reverse',
              'path': '/'.join(self.context.getPhysicalPath())}
        
        brains = self.context.getFolderContents(contentFilter=cf, full_objects=True)

        if max_only:
            num_of_entries = self.getMaxEntries()
            brains = self.context.getFolderContents(contentFilter=cf, full_objects=True)[:num_of_entries]
        else:
            brains = self.context.getFolderContents(contentFilter=cf, full_objects=True)

        return [IFeedEntry(brain) for brain in brains]
        


class VideoFeedEntry(BaseFeedEntry):
    implements(IFeedEntry)

    def getWebURL(self):
        return self.context.absolute_url()

    def getEnclosure(self):
        """See IFeedEntry
        """
        return IEnclosure(self.context)

    def getEffectiveDate(self):
        return self.context.created()

    def getBody(self):
        """See IFeedEntry
        """
        flash_tag = '''<embed src="%(flowplayer_url)s?config=%(data)s"
                              width="400"
                              height="320"
                              scale="noscale"
                              bgcolor="111111"
                              type="application/x-shockwave-flash"
                              allowFullScreen="true"
                              allowScriptAccess="always"
                              allowNetworking="all"
                              pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>'''
        data = """{embedded:true,baseURL:'%(base_url)s', useNativeFullScreen:true,initialScale:'scale',playList:[{type:'jpg',url:'%(image_url)s'},{'overlayId':'play',url:'%(video_url)s'}],autoBuffering:false,autoPlay:true}"""
        portal_url = self.context.portal_url()
        data = data % {'base_url': portal_url,
                       'image_url': '%s/image' % self.context.absolute_url(),
                       'video_url': self.context.getUrl(),
                       }
        import urllib
        return flash_tag % {'flowplayer_url': '%s/FlowPlayerDark.swf' % portal_url,
                            'data': urllib.quote(data),
                            }


                              

        

    def getDescription(self):

        return self.context.Description()

class VideoEnclosure:
    """ Adapter from Video to IEnclosure
    """
    implements(IEnclosure)

    def __init__(self, context):
        self.context = context
        

    def getURL(self):
        """See IEnclosure
        """
        return self.context.getUrl()

    def getLength(self):
        """See IEnclosure
        """
        # XXX
        return '200000'

    def __len__(self):
        """See IEnclosure
        """
        return self.getLength()

    def getMajorType(self):
        """See IEnclosure
        """
        return 'video'
    
    def getMinorType(self):
        """See IEnclosure
        """
        return 'x-flv'

    def getType(self):
        """See IEnclosure
        """
        return '/'.join((self.getMajorType(), self.getMinorType(),))

        
    def __nonzero__(self):
        
        return 1
