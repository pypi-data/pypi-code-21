from zope.interface import Interface


class IVideo(Interface):
    """An object referring to externally hosted FLV files"""


class IVideoFolder(Interface):
    """Marker interface for folders in which we want to have RSS feeds """


class IVideoFolderEnableness(Interface):
    def isVideoFolder():
        """ is a video folder? """

    def notisVideoFolder():
        """ is not restricted? """


class IPossibleVideoFolder(Interface):
    """ Marker interface for possible video folders """

