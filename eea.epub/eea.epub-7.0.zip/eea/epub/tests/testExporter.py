""" Functional Tests
"""
from StringIO import StringIO
from zipfile import ZipFile
from zope.interface import alsoProvides
from eea.epub.tests.base import EpubFunctionalTestCase
from eea.epub.interfaces import ILayer
from Products.Five.security import newInteraction


class ExporterTest(EpubFunctionalTestCase):
    """ ExporterTest functional testing class
    """

    def afterSetUp(self):
        """ Set up
        """
        self.setRoles(['Manager'])
        self.article = self.portal[self.portal.invokeFactory(
                                    'News Item', id='testArticle')]
        self.article.setTitle('TestTitle')
        self.article.setText('TestText')

        context = self.article
        alsoProvides(context.REQUEST, ILayer)
        view = context.restrictedTraverse('@@download.epub')
        self.response = view.request.response
        newInteraction()
        self.responseOutput = view()

    def test_responseHeaders(self):
        """ Test Response Headers
        """
        self.failUnless(self.response.getHeader('Content-Type') == \
                                                'application/xml+epub')
        self.failUnless(self.response.getHeader('Content-Disposition') == \
                                    'attachment; filename=testArticle.epub')

    def test_zipFile(self):
        """ Test Zip file
        """
        responseOutput = StringIO(self.responseOutput)
        zipFile = ZipFile(responseOutput, 'r')
        fileNames = zipFile.namelist()
        self.failUnless('mimetype' in fileNames)
        self.failUnless('OEBPS/content.xhtml' in fileNames)
        self.failUnless('OEBPS/Css/print.css' in fileNames)


def test_suite():
    """Test Suite"""
    from unittest import TestSuite, makeSuite
    suite = makeSuite(ExporterTest)
    return  TestSuite(suite)
