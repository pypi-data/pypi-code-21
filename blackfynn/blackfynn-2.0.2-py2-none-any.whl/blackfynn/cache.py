import os
import time
import sqlite3
import numpy as np
import pandas as pd
from glob import glob
import multiprocessing as mp
from itertools import groupby
from datetime import datetime

# blackfynn-specific
from blackfynn import settings
from blackfynn.utils import usecs_to_datetime, log
from blackfynn.models import DataPackage, TimeSeriesChannel

def filter_id(some_id):
    return some_id.replace(':','_').replace('-','_')

def remove_old_pages(cache, mbdiff):
    # taste the rainbow!
    n = int(1.5 * ((mbdiff * 1024*1024) / 100) / cache.page_size) + 5

    # 2. Delete some pages from cache
    with cache.index_con as con:
        log.debug("Cache - removing {} pages...".format(n))
        # find the oldest/least accessed pages
        q = """
            SELECT channel,page,access_count,last_access
            FROM ts_pages
            ORDER BY last_access ASC, access_count ASC
            LIMIT {num_pages}
        """.format(num_pages=n)
        pages = con.execute(q).fetchall()

    # remove the selected pages
    pages_by_channel = groupby(pages, lambda x: x[0])
    for channel, page_group in pages_by_channel:
        _,pages,counts,times = zip(*page_group)
        # remove page files
        cache.remove_pages(channel, *pages)

    with cache.index_con as con:
        con.execute("VACUUM")

    log.debug('Cache - {} pages removed.'.format(n))
    return n


def compact_cache(cache):
    log.debug('Inspecting cache...')
    wait = 2
    max_mb = settings.cache_max_size
    current_mb = (cache.size/(1024.0*1024))
    desired_mb = 0.9*max_mb 
    while current_mb > desired_mb:
        log.debug('Cache - current: {:02f} MB, maximum: {} MB'.format(current_mb, max_mb))
        try:
            remove_old_pages(cache, current_mb-desired_mb)
        except sqlite3.OperationalError:
            log.debug('Cache - Index DB was locked, waiting {} seconds...'.format(wait))
            if wait >= 1024:
                log.error('Cache - Unable to compact cache!')
                return # silently fail
            time.sleep(wait)
            wait = wait*2
        current_mb = (cache.size/(1024.0*1024))


class Cache(object):
    def __init__(self):
        self.dir           = settings.cache_dir
        self.index_loc     = settings.cache_index
        self.index_con     = sqlite3.connect(self.index_loc, timeout=60)
        self.write_counter = 0

        # this might be replaced with existing page size (from DB)
        self.page_size = settings.ts_page_size

        # setup DB
        self.init_tables()

        # check/compact cache if too big
        self.start_compaction()

    def init_tables(self):
        with self.index_con as con:
            self.init_index_table(con)
            self.init_settings_table(con)

    def init_index_table(self, con):
        # check for index table
        q = "SELECT name FROM sqlite_master WHERE type='table' AND name='ts_pages'"
        r = con.execute(q)
        if r.fetchone() is None:
            log.info('Cache - Creating \'ts_pages\' table')
            # create index table
            q = """
                CREATE TABLE ts_pages (
                    channel CHAR(50) NOT NULL,
                    page INTEGER NOT NULL,
                    access_count INTEGER NOT NULL,
                    last_access DATETIME NOT NULL,
                    has_data BOOLEAN,
                    PRIMARY KEY (channel, page))
            """
            con.execute(q)

    def init_settings_table(self, con):
        # check for settings table
        q = "SELECT name FROM sqlite_master WHERE type='table' AND name='settings'"
        r = con.execute(q)
        if r.fetchone() is None:
            log.info('Cache - Creating \'settings\' table')
            # create settings table
            q = """
                CREATE TABLE settings (
                    ts_page_size INTEGER NOT NULL,
                    max_bytes    INTEGER NOT NULL,
                    modified     DATETIME)
            """
            con.execute(q)

            # insert settings values
            q = """
                INSERT INTO settings
                VALUES ({page_size},{max_bytes},'{time}')
            """.format(
                page_size = self.page_size,
                max_bytes = settings.cache_max_size,
                time      = datetime.now().isoformat())
            con.execute(q)

        else:
            # settings table exists... get page size
            result = con.execute("SELECT ts_page_size FROM settings").fetchone()
            if result is not None:
                self.page_size = result[0]
                if settings.ts_page_size != self.page_size:
                    log.warn('Using existing page_size={} from DB settings (user specified page_size={})' \
                        .format( self.page_size, settings.ts_page_size))
            else:
                # somehow, there is no entry
                self.page_size = settings.ts_page_size

    def set_page(self, channel, page, has_data):
        with self.index_con as con:
            q = "INSERT INTO ts_pages VALUES ('{channel}',{page},0,'{time}',{has_data})".format(
                    channel=channel.id,
                    page=page,
                    time=datetime.now().isoformat(),
                    has_data=int(has_data))
            con.execute(q)

    def set_page_data(self, channel, page, data, update=False):
        has_data = False if data is None else len(data)>0
        if has_data:
            # there is data, write it to file
            filename = self.page_file(channel.id, page, make_dir=True)
            data.name = 'values'
            data.reset_index().to_feather(filename)
            self.page_written()
        try:
            if update:
                # modifying an existing page entry
                self.update_page(channel, page, has_data)
            else:
                # adding a new page entry
                self.set_page(channel, page, has_data)
        except sqlite3.IntegrityError:
            # page already exists - ignore
            pass

    def check_page(self, channel, page):
        """
        Does page exist in cache?
        """
        with self.index_con as con:
            q = """ SELECT page
                    FROM   ts_pages
                    WHERE  channel='{channel}' AND page={page}
            """.format(channel=channel.id, page=page)
            r = con.execute(q).fetchone()
            return r is not None

    def page_has_data(self, channel, page):
        with self.index_con as con:
            q = """
                SELECT has_data
                FROM   ts_pages
                WHERE  channel='{channel}' AND page={page}
            """.format(channel=channel.id, page=page)
            r = con.execute(q).fetchone()
            return None if r is None else bool(r[0])

    def get_page_data(self, channel, page):
        has_data = self.page_has_data(channel, page) 
        if has_data is None:
            # page not present in cache
            return None
        elif not has_data:
            # page is empty
            return pd.Series([])

        # page has data, let's get it
        filename = self.page_file(channel.id, page, make_dir=True)
        if os.path.exists(filename):
            # get page data from file
            series = pd.read_feather(filename).set_index('index')['values']
            # update access count
            self.update_page(channel, page, has_data)
            return series
        else:
            # page file has been deleted recently?
            log.warn('Page file not found: {}'.format(filename))
            return None

    def update_page(self, channel, page, has_data=True):
       with self.index_con as con:
            q = """
                UPDATE ts_pages 
                SET access_count = access_count + 1,
                    last_access  = '{now}',
                    has_data     = {has_data}
                WHERE channel='{channel}' AND page='{page}'
            """.format(channel=channel.id,
                       page=page,
                       has_data=int(has_data),
                       now=datetime.now().isoformat())
            con.execute(q) 

    def page_written(self):
        # cache compaction?
        self.write_counter += 1
        if self.write_counter > settings.cache_inspect_interval:
            self.write_counter = 0
            self.start_compaction()

    def start_compaction(self, async=True):
        if async:
            # spawn cache compact job
            p = mp.Process(target=compact_cache, args=(self,))
            p.start() 
        else:
            log.info('Compacting cache...')
            compact_cache(self)
            log.info('Done')

    def remove_pages(self, channel_id, *pages):
        # remove page data files
        for page in pages:
            filename = self.page_file(channel_id,page)
            if os.path.exists(filename):
                os.remove(filename)
            try:
                os.removedirs(os.path.dirname(filename))
            except os.error:
                # directory not empty
                pass
        # remove page index entries
        with self.index_con as con:
            q = """
                DELETE
                FROM ts_pages
                WHERE channel = '{channel}' AND page in ({pages})
            """.format(channel=channel_id, pages=','.join(map(str, pages)))
            con.execute(q)

    def page_file(self, channel_id, page, make_dir=False):
        """
        Return the file corresponding to a timeseries page (stored in feather format).
        """
        filedir = os.path.join(self.dir, filter_id(channel_id))
        if make_dir and not os.path.exists(filedir):
            os.makedirs(filedir)
        filename = os.path.join(filedir,'page-{}.feather'.format(page))
        return filename

    def clear(self):
        import shutil
        shutil.rmtree(self.dir)

    @property
    def page_files(self):
        return glob(os.path.join(self.dir,'*','*.feather'))

    @property
    def size(self):
        """
        Returns the size of the cache in bytes
        """
        all_files = self.page_files + [self.index_loc]
        return sum(map(lambda x: os.stat(x).st_size, all_files))

cache = Cache() if settings.use_cache else None
