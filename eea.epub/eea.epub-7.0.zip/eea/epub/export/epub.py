""" Export to ePub utility
"""
import re
import os
import urlparse
import logging
from zipfile import ZipFile
import requests
from bs4 import BeautifulSoup
from zope.interface import implementer
from App.Common import package_home
from eea.epub.export.interfaces import IHtml2EPub
logger = logging.getLogger('eea.epub')

@implementer(IHtml2EPub)
class Html2EPub(object):
    """ Convert HTML to ePub
    """
    def abs_url(self, src, base_url=''):
        """ Return abs URL out of a `src` img attribute
        """
        if src.startswith(('http:', 'https:')):
            return src

        if base_url:
            if src.startswith('/'):
                return urlparse.urljoin(base_url, src)
            return urlparse.urljoin("%s/" % base_url, src)
        return None

    def slugify(self, title):
        """ Very basic slugify for ids or file names
        """
        return re.sub(r'[^a-zA-Z0-9\.]', '_', title)

    def stream(self, filePath):
        """ Same as `replace`, but no text handling, simply bytestream the data
        """
        filePath = self.static_path(filePath)
        f = open(filePath, "rb")
        content = f.read()
        f.close()
        return content

    def static_path(self, filePath):
        """ Return abs path of a static file named `filename` which is available
        inside the static folder available in this package for the epub tpl
        """
        return os.path.join(package_home(globals()), 'static', filePath)

    def replace(self, filePath, variables):
        """ Replaces content from a file with given variables
        """
        filePath = self.static_path(filePath)
        f = open(filePath)
        content = f.read()
        f.close()
        return content % variables

    def store_image(self, zipFile, url, itemid, filename='', cookies=None):
        """ Given an URL to an image, save it in zip and return path
        """
        try:
            resp = requests.get(url, cookies=cookies, timeout=5)
        except requests.exceptions.RequestException:
            return ('', '')
        if resp.status_code == 200:
            headers = resp.headers
            if not filename:
                filename = "%s%s" % (itemid, url.strip('/').rsplit('/', 1)[-1])
                filename = self.slugify(filename)

            media_type = headers.get('content-type')
            if not media_type:
                if filename.endswith('png'):
                    media_type = 'image/png'
                elif filename.endswith('jpg') or filename.endswith('jpeg'):
                    media_type = 'image/jpeg'
                elif filename.endswith('gif'):
                    media_type = 'image/gif'
                elif filename.endswith('svg'):
                    media_type = 'image/svg+xml'

            if len(filename.split('.')) < 2:
                ext = media_type.rstrip('+xml').split('/')[-1]
                filename = "%s.%s" % (filename, ext)

            zipFile.writestr('OEBPS/Images/%s' % filename, resp.content)
            return ("Images/%s" % filename,
                    '<item href="Images/%s" id="%s" media-type="%s"/>'
                    % (filename, itemid, media_type))
        else:
            return '', ''

    def handle_statics(self, body, zipFile, base_url='', cookies=None, css=''):
        """
        * Embedding images: looks for referenced images in content
        and properly save them in the epub
        * Style related images available in eea.epub template

        """
        manifest = []
        soup = BeautifulSoup(body)
        imgs = soup.find_all("img")
        for i, img in enumerate(imgs):
            if img.get('src'):
                url = self.abs_url(img['src'], base_url)
                itemid = 'image%05.d' % i
                src, manifest_entry = self.store_image(zipFile, url, itemid)
                if src:
                    img['src'] = src
                    if not img.get('alt'):
                        img['alt'] = "Image at %s" % url
                    manifest.append(manifest_entry)
                else:
                    img.extract()
        for img in os.listdir(self.static_path("OEBPS/Images")):
            rel_path = "OEBPS/Images/%s" % img
            if not os.path.isfile(self.static_path(rel_path)):
                continue
            zipFile.writestr(rel_path, self.stream(rel_path))
            manifest.append('<item href="Images/%s" id="%s" media-type="%s" />'
                            % (img, img, 'image/png'))

        for img in os.listdir(self.static_path("OEBPS/Fonts")):
            rel_path = "OEBPS/Fonts/%s" % img
            if not os.path.isfile(self.static_path(rel_path)):
                continue
            zipFile.writestr(rel_path, self.stream(rel_path))
            manifest.append('<item href="Fonts/%s" id="%s" media-type="%s" />'
                             % (img, img, 'application/x-font-ttf'))

        zipFile.writestr('OEBPS/Css/main.css',
                         self.stream("OEBPS/Css/main.css"))
        manifest.append(
          '<item href="Css/main.css" id="main.css" media-type="text/css" />')

        zipFile.writestr('OEBPS/Css/print.css', css)
        manifest.append(
          '<item href="Css/print.css" id="print.css" media-type="text/css" />')

        zipFile.writestr('OEBPS/Css/fonts.css',
                         self.stream("OEBPS/Css/fonts.css"))
        manifest.append(
          '<item href="Css/fonts.css" id="fonts.css" media-type="text/css" />')

        return soup, manifest

    def set_cover(self, zipFile, cover, base_url=''):
        """ Look for image inside the object and set it as cover
        """
        if cover:
            zipFile.writestr('OEBPS/Images/%s' % "cover.png", cover)
            return {
                'metadata': ['<meta name="cover" content="cover"/>'],
                'manifest': [
                    '<item href="Images/%s" id="cover" media-type="%s" />' %
                    ("cover.png", "image/png")
                ]}

    def set_toc(self, soup):
        """
        Build the table of contents for toc.ncx and return it
        as xml utf-8 string.
        Headings Level 2 are used to generate the table of contents.

        """
        chapters = []
        chapter_tpl = u"""
                      <navPoint id="navpoint-%(i)d" playOrder="%(i)d">
                        <navLabel>
                          <text>%(title)s</text>
                        </navLabel>
                        <content src="content.xhtml#%(offset)s"/>
                      </navPoint>"""
        for (i, h2) in enumerate(soup.find_all("h2")):
            title = h2.text
            offset = h2.get("id") or "%s_%d" % (self.slugify(title), i)
            chapters.append((title, offset))
            h2['id'] = offset
        if not chapters:
            h1 = soup.find("h1")
            if h1 and h1.text:
                chapters.append((h1.text, ''))
            else:
                chapters.append(('Content', ''))
        chap_xmls = [chapter_tpl % ({'title': t,
                                     'i': (i + 1),
                                     'offset': o})
                     for (i, (t, o)) in enumerate(chapters)]
        return u"\n".join(chap_xmls).encode("utf-8")

    def fix_daviz(self, soup, zipFile, base_url='', cookies=None):
        """
        Replace Daviz iframe with fallback images.
        Must be called AFTER `handle_statistics`.

        """
        manifest = []
        for (i, iframe) in enumerate(soup.find_all('iframe')):
            src = iframe.get('src')
            if u'embed-chart' in src:
                src = src.replace('embed-chart', 'embed-chart.png')
                # src = absolute_url(self.context,
                #         url=src, default=src, view='embed-chart.png')
                base = src.split('embed-chart.png')[0]
                query = urlparse.parse_qs(urlparse.urlparse(src).query)
                chart = query.get('chart')[0]
            elif u'embed-dashboard' in src:
                src = src.replace('embed-dashboard', 'embed-dashboard.png')
                # src = absolute_url(self.context,
                #         url=src, default=src, view='embed-dashboard.png')
                base = src.split('embed-dashboard.png')[0]
                query = urlparse.parse_qs(urlparse.urlparse(src).query)
                chart = query.get('dashboard')[0]
            else:
                continue

            src += '&tag:int=0&safe:int=0'

            if not src.startswith('http'):
                src = os.path.join(base_url, src)
            if not base.startswith('http'):
                base = os.path.join(base_url, base)

            img_src = ''
            try:
                resp = requests.get(src, cookies=cookies,
                                    timeout=5)
            except Exception, err:
                logger.exception(err)
            else:
                if resp.status_code == 200:
                    itemid = 'daviz%02.d' % i
                    fname = "%s.png" % itemid
                    img_src, manifest_item = self.store_image(zipFile, src,
                                                              itemid, fname)
            if img_src:
                iframe.replaceWith(
                    BeautifulSoup("<img src='%s' alt='%s' />" % (
                    img_src, "Chart at %s" % src
                )).find("img"))
                manifest.append(manifest_item)
            else:
                chart_url = u'%s#tab-%s' % (base, chart)
                message = BeautifulSoup(u'''
                <div class="portalMessage warningMessage pdfMissingImage">
                  <span>
                    This area contains interactive content
                    which can not be displayed in an e-book.
                    You may visit the online version at:
                  </span>
                  <a href="%(url)s">%(url)s</a>
                </div>''' % {'url': chart_url})
                iframe.replaceWith(message.find("div"))
        return (soup, manifest)

    def __call__(self, body, cover, output, **kwargs):
        # Object absolute url
        base_url = kwargs.get('base_url', '')
        title = kwargs.get('title', '')
        css = kwargs.get('css', '')
        cookies = kwargs.get('cookies', '')

        if not isinstance(body, unicode):
            body = body.decode('utf-8')

        zipFile = ZipFile(output, 'w')
        zipFile.writestr('mimetype', 'application/epub+zip')
        zipFile.writestr('META-INF/container.xml',
                         self.stream('META-INF/container.xml'))

        cover = self.set_cover(zipFile, cover, base_url)
        soup, statics = self.handle_statics(body, zipFile,
                                            base_url, cookies, css)
        soup, daviz = self.fix_daviz(soup, zipFile, base_url, cookies)
        toc = self.set_toc(soup)
        body = soup.prettify()

        variables = {
            'TITLE': title,
            'LANGUAGE': 'en', # make this dynamic
            'IDENTIFIER': base_url,
            'TOC': toc,
            'METADATA_MORE': '',
            'MANIFEST_MORE': '\n'.join(statics + daviz),
        }

        if cover:
            variables.update({
                'METADATA_MORE': '\n'.join(cover['metadata']),
                'MANIFEST_MORE': '\n'.join(cover['manifest'] + statics + daviz),
            })

        zipFile.writestr('OEBPS/content.xhtml', body.encode("utf-8"))
        zipFile.writestr('OEBPS/content.opf',
                         self.replace('OEBPS/content.opf', variables))
        zipFile.writestr('OEBPS/toc.ncx',
                         self.replace('OEBPS/toc.ncx', variables))
        zipFile.close()
