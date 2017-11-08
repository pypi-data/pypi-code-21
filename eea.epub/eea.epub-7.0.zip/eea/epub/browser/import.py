""" Browser Import
"""

import xml.etree.cElementTree as ET
import logging
import re
import urllib
from zipfile import ZipFile
from bs4 import BeautifulSoup
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from eea.epub.interfaces import IImportedBook
from eea.epub.interfaces import IImportedChapter
from eea.epub.interfaces import IImportedImage
from eea.epub.browser.events import EpubImportedEvent
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides
from zope.event import notify
import transaction
import lxml.html

logger = logging.getLogger('eea.epub.browser.import')


def titleToId(title):
    """ Return a stripped title to be made into an id
    """
    return title.strip().strip('!@#$%^&*()<>./+').lower().replace(' ', '-')


def elemTagWithoutNamespace(elem):
    """Remove the xmlns that ElementTree inserts before the tag name

    If a namespace is present, ElementTree prefixes the tag names in
    'Clark's Notation', e.g. {http://www.w3.org/2005/Atom}feed. To make it
    easier to select by tag, we remove this.

    http://stackoverflow.com/questions/1249876
    """
    assert not isinstance(elem, str), \
        'Make sure you pass in the element, not the tag'
    if '}' in elem.tag:
        return elem.tag.split('}')[1]
    return elem.tag


def stripNamespaces(node):
    """ Strips Namespaces from xml elements
    """
    node.tag = elemTagWithoutNamespace(node)
    for elem in node.getchildren():
        elem.tag = elemTagWithoutNamespace(elem)
        stripNamespaces(elem)
    return node

def cleanNames(name):
    """ Remove non alpha numeric characters from argument minus exceptions """
    return "".join(
        (x if (x.isalnum() or x in ['.', '/', '-', '#']) else '') for x in name)

def checkFileName(fileName):
    """ Check if fileName doesn't contain non allowed characters """
    bad_file_name = ''
    for i in fileName:
        if not i.isalnum() and i not in [".", "_", "-", '/', '#']:
            bad_file_name = fileName
            break
    return bad_file_name

class EpubFile(object):
    """ EpubFile
    """
    def __init__(self, zipFile):
        self.zipFile = zipFile
        self.cache = {}

    @property
    def rootFile(self):
        """ Find root of the Epub
        """
        if 'rootFile' in self.cache:
            return self.cache['rootFile']

        rfile = self.zipFile.read('META-INF/container.xml')
        xml = ET.XML(rfile)
        xml = stripNamespaces(xml)
        xml = xml.find('rootfiles')
        xml = xml.find('rootfile')
        rootFilePath = xml.get('full-path')
        fileContent = self.zipFile.read(rootFilePath)
        xml = ET.XML(fileContent)
        xml = stripNamespaces(xml)

        self.cache['rootFile'] = xml
        return xml

    @property
    def tocNavPoints(self):
        """ Navigation for table of contents
        """
        filePath = 'OEBPS/toc.ncx'
        fileContent = self.zipFile.read(filePath)
        xml = ET.XML(fileContent)
        xml = stripNamespaces(xml)
        ret = []
        for elem in xml.find('navMap'):
            ret.append({
                'label': elem.find('navLabel').find('text').text,
                'href': elem.find('content').get('src'),
            })
        return ret

    @property
    def coverImageData(self):
        """ Gets the cover image of the epub
        """
        if 'coverImageData' in self.cache:
            return self.cache['coverImageData']

        for elem in self.rootFile.find('manifest').findall('item'):
            mtype = elem.get('media-type', '')
            name = elem.get('type', '')
            mid = elem.get('id', '')
            if mtype.startswith('image') and (name.startswith('cover')
                                             or mid.startswith('cover')):
                coverImageData = self.zipFile.read('OEBPS/' + elem.get('href'))
                self.cache['coverImageData'] = coverImageData
                return coverImageData

        return None

    @property
    def title(self):
        """ Title of the epub
        """
        xml = self.rootFile
        xml = xml.find('metadata')
        xml = xml.find('title')
        return xml.text

    @property
    def page_resources(self):
        """ Defines the epub page resources
        """
        props = getToolByName(self, 'portal_properties').site_properties
        clean_epub_names = props.getProperty('clean_epub_file_names')

        if 'page_resources' in self.cache:
            return self.cache['page_resources']

        guide = self.rootFile.find('guide')
        chapter_hrefs = []
        if guide != None:
            for elem in guide.findall('reference'):
                if elem.get('type') == 'text':
                    chapter_hrefs.append(elem.get('href'))

        page_resources = []
        bad_file_names = []
        bad_file_name = ""
        items = self.rootFile.find('manifest').findall('item')
        chapter_links = []
        for elem in items:
            if not elem.get('media-type') == 'application/xhtml+xml':
                continue
            chapter_links.append(elem)
            href = elem.get('href')
            if clean_epub_names:
                bad_file_name = checkFileName(href)
                if bad_file_name:
                    bad_file_names.append(bad_file_name)

        for elem in chapter_links:
            href = elem.get('href')
            fileName = 'OEBPS/' + elem.get('href')
            fileName = urllib.unquote(fileName)
            fileContent = self.zipFile.read(fileName)
            html = lxml.html.fromstring(fileContent)
            html = html.find('body')
            isChapter = href in chapter_hrefs
            title = href
            description = ''
            if isChapter:
                description = html.find('p')
                html.remove(description)
                description = description.text.strip()
                h1 = html.find('h1')
                if h1 != None:
                    title = h1.text
                    html.remove(h1)
            imgs = list(html.getiterator('img'))
            for img in imgs:
                img.attrib['src'] = cleanNames(img.attrib['src'])

            if clean_epub_names:
                links = list(html.getiterator('a'))
                for link in links:
                    page_href = link.attrib.get('href')
                    if page_href:
                        for name in bad_file_names:
                            found = page_href.find(name)
                            if found >= 0:
                                bad_file_name = True
                                link.attrib['href'] = cleanNames(page_href)
            ##### regex replace of <a /> with <a></a>
            html = lxml.html.tostring(html)

            def repl(m):
                """ Replace """
                res = m.group(1) + '></a>'
                return res
            regex = r'(<a[^>]*)(/>)'

            html = re.sub(regex, repl, html)
            html = str(BeautifulSoup(html, 'lxml'))

            page_resources.append({
                'id': elem.get('href'),
                'title': title,
                'content': html,
                'description': description,
                'isChapter': isChapter,
                'badName' : True if bad_file_name else False
            })
        self.cache['page_resources'] = page_resources
        return page_resources

    def findDeep(self, elem, href):
        """ Find children in given element
        """
        for child in elem.getchildren():
            if (child.tag == 'img') and (child.get('src') == href):
                return child
            match = self.findDeep(child, href)
            if match != None:
                return match

    def findFirstImageMatchingHref(self, href):
        """ Finds the first image matching the given href
        """
        chapters = [resource for resource in self.page_resources if
                    resource['isChapter']]
        for chapter in chapters:
            body = chapter['content']
            if href in body:
                xml = ET.XML(body)
                xml = stripNamespaces(xml)
                match = None
                for elem in xml.getchildren():
                    match = self.findDeep(elem, href)
                    if match != None:
                        return {
                            'title': match.get('title', ''),
                            'alt': match.get('alt', ''),
                        }
        return {
            'title': '',
            'alt': '',
        }

    @property
    def images(self):
        """ Returns the images of the epub
        """

        if 'images' not in self.cache:
            self.cache['images'] = []
            for elem in self.rootFile.find('manifest').getchildren():
                if elem.get('media-type').startswith('image'):
                    href = elem.get('href')
                    firstMatch = self.findFirstImageMatchingHref(href)
                    self.cache['images'].append({
                        'href': href,
                        'title': firstMatch['title'],
                        'alt': firstMatch['alt'],
                    })
        return self.cache['images']

    @property
    def creator(self):
        """ Sets the creator of the epub
        """
        if 'creator' not in self.cache:
            elem = self.rootFile.find('metadata').find('creator')
            if elem != None:
                self.cache['creator'] = elem.text
            else:
                self.cache['creator'] = None
        return self.cache['creator']

    @property
    def language(self):
        """ Checks for the language of the book found in the metadata
        """
        elem = self.rootFile.find('metadata').find('language')
        if elem != None:
            return elem.text
        return None

    @property
    def ploneID(self):
        """ Returns a title that can be turned into an id with the use of
        titleToId
        """
        return titleToId(self.title)

class ImportView(BrowserView):
    """ ImportView Browserview
    """
    def __call__(self):
        if self.request.environ['REQUEST_METHOD'] == 'POST':
            httpFileUpload = self.request.form.values()[0]
            try:
                self.importFile(httpFileUpload) # new-id =
            except Exception, err:
                msg = "An error occur during upload," \
                      " your EPUB format may not be supported"
                logger.exception(err)
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='info')
                return self.request.response.redirect(
                    self.context.absolute_url() + "/edit")
            return self.request.response.redirect(self.context.absolute_url())

    def importFile(self, epubFile):
        """ Imports the epub file
        """

        zipFile = ZipFile(epubFile, 'r')
        epub = EpubFile(zipFile)

        transaction.savepoint()

        context = self.context
        context.setTitle(epub.title)
        if epub.creator != None:
            context.setCreators([epub.creator])

        annotations = IAnnotations(context)
        mapping = annotations['eea.epub'] = PersistentDict({'toc': []})
        mapping['toc'] = epub.tocNavPoints

        alsoProvides(context, IImportedBook)
        notify(EpubImportedEvent(self.context))
        context.reindexObject()

        # Save original file, we might need it later
        original = context[context.invokeFactory('File', id='original.epub')]
        original.setFile(epubFile)
        field = original.getField('file')
        field.getRaw(original).setContentType('application/epub+zip')

        if epub.coverImageData != None:
            context.invokeFactory('Image', id='epub_cover',
                                  image=epub.coverImageData)

        for image in epub.images:
            workingDirectory = context
            urlParts = image['href'].split('/')
            for urlPart in urlParts:
                if urlPart == urlParts[-1]:
                    path = 'OEBPS/' + image['href']
                    path = urllib.unquote(path)
                    data = epub.zipFile.read(path)
                    urlPart = cleanNames(urlPart)
                    obj = workingDirectory[workingDirectory.invokeFactory(
                            'Image', id=urlPart, image=data)]
                    obj.setTitle(image['title'].strip())
                    obj.setDescription(image['alt'])
                    alsoProvides(obj, IImportedImage)
                    obj.reindexObject()
                elif not urlPart in workingDirectory.objectIds():
                    workingDirectory = \
                    workingDirectory[workingDirectory.invokeFactory('Folder',
                                                                    id=urlPart)]
                else:
                    workingDirectory = workingDirectory[urlPart]

        for resource in epub.page_resources:
            workingDirectory = context
            urlParts = resource['id'].split('/')
            for urlPart in urlParts:
                if urlPart == urlParts[-1]:
                    urlPart = urllib.unquote(urlPart)
                    if resource['badName']:
                        urlPart = cleanNames(urlPart)
                    urlPart = urlPart.strip()
                    title = resource['title']
                    # set title as the id part of the file if the original
                    # title is equal to the id of the file
                    title = urlPart if title == resource['id'] else title
                    article = workingDirectory[ \
                        workingDirectory.invokeFactory('Document', id=urlPart)]
                    article.setTitle(title)
                    article.setText(resource['content'])
                    article.setDescription(resource['description'])
                    article._at_rename_after_creation = False
                    if resource['isChapter']:
                        alsoProvides(article, IImportedChapter)
                    article.reindexObject()
                elif not urlPart in workingDirectory.objectIds():
                    workingDirectory = \
                    workingDirectory[workingDirectory.invokeFactory('Folder',
                                                                 id=urlPart)]
                else:
                    workingDirectory = workingDirectory[urlPart]

        newId = context._renameAfterCreation(check_auto_id=False)
        return newId
