""" Functional tests for importing epubs
"""

from StringIO import StringIO
import os.path
from App.Common import package_home
from eea.epub.interfaces import IImportedBook
from eea.epub.interfaces import IImportedChapter
from eea.epub.interfaces import IImportedImage
from eea.epub.tests.base import EpubFunctionalTestCase

class ImporterTest(EpubFunctionalTestCase):
    """ ImporterTest class
    """

    def afterSetUp(self):
        """ After setup method
        """
        self.setRoles(['Manager'])

        filePath = os.path.join(package_home(globals()), 'test.epub')
        f = open(filePath)
        fileContent = StringIO(f.read())
        f.close()

        eid = self.portal.invokeFactory('EpubFile', id='tmp')
        tmp = getattr(self.portal, eid)
        view = tmp.restrictedTraverse('@@epub_import_view')
        view.importFile(fileContent)

        self.rootEpubFolder = getattr(self.portal,
                        'climate-change-impact-in-europe', None)

    def test_folderStructure(self):
        """ Tests the folderStructure of the epub contenttype
        """
        self.failUnless(self.rootEpubFolder is not None)
        self.failUnless(IImportedBook.providedBy(self.rootEpubFolder))

        chapter = getattr(self.rootEpubFolder, 'chapter1.xhtml')
        self.failUnless(IImportedChapter.providedBy(chapter))
        self.failUnless(chapter.Title() == 'Climate change impact in Europe')
        self.failUnless(chapter.Description() == \
                "The earth's climate has not changed many times in the course "
                "of its long history. Most of these changes occurred over "
                "hundreds, thousands or millions of years and were driven by "
                "natural phenomena such as variations in the Earth's orbit "
                "around the sun, variations in the Earth's axis, fluctuations "
                "in the sun's activity and volcanic eruptions.")

        chapter = getattr(self.rootEpubFolder, 'cover.xhtml')
        self.failUnless(chapter.portal_type == "Document")

    def test_originalFileSaved(self):
        """ Test if the original file saved is the save as the one saved
        """
        original = getattr(self.rootEpubFolder, 'original.epub')
        self.failUnless(original.portal_type == 'File')
        field = original.getField('file')
        self.failUnless(field.getContentType(original) == \
                'application/epub+zip')

    def test_coverImage(self):
        """ Tests if the portal type of epub_cover is Image
        """
        self.failUnless(self.rootEpubFolder.epub_cover.portal_type == 'Image')

    def test_creator(self):
        """ Tests if the name of the creator is equal to a given entry
        """
        self.failUnless(self.rootEpubFolder.Creator() == 'S\xc3\xb8ren Roug')

    def test_imagesImportedCorrectly(self):
        """ Tests if images were imported correctly
        """
        brains = self.rootEpubFolder['Pictures'].getFolderContents(
                                            {'portal_type': 'Image'})
        img1 = brains[0].getObject()
        self.failUnless(IImportedImage.providedBy(img1))
        self.failUnless(len(brains) == 9)

def test_suite():
    """ Test Suite
    """
    from unittest import TestSuite, makeSuite
    suite = makeSuite(ImporterTest)
    return  TestSuite(suite)
