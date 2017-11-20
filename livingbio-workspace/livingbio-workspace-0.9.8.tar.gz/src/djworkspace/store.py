import logging
import os

import workspace

try:
    from django.core.files import File
    from django.core.files.storage import DefaultStorage, FileSystemStorage
except ImportError:
    logging.warning("django_workspace require used in django framework")
    raise


def store(fieldfile, filepath):
    filename = os.path.basename(filepath)

    with open(filepath) as ifile:
        fieldfile.save(filename, File(ifile))


def remote(filepath, storage=DefaultStorage()):
    assert not isinstance(storage, FileSystemStorage), "Local FileSystem not support remote storage"
    assert os.path.exists(filepath), "File not exists"

    filename = os.path.basename(filepath)

    with open(filepath, 'rb') as ifile:
        return storage.save(filename, File(ifile))


def local(url_or_remote_file):
    if isinstance(url_or_remote_file, File):
        try:
            # NOTE: if it is a local file storage
            filepath = url_or_remote_file.path
            if os.path.exists(filepath):
                return filepath
        except Exception:
            pass

        if url_or_remote_file.storage.__class__.__name__.startswith('HashedFilename'):
            # NOTE: if it is a hashedfilename storage
            filename = os.path.basename(url_or_remote_file.name)
            return workspace._local(filename, url_or_remote_file.url)

        return workspace.local(url_or_remote_file.url)

    return workspace.local(url_or_remote_file)
