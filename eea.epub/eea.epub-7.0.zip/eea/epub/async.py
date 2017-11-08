""" Async job
"""
import os
import time
import errno
import logging
import requests
from zope.component import queryUtility
from eea.converter.job import AsyncJob
from eea.epub.export.interfaces import IHtml2EPub
logger = logging.getLogger('eea.epub')

class EpubJob(AsyncJob):
    """ Asynchronous generate ePub
    """
    path = ''

    def get_cover(self):
        """ Epub body
        """
        url = '/'.join((self.cmd, self.cover))
        try:
            resp = requests.get(url, cookies=self.cookies, timeout=self.timeout)
            status = resp.status_code
        except requests.exceptions.RequestException:
            return None

        if status != 200:
            return None

        cover = resp.content
        return cover

    def get_body(self):
        """ Epub body
        """
        url = '/'.join((self.cmd, self.body, ''))
        resp = requests.get(url, cookies=self.cookies, timeout=self.timeout)
        status = resp.status_code
        if status != 200:
            raise requests.exceptions.RequestException("%s" % status)

        html = resp.content
        if isinstance(html, unicode):
            html = html.decode('utf-8')
        return html

    def get_css(self):
        """ Epub print CSS
        """
        url = '/'.join((self.cmd, self.body, 'css'))
        resp = requests.get(url, cookies=self.cookies, timeout=self.timeout)
        status = resp.status_code
        if status != 200:
            raise requests.exceptions.RequestException("%s" % status)

        css = resp.content
        if isinstance(css, unicode):
            css = css.decode('utf-8')
        return css

    def run(self, **kwargs):
        """ Run job
        """
        safe = kwargs.get('safe', True)
        retry = kwargs.pop('retry', 0)
        errors = []

        try:
            body = self.get_body()
            cover = self.get_cover()
            css = self.get_css()

            html2epub = queryUtility(IHtml2EPub)
            html2epub(
                body, cover, self.path,
                title=self.title,
                base_url=self.cmd,
                css=css,
                cookies=self.cookies
            )
        except Exception, err:
            errors.append(err)


        if self.path and not os.path.getsize(self.path):
            # Protect against timeouts
            if retry < 3:
                retry += 1
                kwargs['retry'] = retry
                logger.warn('Retry %s cmd: %s', retry, self.cmd)
                time.sleep(retry)
                return self.run(**kwargs)

            self.cleanup()
            self.path = ''
            errors.append(
                IOError(errno.ENOENT, "Empty output ePub", self.cmd)
            )

        # Finish
        for error in errors:
            if not safe:
                raise error
            logger.exception(error)
