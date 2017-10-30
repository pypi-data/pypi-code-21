import errno
import inotify
import inotify.adapters
import inotify.calls
import inotify.constants
import logging
import os
import selectors

from django.contrib.staticfiles.finders import get_finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.autoreload import gen_filenames

FORMAT = '%(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)



class SelectorInotify(inotify.adapters.Inotify):
    def __init__(self, paths=[], block_duration_s=None):
        self._Inotify__block_duration = block_duration_s
        self._Inotify__watches = {}
        self._Inotify__watches_r = {}
        self._Inotify__buffer = b''
        self._Inotify__inotify_fd = inotify.calls.inotify_init()
        self._selector = selectors.DefaultSelector()

        self._selector.register(self._Inotify__inotify_fd, selectors.EVENT_READ)

        for path in paths:
            self.add_watch(path)

    def event_gen(self):
        while True:
            block_duration_s = self._Inotify__get_block_duration()

            # Poll, but manage signal-related errors.

            try:
                events = self._selector.select(block_duration_s)
            except IOError as e:
                if e.errno != errno.EINTR:
                    raise

                continue

            # Process events.

            for meta, event_type in events:
                # (fd) looks to always match the inotify FD.

                for (header, type_names, path, filename) \
                        in self._Inotify__handle_inotify_event(meta.fd, event_type):
                    yield (header, type_names, path, filename)

            yield None

class WatchError(BaseException):
    def __init__(self, ex):
        self._original_exception = ex
        if hasattr(ex, 'message'):
            msg = ex.message
        else:
            msg = str(ex)
        super().__init__(msg)

class Watcher:
    EVENT_MASK = (inotify.constants.IN_CLOSE_WRITE |
                  inotify.constants.IN_MODIFY |
                  inotify.constants.IN_DELETE_SELF |
                  inotify.constants.IN_MOVE_SELF |
                  inotify.constants.IN_CREATE |
                  inotify.constants.IN_MOVED_FROM |
                  inotify.constants.IN_MOVED_TO)
    STATIC = 0
    APP = 1

    def __init__(self):
        self.inotify = SelectorInotify()
        self.target_storage = staticfiles_storage
        self.source_storages = set()
        self.watch_map = {}
        for finder in get_finders():
            if hasattr(finder, 'storages'):
                for s in finder.storages.values():
                    if hasattr(s,'watch_sources'):
                        self.source_storages.add(s)
            elif hasattr(finder, 'storage') and hasattr(finder.storage,'watch_sources'):
                self.source_storages.add(finder.storage)

        for storage in self.source_storages:
            storage.watch_sources(self.inotify, mask=Watcher.EVENT_MASK)

        self._app_files = gen_filenames()
        for f in self._app_files:
            self.inotify.add_watch(bytes(os.path.dirname(f),encoding='utf-8'), mask=Watcher.EVENT_MASK)

    def unwatch(self):
        for storage in self.source_storages:
            storage.unwatch_sources(self.inotify)
        for f in self._app_files:
            self.inotify.remove_watch(bytes(f,encoding='utf-8'))

    def changes(self):
        try:
            for event in self.inotify.event_gen():
                if event is not None:
                    header, type_names, watch_path, filename = event
                    changed_src_path = os.path.join(watch_path.decode('utf-8'), filename.decode('utf-8')).rstrip('/')
                    if changed_src_path in self._app_files:
                        yield (changed_src_path, Watcher.APP)
                    for s in self.source_storages:
                        prefixed_path, f = s.get_changed_file(event)
                        if f is not None:
                            self.target_storage.delete(prefixed_path)
                            with f as SRC:
                                self.target_storage.save(prefixed_path, SRC)
                                yield (prefixed_path, Watcher.STATIC)
                                break
        except Exception as ex:
            raise WatchError(ex)
        finally:
            self.unwatch()




