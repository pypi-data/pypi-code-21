"""iRODS storage broker."""

import os
import json
import logging
import tempfile
import time
import datetime

from dtoolcore.utils import (
    generate_identifier,
    base64_to_hex,
    get_config_value,
    mkdir_parents,
)
from dtoolcore.filehasher import FileHasher, sha256sum_hexdigest
from dtoolcore.storagebroker import StorageBrokerOSError

from dtool_irods import CommandWrapper

logger = logging.getLogger(__name__)


#############################################################################
# iRODS helper functions.
#############################################################################

def _get_file(irods_path, local_abspath):
    cmd = CommandWrapper(["iget", irods_path, local_abspath])
    cmd()


def _get_text(irods_path):
    """Get raw text from iRODS."""
    # Command to get contents of file to stdout.
    cmd = CommandWrapper([
        "iget",
        irods_path,
        "-"
    ])
    return cmd()


def _put_text(irods_path, text):
    """Put raw text into iRODS."""
    with tempfile.NamedTemporaryFile() as fh:
        fpath = fh.name
        fh.write(text)
        fh.flush()
        cmd = CommandWrapper([
            "iput",
            "-f",
            fpath,
            irods_path
        ])
        cmd()
    assert not os.path.isfile(fpath)


def _get_obj(irods_path):
    """Return object from JSON text stored in iRODS."""
    return json.loads(_get_text(irods_path))


def _put_obj(irods_path, obj):
    """Put python object into iRODS as JSON text."""
    text = json.dumps(obj)
    _put_text(irods_path, text)


def _path_exists(irods_path):
    cmd = CommandWrapper(["ils", irods_path])
    cmd(exit_on_failure=False)
    return cmd.success()


def _mkdir(irods_path):
    cmd = CommandWrapper(["imkdir", irods_path])
    cmd()


def _mkdir_if_missing(irods_path):
    if not _path_exists(irods_path):
        _mkdir(irods_path)


def _cp(fpath, irods_path):
    cmd = CommandWrapper(["iput", "-f", fpath, irods_path])
    cmd()


def _rm(irods_path):
    cmd = CommandWrapper(["irm", "-rf", irods_path])
    cmd()


def _rm_if_exists(irods_path):
    if _path_exists(irods_path):
        _rm(irods_path)


def _ls(irods_path):
    cmd = CommandWrapper(["ils", irods_path])
    cmd()

    def remove_header_line(lines):
        return lines[1:]

    def remove_redundant_whitespace(lines):
        return [l.strip() for l in lines]

    def deal_with_collections(lines):
        fixed_lines = []
        for l in lines:
            if l.startswith("C"):
                _, path = l.split()
                l = os.path.basename(path)
            fixed_lines.append(l)
        return fixed_lines

    text = cmd.stdout.strip()
    lines = text.split("\n")
    return deal_with_collections(
        remove_redundant_whitespace(
            remove_header_line(lines)
        )
    )


def _ls_abspaths(irods_path):
    for f in _ls(irods_path):
        yield os.path.join(irods_path, f)


def _put_metadata(irods_path, key, value):
    cmd = CommandWrapper(["imeta", "set", "-d", irods_path, key, value])
    cmd()


def _get_checksum(irods_path):
    # Get the hash.
    cmd = CommandWrapper(["ichksum", "-K", irods_path])
    cmd()
    line = cmd.stdout.strip()
    info = line.split()
    compound_chksum = info[1]
    alg, checksum = compound_chksum.split(":")
    return checksum


#############################################################################
# iRODS storage broker.
#############################################################################


class IrodsStorageBroker(object):
    """
    Storage broker to interact with datasets in iRODS.
    """

    #: Attribute used to define the type of storage broker.
    key = "irods"

    #: Attribute used by :class:`dtoolcore.ProtoDataSet` to write the hash
    #: function name to the manifest.
    hasher = FileHasher(sha256sum_hexdigest)

    def __init__(self, uri, config_path=None):

        self._abspath = os.path.abspath(uri)
        self._dtool_abspath = os.path.join(self._abspath, '.dtool')
        self._admin_metadata_fpath = os.path.join(self._dtool_abspath, 'dtool')
        self._data_abspath = os.path.join(self._abspath, 'data')
        self._manifest_abspath = os.path.join(
            self._dtool_abspath,
            'manifest.json'
        )
        self._readme_abspath = os.path.join(
            self._abspath,
            'README.yml'
        )
        self._overlays_abspath = os.path.join(
            self._dtool_abspath,
            'overlays'
        )
        self._metadata_fragments_abspath = os.path.join(
            self._dtool_abspath,
            'tmp_fragments'
        )

        self._irods_cache_abspath = get_config_value(
            "DTOOL_IRODS_CACHE_DIRECTORY",
            config_path=config_path,
            default=os.path.expanduser("~/.cache/dtool/irods")
        )

        # Cache for optimisation
        self._use_cache = False
        self._ls_abspath_cache = {}
        self._metadata_cache = {}
        self._size_and_timestamp_cache = {}
        self._metadata_dir_exists_cache = None

    def _ls_abspaths_with_cache(self, irods_path):
        if self._use_cache:
            if irods_path in self._ls_abspath_cache:
                return self._ls_abspath_cache[irods_path]

        abspaths = []
        for f in _ls(irods_path):
            abspaths.append(os.path.join(irods_path, f))

        if self._use_cache:
            self._ls_abspath_cache[irods_path] = abspaths

        return abspaths

    def _get_metadata_with_cache(self, irods_path, key):
        if self._use_cache:
            if irods_path in self._metadata_cache:
                if key in self._metadata_cache[irods_path]:
                    return self._metadata_cache[irods_path][key]

        cmd = CommandWrapper(["imeta", "ls", "-d", irods_path, key])
        cmd()
        text = cmd.stdout
        value_line = text.split('\n')[2]
        value = value_line.split(":")[1]
        value = value.strip()

        if self._use_cache:
            self._metadata_cache.setdefault(
                irods_path, {}).update({key: value})

        return value

    def _build_size_and_timestamp_cache(self):
        cmd = CommandWrapper(["ils", "-l", self._data_abspath])
        cmd()
        text = cmd.stdout.strip()
        for line in text.split("\n")[1:]:
            line = line.strip()
            info = line.split()
            size_in_bytes_str = info[3]
            size_in_bytes = int(size_in_bytes_str)
            time_str = info[4]
            dt = datetime.datetime.strptime(time_str, "%Y-%m-%d.%H:%M")
            utc_timestamp = int(time.mktime(dt.timetuple()))
            fname = info[6]
            fpath = os.path.join(self._data_abspath, fname)
            self._size_and_timestamp_cache[fpath] = (
                size_in_bytes,
                utc_timestamp
            )

    def _get_size_and_timestamp_with_cache(self, irods_path):
        if self._use_cache:
            if irods_path in self._size_and_timestamp_cache:
                return self._size_and_timestamp_cache[irods_path]

        cmd = CommandWrapper(["ils", "-l", irods_path])
        cmd()
        text = cmd.stdout.strip()
        first_line = text.split("\n")[0].strip()
        info = first_line.split()
        size_in_bytes_str = info[3]
        size_in_bytes = int(size_in_bytes_str)
        time_str = info[4]
        dt = datetime.datetime.strptime(time_str, "%Y-%m-%d.%H:%M")
        utc_timestamp = int(time.mktime(dt.timetuple()))

        return size_in_bytes, utc_timestamp

    @classmethod
    def list_dataset_uris(cls, prefix, config_path):
        """Return list containing URIs in prefix location."""
        uri_list = []

        logger.info("prefix: '{}'".format(prefix))

        for dir_path in _ls_abspaths(prefix):

            logger.info("dir path: '{}'".format(dir_path))

            storage_broker = cls(dir_path, config_path)

            if not storage_broker.has_admin_metadata():
                continue

            uri_list.append("{}://{}".format(cls.key, dir_path))

        return uri_list

    @classmethod
    def generate_uri(cls, name, uuid, prefix):
        dataset_path = os.path.join(prefix, uuid)
        dataset_abspath = os.path.abspath(dataset_path)
        return "{}:{}".format(cls.key, dataset_abspath)

#############################################################################
# Methods used by both ProtoDataSet and DataSet.
#############################################################################

    def get_admin_metadata(self):
        """Return admin metadata from iRODS.

        :returns: administrative metadata as a dictionary
        """
        return _get_obj(self._admin_metadata_fpath)

    def has_admin_metadata(self):
        """Return True if the administrative metadata exists.

        This is the definition of being a "dataset".
        """
        return _path_exists(self._admin_metadata_fpath)

    def get_readme_content(self):
        """Return content of the README file as a string.

        :returns: readme content as a string
        """
        return _get_text(self._readme_abspath)

    def put_overlay(self, overlay_name, overlay):
        """Store the overlay by writing it to iRODS.

        It is the client's responsibility to ensure that the overlay provided
        is a dictionary with valid contents.

        :param overlay_name: name of the overlay
        :overlay: overlay dictionary
        """
        fpath = os.path.join(self._overlays_abspath, overlay_name + '.json')
        _put_obj(fpath, overlay)

#############################################################################
# Methods only used by DataSet.
#############################################################################

    def get_manifest(self):
        """Return the manifest contents from iRODS.

        :returns: manifest as a dictionary
        """
        return _get_obj(self._manifest_abspath)

    def list_overlay_names(self):
        """Return list of overlay names."""
        overlay_names = []
        for fname in _ls(self._overlays_abspath):
            name, ext = os.path.splitext(fname)
            overlay_names.append(name)
        return overlay_names

    def get_overlay(self, overlay_name):
        """Return overlay as a dictionary.

        :param overlay_name: name of the overlay
        :returns: overlay as a dictionary
        """
        fpath = os.path.join(self._overlays_abspath, overlay_name + '.json')
        return _get_obj(fpath)

    def get_item_abspath(self, identifier):
        """Return absolute path at which item content can be accessed.

        :param identifier: item identifier
        :returns: absolute path from which the item content can be accessed
        """
        admin_metadata = self.get_admin_metadata()
        uuid = admin_metadata["uuid"]
        # Create directory for the specific dataset.
        dataset_cache_abspath = os.path.join(self._irods_cache_abspath, uuid)
        mkdir_parents(dataset_cache_abspath)

        # Get the file extension from the  relpath from the handle metadata.
        irods_item_path = os.path.join(self._data_abspath, identifier)
        relpath = self._get_metadata_with_cache(irods_item_path, "handle")
        _, ext = os.path.splitext(relpath)

        local_item_abspath = os.path.join(
            dataset_cache_abspath,
            identifier + ext)

        if not os.path.isfile(local_item_abspath):
            _get_file(irods_item_path, local_item_abspath)

        return local_item_abspath


#############################################################################
# Methods only used by ProtoDataSet.
#############################################################################

    def create_structure(self):
        """Create necessary structure to hold a dataset."""

        # Ensure that the specified path does not exist and create it.
        if _path_exists(self._abspath):
            raise(StorageBrokerOSError(
                "Path already exists: {}".format(self._abspath)
            ))

        # Make sure the parent collection exists.
        parent, _ = os.path.split(self._abspath)
        if not _path_exists(parent):
            raise(StorageBrokerOSError(
                "No such iRODS collection: {}".format(parent)))

        _mkdir(self._abspath)

        # Create more essential subdirectories.
        essential_subdirectories = [
            self._dtool_abspath,
            self._data_abspath,
            self._overlays_abspath
        ]
        for abspath in essential_subdirectories:
            _mkdir_if_missing(abspath)

    def put_admin_metadata(self, admin_metadata):
        """Store the admin metadata by writing to iRODS.

        It is the client's responsibility to ensure that the admin metadata
        provided is a dictionary with valid contents.

        :param admin_metadata: dictionary with administrative metadata
        """
        _put_obj(self._admin_metadata_fpath, admin_metadata)

    def put_manifest(self, manifest):
        """Store the manifest by writing it to iRODS.

        It is the client's responsibility to ensure that the manifest provided
        is a dictionary with valid contents.

        :param manifest: dictionary with manifest structural metadata
        """
        _put_obj(self._manifest_abspath, manifest)

    def put_readme(self, content):
        """
        Put content into the README of the dataset.

        The client is responsible for ensuring that the content is valid YAML.

        :param content: string to put into the README
        """
        _put_text(self._readme_abspath, content)

    def put_item(self, fpath, relpath):
        """Put item with content from fpath at relpath in dataset.

        Missing directories in relpath are created on the fly.

        :param fpath: path to the item on local disk
        :param relpath: relative path name given to the item in the dataset as
                        a handle
        """
        # Put the file into iRODS.
        fname = generate_identifier(relpath)
        dest_path = os.path.join(self._data_abspath, fname)
        _cp(fpath, dest_path)

        # Add the relpath handle as metadata.
        _put_metadata(dest_path, "handle", relpath)

        return relpath

    def iter_item_handles(self):
        """Return iterator over item handles."""
        for abspath in self._ls_abspaths_with_cache(self._data_abspath):
            relpath = self._get_metadata_with_cache(abspath, "handle")
            yield relpath

    def item_properties(self, handle):
        """Return properties of the item with the given handle."""
        fname = generate_identifier(handle)
        irods_item_path = os.path.join(self._data_abspath, fname)

        # Get the hash.
        checksum = _get_checksum(irods_item_path)
        checksum_as_hex = base64_to_hex(checksum)

        # Get the UTC timestamp and the size in bytes.
        size, timestamp = self._get_size_and_timestamp_with_cache(
            irods_item_path
        )

        # Get the relpath from the handle metadata.
        relpath = self._get_metadata_with_cache(irods_item_path, "handle")

        properties = {
            'size_in_bytes': int(size),
            'utc_timestamp': timestamp,
            'hash': checksum_as_hex,
            'relpath': relpath
        }
        return properties

    def _handle_to_fragment_absprefixpath(self, handle):
        stem = generate_identifier(handle)
        return os.path.join(self._metadata_fragments_abspath, stem)

    def add_item_metadata(self, handle, key, value):
        """Store the given key:value pair for the item associated with handle.

        :param handle: handle for accessing an item before the dataset is
                       frozen
        :param key: metadata key
        :param value: metadata value
        """
        _mkdir_if_missing(self._metadata_fragments_abspath)

        prefix = self._handle_to_fragment_absprefixpath(handle)
        fpath = prefix + '.{}.json'.format(key)

        _put_obj(fpath, value)

    def _metadata_dir_exists(self):
        if self._use_cache:
            if self._metadata_dir_exists_cache is None:
                self._metadata_dir_exists_cache = \
                    _path_exists(self._metadata_fragments_abspath)
            return self._metadata_dir_exists_cache
        return _path_exists(self._metadata_fragments_abspath)

    def get_item_metadata(self, handle):
        """Return dictionary containing all metadata associated with handle.

        In other words all the metadata added using the ``add_item_metadata``
        method.

        :param handle: handle for accessing an item before the dataset is
                       frozen
        :returns: dictionary containing item metadata
        """
        if not self._metadata_dir_exists():
            return {}

        prefix = self._handle_to_fragment_absprefixpath(handle)

        files = [f for f in self._ls_abspaths_with_cache(
                 self._metadata_fragments_abspath)
                 if f.startswith(prefix)]

        metadata = {}
        for f in files:
            key = f.split('.')[-2]  # filename: identifier.key.json
            value = _get_obj(f)
            metadata[key] = value

        return metadata

    def pre_freeze_hook(self):
        """Pre :meth:`dtoolcore.ProtoDataSet.freeze` actions.

        This method is called at the beginning of the
        :meth:`dtoolcore.ProtoDataSet.freeze` method.

        In iRODS it is used to create caches for repetitive and time consuming
        calls to iRODS.
        """
        self._use_cache = True
        self._build_size_and_timestamp_cache()

    def post_freeze_hook(self):
        """Post :meth:`dtoolcore.ProtoDataSet.freeze` cleanup actions.

        This method is called at the end of the
        :meth:`dtoolcore.ProtoDataSet.freeze` method.
        """
        self._use_cache = False
        self._ls_abspath_cache = {}
        self._metadata_cache = {}
        self._size_and_timestamp_cache = {}
        _rm_if_exists(self._metadata_fragments_abspath)
