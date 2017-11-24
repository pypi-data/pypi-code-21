from Acquisition import aq_inner
from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName


class LastVideos(BrowserView):

    VIDEO_TYPES = ['Video']
    FOLDER_TYPES = ['Folder']

    def __call__(self):
        """
        return a dict: {'last_video': last video in the context,
                        'from_each':  a dict with 3 videos for each section,
                        }
        
        """

        return {'last_video': self.getLastVideo(),
                'from_sections': self.getLastVideosFromSections(),
                }

    def getLastVideo(self, section=None, limit=1):
        context = aq_inner(self.context)
        if section is not None:
            context_path = section
        else:
            context_path = context.getPhysicalPath()
            
        pcal = getToolByName(context, 'portal_catalog')
        brains = pcal(portal_type=self.VIDEO_TYPES,
                      path = '/'.join(context_path),
                      sort_on='created',
                      sort_order='reverse',
                      sort_limit=limit,
                      )
        
        return [b.getObject() for b in brains]

    def getLastVideosFromSections(self):
        context = aq_inner(self.context)

        sections = context.bideoak.getFolderContents({'portal_type': self.FOLDER_TYPES}, full_objects=True)

        for section in sections:
            yield {'section': {'Title': section.Title(),
                               'id': section.id,
                               'absolute_url': section.absolute_url(),
                               'Description': section.Description(),
                               },
                   'videos': self.getLastVideo(section=section.getPhysicalPath(), limit=3),
                  }
    
