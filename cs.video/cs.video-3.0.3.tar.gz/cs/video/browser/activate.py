"""
Handle IVideoFolder activation
"""
from Acquisition import aq_inner
from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.Five.utilities.interfaces import IMarkerInterfaces

from cs.video import videoMessageFactory as _
from cs.video.interfaces import IVideoFolder, IVideoFolderEnableness

class VideoFolderHandler(BrowserView):
    def __call__(self, deactivate=0):
        context = aq_inner(self.context)
        marker_interfaces = IMarkerInterfaces(context)
        if not deactivate:
            marker_interfaces.update(add=[IVideoFolder], remove=[])
            message = _(u'Video Folder activated')
        else:
            marker_interfaces.update(add=[], remove=[IVideoFolder])
            message = _(u'Video Folder deactivated')

        context.plone_utils.addPortalMessage(message)
        return self.request.response.redirect(context.absolute_url())

class VideoFolderEnableness(BrowserView):
    implements(IVideoFolderEnableness)

    def isVideoFolder(self):
        """ is a video folder? """
        context = aq_inner(self.context)
        return IVideoFolder.providedBy(context)

    def notisVideoFolder(self):
        """ is not restricted? """
        return not self.isVideoFolder()
        
