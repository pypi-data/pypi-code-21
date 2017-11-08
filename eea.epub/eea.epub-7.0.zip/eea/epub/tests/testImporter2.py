""" Other functional tests for importing epubs
"""
from StringIO import StringIO
import os.path
from App.Common import package_home
from eea.epub.tests.base import EpubFunctionalTestCase


class ImporterTest(EpubFunctionalTestCase):
    """ ImporterTest class
    """

    def afterSetUp(self):
        """ After setup method
        """
        self.setRoles(['Manager'])

        filePath = os.path.join(package_home(globals()), 'test2.epub')
        f = open(filePath)
        fileContent = StringIO(f.read())
        f.close()

        fid = self.portal.invokeFactory('EpubFile', id='tmp')
        tmp = getattr(self.portal, fid)
        view = tmp.restrictedTraverse('@@epub_import_view')
        view.importFile(fileContent)

        self.rootEpubFolder = getattr(self.portal,
                        'climate-change-impact-in-europe', None)

    def test_toc(self):
        """ Tests the lenght of the table of contents
        """
        view = self.rootEpubFolder.restrictedTraverse('@@epub_toc_logic')
        navPoints = view.getNavPoints()
        self.failUnless(len(navPoints) == 10)

    def test_imageMetadata(self):
        """ Tests Image metadata
        """
        brains = self.rootEpubFolder['Pictures'].getFolderContents(
                                            {'portal_type': 'Image'})
        img1 = brains[0].getObject()
        self.failUnless(img1.Title() == 'Sun')
        self.failUnless(img1.Description() == 'This is a sun or something')


def test_suite():
    """ Test suite
    """
    from unittest import TestSuite, makeSuite
    suite = makeSuite(ImporterTest)
    return  TestSuite(suite)
