""" Epub Body
"""
import logging
import urlparse
import requests
from bs4 import BeautifulSoup

from zope.interface import implementer
from zope.component import queryAdapter, queryMultiAdapter
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.interfaces import IPublishTraverse

from Products.Five.browser import BrowserView
from eea.converter.interfaces import IPDFOptionsMaker

logger = logging.getLogger('eea.epub')


@implementer(IPublishTraverse)
class Css(BrowserView):
    """ Used for Css
    """
    def publishTraverse(self, request, name):
        """ Custom traverser
        """
        return self

    def __call__(self, *args, **kwargs):
        return self.request.URL0


@implementer(IPublishTraverse)
class Body(BrowserView):
    """ Epub body
    """
    template = ViewPageTemplateFile('../zpt/body.pt')

    def __init__(self, context, request):
        super(Body, self).__init__(context, request)
        self._print_css = None
        self._css = None
        self._body = None

    def absolute_url(self, src):
        """ Return abs URL out of a `src` img attribute
        """
        if src.startswith(('http:', 'https:')):
            return src
        state = queryMultiAdapter(
            (self.context.aq_inner, self.request),
            name=u'plone_context_state')
        url = state.object_url()
        if src.startswith('/'):
            return urlparse.urljoin(url, src)
        return urlparse.urljoin("%s/" % url, src)

    def cleanup(self, soup):
        """ Remove unnecessary items
        """
        # Remove relatedItems
        for item in soup.find_all(id='languageCodes'):
            item.clear()

        # Remove relatedItems
        for item in soup.find_all(class_='documentExportActions'):
            item.clear()

        # Remove relatedItems
        for item in soup.find_all(id='relatedItems'):
            item.clear()

        for item in soup.find_all(class_='relatedItems'):
            item.clear()

        for item in soup.find_all(id='socialmedia-viewlet'):
            item.clear()

        return soup

    def body(self):
        """ Return ePub body based on pdf.body
        """
        if self._body is not None:
            return self._body

        options = queryAdapter(self.context, IPDFOptionsMaker, name='pdf.body')
        path = getattr(options, 'body', '')
        path = path.replace(self.context.absolute_url() + '/', '', 1)
        if not path:
            self._css = []
            self._body = u""
            return self._body

        try:
            html = self.context.restrictedTraverse(path)
            soup = BeautifulSoup(html())
            soup = self.cleanup(soup)

            # Print css
            self._css = [css.get('href') for css in
                         soup.find_all(media='print', rel='stylesheet')
                         if css.get('href')]

            html = soup.find(id='content')
            self._body = html.decode()
        except Exception:
            self._css = []
            self._body = u"<body></body>"

        return self._body

    #
    # Public interface
    #
    def publishTraverse(self, request, name):
        """ Custom traverser
        """
        if name == 'css':
            return self.css
        elif name == 'Css' or name.endswith('.css'):
            return Css(self.context, self.request)
        return super(Body, self).publishTraverse(request, name)

    def css(self, **kwargs):
        """ Print css
        """
        if self._print_css is not None:
            return self._print_css

        if self._css is None:
            self.body()

        print_css = []
        for src in self._css:
            try:
                resp = requests.get(
                    src, cookies=self.request.cookies, timeout=5)
            except Exception, err:
                logger.exception(err)
            else:
                if resp.status_code == 200:
                    css = resp.content
                    if isinstance(css, unicode):
                        css = css.encode('utf-8')
                    print_css.append(css)

        print_css = '\n'.join(print_css)
        print_css = print_css.replace('@media print', "@media all")
        self._print_css = print_css

        return self._print_css

    def __call__(self, **kwargs):
        return self.template()
