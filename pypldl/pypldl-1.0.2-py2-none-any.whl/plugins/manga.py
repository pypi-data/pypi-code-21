import re
import os
import logging
from ..core import Task

logger = logging.getLogger('manga')


class _MangaTask(Task):
    """
    Download manga chapters

    Attributes:
      title -- manga (path) title
      chapters -- list of chapter paths
      base_url -- base URL, override class value
      progress_chapters -- number of processed chapters
      progress_pages -- number of downloaded pages
      progress_queued_pages -- number of queued pages (not downloaded yet)

    title and chapters will be updated when the task is run.

    Priority format is: (chapter, [page])

    """

    img_extensions = ('jpg', 'png')

    def __init__(self, title, chapters=None):
        """Create a manga task

        Parameters:
          title -- manga title
          chapters -- chapters to download (see below)
          
        Chapters can be provided as:
          None -- download all chapters
          strings -- chapter paths (as seen in URLs) or names (not titles)
          integers -- chapter numbers

        """
        Task.__init__(self)
        self.title = title
        self.chapters = chapters
        self.progress_chapters = None
        self.progress_pages = None
        self.progress_queued_pages = None

    def __str__(self):
        return '<manga%s: %r>' % (self.handler_name, self.title)


    def progress(self):
        if self.progress_pages is None:
            return (0, "initializing")
        with self.lock:
            chapters = self.progress_chapters
            pages = self.progress_pages
            queue = self.progress_queued_pages
            nchapters = len(self.chapters)
        npages = pages + queue

        if chapters == 0:
            # no chapter downloaded yet, cannot estimate
            max_pages = "???"
            progress = 0.
        elif chapters == nchapters:
            # all chapter processed, page count is known
            max_pages = npages
            progress = float(pages)/npages
        else:
            # page count not known yet, make an estimation
            est_pages = npages + (nchapters - chapters) * (float(npages) / chapters)
            max_pages = "{0} (est.)".format(int(est_pages))
            progress = float(pages)/est_pages
        status = "chapters: {0}/{1}  pages: {2}/{3}".format(
                chapters, nchapters, pages, max_pages)
        return (progress, status)


    def run(self):
        # get manga information, update attributes
        info = self.get_manga_info(self.dm, self.title)
        if info is False:
            raise ValueError("manga not found: '%s'" % self.title)

        self.title = info['path']
        if self.outdir is None:
            self.outdir = self.title

        self.base_url = self.build_manga_url(self.title)
        logger.debug('get info for manga %s', self.title)

        # resolve chapters
        if self.chapters is None:
            chapters = info['chapters'].values()
        else:
            all_paths = set(info['chapters'].values())
            chapters = []
            for ch in self.chapters:
                if ch in all_paths:
                    chapters.append(ch)
                else:
                    if not isinstance(ch, basestring):
                        ch = str(ch)
                    if ch not in info['chapters']:
                        raise ValueError("chapter '%s' not found for manga '%s'" % (self.title, ch))
                    chapters.append(ch)
        self.chapters = chapters

        # initialize values for progress
        self.progress_chapters = 0
        self.progress_pages = 0
        self.progress_queued_pages = 0

        # download chapters
        logger.info("manga '%s': %d chapter(s) to download", self.title, len(chapters))
        for i, ch in enumerate(chapters):
            prio = (i,)
            self.dm.add_job(prio, self.fetch_chapter, (prio, ch))


    def fetch_chapter(self, prio, chapter):
        """Job routine to fetch a chapter"""

        pages = self.get_chapter_pages_paths(chapter)
        logger.info("downloading chapter '%s/%s' (%d pages)", self.title, chapter, len(pages))

        outprefix = self.outpath(chapter.replace('/', ','))
        outpath_fmt = '{0},{1:0%d}.' % max(3, len(str(len(pages))))

        for i, page in enumerate(pages):
            # build output path for the page
            outpath = outpath_fmt.format(outprefix, i+1)
            for ext in self.img_extensions:
                if os.path.exists(outpath+ext):
                    skip = True
                    break
            else:
                skip = False
            if skip:
                logger.info("skip page '%s/%s' (already downloaded)", self.title, page)
                with self.lock:
                    self.progress_pages += 1
                continue  # page already downloaded, skip
            logger.info("download page '%s/%s'", self.title, page)
            with self.lock:
                self.progress_queued_pages += 1
            self.dm.add_job(prio + (i,), self.fetch_page, (page, outpath))
        with self.lock:
            self.progress_chapters += 1


    def fetch_page(self, page, outpath):
        """Job routine to fetch a page"""

        img = self.get_image_url(page)
        ext = img.split('?')[0].rsplit('.', 1)[-1].lower()
        if ext not in self.img_extensions:
            ext = self.img_extensions[0]
        try:
            if img is None:
                logger.warning("no URL for page '%s/%s'", self.title, page)
                return
            self.download(img, outpath+ext)
        finally:
            with self.lock:
                self.progress_pages += 1
                self.progress_queued_pages -= 1


    @classmethod
    def build_manga_url(cls, title):
        """Build a manga URL from its title"""
        raise NotImplementedError()


    @classmethod
    def get_manga_info(cls, dm, title):
        """Get manga information, including chapter list

        Parameters:
          dm -- DownloadManager
          title -- manga title (will be normalized)

        Return a map with the following fields:
          title -- manga pretty title
          path -- manga path title
          chapters -- OrderedDict of chapter paths indexed by number (not title)
        If manga is not found, return False.

        """
        raise NotImplementedError()

    def get_chapter_pages_paths(self, chapter):
        """Get pages paths of a chapter
        Return a list of pages paths.
        """
        raise NotImplementedError()

    def get_image_url(self, page):
        """Get an image URL from a page path
        Return None if image URL is not found.
        """
        raise NotImplementedError()

