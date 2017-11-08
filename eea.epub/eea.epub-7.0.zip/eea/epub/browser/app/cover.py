""" ePub cover
"""
from zope.publisher.interfaces import NotFound
from zope.component import queryMultiAdapter, queryUtility
from Products.Five.browser import BrowserView
from eea.converter.interfaces import IConvert

class Cover(BrowserView):
    """ ePub Cover
    """
    def __call__(self, header=True, safe=False, **kwargs):
        pdf = queryMultiAdapter(
            (self.context.aq_inner, self.request), name="download.pdf")
        job = pdf.make_cover()
        ofile = getattr(job, 'path', '')
        if not ofile:
            getattr(job, 'cleanup', lambda: None)()
            if not safe:
                raise NotFound(self.context, self.__name__, self.request)
            return None

        converter = queryUtility(IConvert)
        data = converter(None, path_from=ofile)
        job.cleanup()

        if header:
            self.request.response.setHeader('Content-Type', 'image/png')
        return data
