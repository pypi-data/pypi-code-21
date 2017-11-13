from collections import OrderedDict
import logging
import os
import os.path as op
import re
import shutil

from pozetroncli.conf import get_tags_filename


TAG_REGEX = re.compile(r'^([a-z0-9]+(?:(?:\.|_{1,2}|-{1,2})[a-z0-9]+)*)'
                       r'(?::([a-zA-Z0-9_][a-zA-Z0-9_.-]{0,127}))?$')
TAG_SEP = re.compile(r'[:._-]+')
HASH_REGEX = re.compile(r'^[0-9a-f]{64}$')


class TagError(Exception):
    pass


class TagStore(object):

    def __init__(self):
        self._tag_to_hash = OrderedDict()
        self._hash_to_tags = None
        logger = logging.getLogger('verbose')
        try:
            with open(get_tags_filename()) as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    tag, hash = line.strip().split(',', 1)
                    if not TAG_REGEX.match(tag) or not HASH_REGEX.match(hash):
                        logger.warning('TagStore: invalid line: {!r}'.format(line))
                        continue
                    self._tag_to_hash[tag] = hash
        except (IOError, OSError) as ex:
            if ex.args[0] != 2:  # FileNotFoundError
                raise
        self._modified = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def save(self):
        if not self._modified:
            return
        makedirs(op.dirname(get_tags_filename()), exist_ok=True)
        tmp_filename = get_tags_filename() + '.tmp'
        with open(tmp_filename, 'w') as file:
            file.writelines('{},{}\n'.format(tag, hash)
                            for tag, hash in self._tag_to_hash.items())
        shutil.move(tmp_filename, get_tags_filename())
        self._modified = False

    def get_hash(self, tag):
        """Returns hash, or None if there is no such tag."""
        return self._tag_to_hash.get(tag)

    def add_tag(self, hash, tag):
        """
        Add new tag. Multiple tags can be assigned to one hash.
        If tag already exists, it is reassigned to a new hash.

        Raises TagError if hash or tag is invalid.
        """
        logger = logging.getLogger('brief')
        if not HASH_REGEX.match(hash):
            raise TagError('Not a valid hash: {}'.format(hash))
        if not TAG_REGEX.match(tag):
            raise TagError('Not a valid tag: {}'.format(tag))
        old_hash = self._tag_to_hash.get(tag)
        self._tag_to_hash[tag] = hash
        self._modified = True
        if old_hash is not None:
            logger.info('Tag removed from {}'.format(old_hash))
        logger.info('{} -> {}'.format(tag, hash))

    def get_tags(self, hash):
        """Returns list of tags for a hash (may be empty)."""
        if self._hash_to_tags is None:
            self._hash_to_tags = {}
            for tag, h in self._tag_to_hash.items():
                tags = self._hash_to_tags.get(h)
                if tags is None:
                    tags = []
                    self._hash_to_tags[h] = tags
                tags.append(tag)
        tags = self._hash_to_tags.get(hash, [])
        tags.sort(key=TAG_SEP.split)
        return tags

    def remove_tag(self, tag):
        """
        Delete tag if it exists.
        If tag does not exist, print message to log.
        """
        logger = logging.getLogger('brief')
        old_hash = self._tag_to_hash.get(tag)
        if old_hash is None:
            logger.info('No such tag')
            return
        del self._tag_to_hash[tag]
        self._modified = True
        logger.info('Tag removed from {}'.format(old_hash))

    def list_tags(self):
        """Returns ordered list of (tag, hash)."""
        return sorted(self._tag_to_hash.items())


def makedirs(path, exist_ok=False):
    """Replacement for os.makedirs, working in Python 2."""
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.args[0] != 17 or not exist_ok:
            raise
