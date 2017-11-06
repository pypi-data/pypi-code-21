import io
import os
import queue
import hashlib
import logging
import threading

import steov

def _persist_blob (root, blob, blob_id, is_stopped):
    temp_file = os.path.join(root, "temp")
    prefix1 = blob_id[:2]
    prefix2 = blob_id[2:4]
    suffix = blob_id[4:]
    blob_dir = os.path.join(root, prefix1, prefix2)
    blob_file = os.path.join(blob_dir, suffix)
    if os.path.exists(blob_file):
        return
    os.makedirs(blob_dir, exist_ok=True)
    with io.BytesIO(blob) as blob_stream:
        with open(temp_file, "wb") as fp:
            while not is_stopped():
                block = blob_stream.read(4096)
                if not block:
                    break
                fp.write(block)
    os.rename(temp_file, blob_file)

class NoopHouse:
    def persist (self, blob):
        if blob is None:
            return None
        return hashlib.sha256(blob).hexdigest()

class FileHouse:
    def __init__ (self, root):
        self._root = root
        temp_file = os.path.join(self._root, "temp")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        self._logger = logging.getLogger(__name__)
        self._persist_lock = threading.Lock()

    def persist (self, blob):
        if blob is None:
            return None
        blob_id = hashlib.sha256(blob).hexdigest()
        try:
            with self._persist_lock:
                _persist_blob(self._root, blob, blob_id, lambda: False)
        except Exception:
            self._logger.error("filehouse.persist_blob.blob_id: " + repr(blob_id))
            self._logger.error("filehouse.persist_blob.stacktrace: " + repr(steov.format_exc()))
        return blob_id

class AsyncFileHouse (FileHouse):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = None

    def start (self):
        self._is_aborted = False
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def persist (self, blob):
        if blob is None:
            return None
        blob_id = hashlib.sha256(blob).hexdigest()
        if self._queue is not None:
            self._queue.put((blob, blob_id))
        else:
            self._logger.error("asyncfilehouse.persist: Trying to persist blob when not running (blob id: " + blob_id + ")")
        return blob_id

    def stop (self):
        self._queue.put(None)
        self._thread.join()
        self._queue = None

    def abort (self):
        queue = self._queue
        self._is_aborted = True
        self.stop()
        while queue.qsize():
            queue.get()
            queue.task_done()

    def __enter__ (self):
        self.start()
        return self

    def __exit__ (self, type, value, traceback):
        self.stop()

    def _run (self):
        while not self._is_aborted:
            blob_id = None
            item = self._queue.get()
            try:
                if item is None:
                    break
                blob, blob_id = item
                _persist_blob(self._root, blob, blob_id, lambda: self._is_aborted)
            except Exception as ex:
                self._logger.error("asyncfilehouse.run.blob_id: " + repr(blob_id))
                self._logger.error("asyncfilehouse.run.stacktrace: " + repr(steov.format_exc()))
            finally:
                self._queue.task_done()
