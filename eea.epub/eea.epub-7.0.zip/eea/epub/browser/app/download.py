""" Export as epub
"""
from StringIO import StringIO

from zope import event
from zope.publisher.interfaces import NotFound
from zope.component.hooks import getSite
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter, queryUtility
from plone.app.async.interfaces import IAsyncService
from Products.Five.browser import BrowserView

from eea.converter import async
from eea.converter.interfaces import IContextWrapper
from eea.converter.job import _output
from eea.downloads.interfaces import IStorage

from eea.epub.export.interfaces import IHtml2EPub
from eea.epub.events.async import AsyncEPUBExportSuccess, AsyncEPUBExportFail
from eea.epub.config import EEAMessageFactory as _
from eea.epub.async import EpubJob


class ExportView(BrowserView):
    """ Export View
    """
    _fallback = None

    @property
    def fallback(self):
        """ Fallback ePub provided
        """
        if self._fallback is not None:
            return self._fallback

        fallback = self.context.restrictedTraverse('action-download-epub', None)
        if fallback and fallback.absolute_url().startswith(
                self.context.absolute_url()):
            self._fallback = (
                self.context.absolute_url() + '/action-download-epub'
            )
        return self._fallback

    def __call__(self):

        support = queryMultiAdapter((self.context, self.request),
                                    name='epub.support')
        if not getattr(support, 'can_download', lambda: False)():
            raise NotFound(self.context, self.__name__, self.request)

        # Fallback ePub provided
        if self.fallback:
            return self.request.response.redirect(self.fallback)

        epub = queryMultiAdapter((self.context, self.request),
                                 name='epub.body')
        body = epub()
        css = epub.css()

        ecover = queryMultiAdapter((self.context, self.request),
                                   name='epub.cover')
        cover = ecover(header=False, safe=True)

        output = StringIO()
        html2epub = queryUtility(IHtml2EPub)
        html2epub(
            body, cover, output,
            title=self.context.Title(),
            base_url=self.context.absolute_url(),
            css=css,
            cookies=self.request.cookies
        )

        response = self.request.response
        response.setHeader('Content-Type', 'application/xml+epub')
        response.setHeader(
                'Content-Disposition', 'attachment; filename=%s.epub' %
                                        self.context.id)

        output.seek(0)
        return output.read()


class AsyncExportView(ExportView):
    """ Download ePub asynchronously
    """
    template = ViewPageTemplateFile('../zpt/download.pt')

    def __init__(self, context, request):
        super(AsyncExportView, self).__init__(context, request)
        self._title = ''
        self._message = _(
            u"* The email is only used for the purpose of sending the ePub. "
            u"We do not store it for any other use."
        )
        self._email = ''
        self._link = ''

    @property
    def message(self):
        """ Message
        """
        return self._message

    @property
    def title(self):
        """ Title
        """
        if self._title:
            return self._title

        title = self.context.title_or_id()
        if isinstance(title, str):
            title = title.decode('utf-8')

        return _(
          u"Enter your email address where to send '${title}' ePub when ready",
            mapping={
                'title': title
            }
        )

    @property
    def email(self):
        """ User email
        """
        return self._email

    def _redirect(self, msg='', title=''):
        """ Redirect
        """
        self.request.set('disable_border', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        if msg:
            self._message = msg
        if title:
            self._title = title
        return self.template()

    def link(self):
        """ Download link
        """
        if not self._link:
            storage = IStorage(self.context).of('epub')
            self._link = storage.absolute_url()
        return self._link

    def period(self):
        """ Wait period
        """
        ptype = getattr(self.context, 'portal_type', '')
        if ptype.lower() in ('collection', 'topic', 'folder', 'atfolder'):
            return _(u"minutes")
        return _(u"seconds")

    def finish(self, email=''):
        """ Finish download
        """
        if email:
            self._email = email
            self._title = _(
                u"An email will be sent to you when the ePub is ready"
            )
            self._message = _(
                u"If you don't have access to your email address "
                u"check <a href='${link}'>this link</a> in a few ${period}.",
                mapping={
                    u"link": u"%s?direct=1" % self.link(),
                    u"period": self.period()
            })
        return self._redirect()

    def download(self, email='', **kwargs):
        """ Download
        """
        # Fallback ePub provided
        if self.fallback:
            self._link = self.fallback

        storage = IStorage(self.context).of('epub')
        filepath = storage.filepath()
        fileurl = self.link()
        url = self.context.absolute_url()
        title = self.context.title_or_id()

        portal = getSite()
        from_name = portal.getProperty('email_from_name')
        from_email = portal.getProperty('email_from_address')

        if self.fallback or async.file_exists(filepath):
            wrapper = IContextWrapper(self.context)(
                fileurl=fileurl,
                filepath=filepath,
                email=email,
                url=url,
                from_name=from_name,
                from_email=from_email,
                title=title,
                etype='epub'
            )

            event.notify(AsyncEPUBExportSuccess(wrapper))
            return self.finish(email=email)

        # Async generate PDF
        out = _output(suffix='.epub')
        cmd = url
        body = 'epub.body'
        cover = 'epub.cover'

        job = EpubJob(
            cmd=cmd,
            title=self.context.Title(),
            body=body,
            cover=cover,
            cookies=self.request.cookies,
            output=out, timeout=60, cleanup=[out]
        )

        worker = queryUtility(IAsyncService)
        queue = worker.getQueues()['']
        worker.queueJobInQueue(queue, ('epub',),
            async.run_async_job,
            self.context, job,
            success_event=AsyncEPUBExportSuccess,
            fail_event=AsyncEPUBExportFail,
            email=email,
            filepath=filepath,
            fileurl=fileurl,
            url=url,
            from_name=from_name,
            from_email=from_email,
            title=title,
            etype='epub'
        )

        return self.finish(email=email)

    def post(self, **kwargs):
        """ POST
        """
        if not self.request.get('form.button.download'):
            return self._redirect('Invalid form')

        email = self.request.get('email')

        # Filter bots
        if self.request.get('body'):
            return self.finish(email=email)

        if not email:
            return self.finish(email=email)

        return self.download(email, **kwargs)

    def __call__(self, *args, **kwargs):

        support = queryMultiAdapter((self.context, self.request),
                                    name='pdf.support')

        asynchronously = getattr(support, 'async', lambda: False)()
        if not asynchronously:
            return super(AsyncExportView, self).__call__()

        # We have the email, continue
        email = getattr(support, 'email', lambda: None)()
        if email:
            return self.download(email, **kwargs)

        # Email provided
        if self.request.method.lower() == 'post':
            return self.post(**kwargs)

        # Ask for email
        return self._redirect()
