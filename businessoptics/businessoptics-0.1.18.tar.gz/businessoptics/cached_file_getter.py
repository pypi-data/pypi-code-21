import errno
import logging
import os
import pickle
import shutil
from tempfile import NamedTemporaryFile
from time import sleep
from zipfile import ZipFile

import requests

log = logging.getLogger(__name__)


class CachedFileGetter(object):
    def __init__(self, key):
        self.key = key

    def get_and_save(self, path):
        raise NotImplementedError()

    def get_metadata(self):
        return NotImplemented

    def is_cache_valid(self, new_meta, old_meta, path):
        return new_meta == old_meta

    def cache_root_location(self):
        return os.path.join(os.path.expanduser('~'),
                            '.download_cache',
                            self.__class__.__name__)

    def path(self):
        base = os.path.join(self.cache_root_location(),
                            str(self.key))
        path = os.path.join(base, 'thefile')
        meta_path = os.path.join(base, 'meta')

        try:
            os.makedirs(base)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        new_meta = self.get_metadata()

        cached = os.path.exists(path)
        if new_meta is not NotImplemented:
            if cached:
                try:
                    with open(meta_path, 'rb') as meta_file:
                        old_meta = pickle.load(meta_file)
                except IOError:
                    pass
                else:
                    cached = self.is_cache_valid(new_meta, old_meta, path)

            with open(meta_path, 'wb') as meta_file:
                pickle.dump(new_meta, meta_file)

        if not cached:
            self.get_and_save(path)
        return path

    def open(self, mode='rb', **kwargs):
        return open(self.path(), mode=mode, **kwargs)


class CachedTuplesCSV(CachedFileGetter):
    def __init__(self, has_tuples):
        super(CachedTuplesCSV, self).__init__(has_tuples.full_url.replace('/', '_'))
        self.has_tuples = has_tuples

    def get_metadata(self):
        return self.has_tuples.get()

    def get_and_save(self, path):
        log.info('Downloading CSV of %s', self.has_tuples.full_url)
        download_url = self.has_tuples.get('external_stream_csv')['download_url']
        with NamedTemporaryFile() as temp_zip_file:
            while True:
                response = requests.get(download_url, stream=True)
                if response.status_code == 200:
                    break
                sleep(5)
            shutil.copyfileobj(response.raw, temp_zip_file)
            temp_zip_file.flush()
            with ZipFile(temp_zip_file) as zipfile:
                extracted_path = zipfile.extract(zipfile.infolist()[0])
        shutil.move(extracted_path, path)
        log.info('Finished downloading CSV')
