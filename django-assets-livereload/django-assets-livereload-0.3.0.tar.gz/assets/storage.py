import datetime
import functools
import json
import logging
import os
import re
import pathlib

from django.core.files.base import ContentFile
from django.contrib.staticfiles import storage

from .filters import get_filter_by_name

FORMAT = '%(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger(__name__)

def path_strip(path, left=0, right=0):
    if right == 0:
        right = len(path.parts)
    else:
        right = -right
    ret = pathlib.Path()
    for part in path.parts[left:right]:
        ret /= part
    return ret

def list_files(path, path_pattern='.*'):
    ret = []
    if not isinstance(path, pathlib.Path):
        path = pathlib.Path(path)
    for item in path.iterdir():
        if item.is_file() and path_pattern.search(item.path):
            ret.append(item)
        elif item.is_dir():
            ret += list_files(item.path, path_pattern=path_pattern)
    return ret


class ManifestTree:
    """
        Represents the target directory layout as constructed from a manifest file.
    """

    @classmethod
    def from_path(cls, path):
        """
            Given a path, constructs a tree from `path` (i.e. a tree where
            each node has at most one directory) and returns the root of the
            tree and the unique leaf node of the tree.
        """
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        # Construct the tree
        root = node = ManifestTree(path)

        # Find the (unique) leaf node
        while len(node._dirs) > 0:
            node = list(node._dirs.values())[0]

        return root, node

    def __init__(self, path='', data=None):
        """
            The constructor creates a tree struture corresponding to `path`.
            If `path` is emtpy or has just one component, the tree will
            consist only of the root node whose name will be `path.name`
            and whose `_data` attribute will contain `data`. If `path` has more
            components, a corresponding tree structure is built up (each node
            except for the leaf having precisely one successor) and the
            unique leaf node of the tree will have its `_data` attribute set to `data`.
        """
        if data is None:
            data = {}

        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        self._files = {}

        # Used for storing subdirectories (instances of ManifestTree)
        # keyed by subdirectory name
        self._dirs = {}

        if len(path.parts) > 1:
            self._name = path.parts[0]
            self._dirs[path.parts[1]] = ManifestTree(path_strip(path,left=1), data)
        else:
            self._data = data
            self._name = path.name

    def append_tree(self, tree):
        """
            Inserts `tree` as a subdirectory whose name will be `tree.name`
        """
        self._dirs[tree.name] = tree

    def __getitem__(self, key):
        """
            Returns the data attribute if `key` is a file, otherwise
            returns the subdirectory named `key` (an instance of ManifestTree)
        """
        if isinstance(key, pathlib.Path):
            key = key.name
        if key in self._files:
            return self._files[key]
        return self._dirs[key]

    def __setitem__(self, key, value):
        """
            If value is a ManifestTree, the method is equivalent to `append_tree(value)`,
            otherwise inserts the value into the `files` dictionary.
        """
        if isinstance(key, pathlib.Path):
            key = key.name
        if isinstance(value, ManifestTree):
            assert value.name == key
            self.append_tree(value)
        self._files[key] = value

    def __contains__(self, key):
        """
            Returns true if the current node has a file or directory whose
            name is `key`.
        """
        if isinstance(key, pathlib.Path):
            key = key.name
        return key in self._files or key in self._dirs

    def load_dir(self, path, file_pattern, dir_pattern, target_pattern=None, default_data=None):
        """
            Grafts a FileSystem directory tree starting at `path` onto the
            current node associating with each file metadata given by `default_data`.
            Only includes paths matching `file_pattern` (which must be an object
            implementing a match method) and only recurses into directories
            matching the `dir_pattern` (which must be an object implementing a
            match method).
        """
        if default_data is None:
            default_data = {}
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        for item in path.iterdir():
            if item.is_file() and file_pattern.match(item.name):
                source = str(item)
                if target_pattern:
                    item = pathlib.Path(file_pattern.sub(target_pattern, str(item)))
                self._files[item.name] = {
                    'name': item.stem,
                    'ext': item.suffix,
                    'sources': [source],
                    'filters': []
                }
                self._files[item.name].update(default_data)
            elif item.is_dir() and dir_pattern.match(item.name):
                dtree = ManifestTree(item.name, data=default_data)
                dtree.load_dir(item, file_pattern, dir_pattern, target_pattern, default_data)
                self._dirs[item.name] = dtree

    def find(self, path):
        """
            Returns the metadata associated with `path`, if `path`
            exists in the manifest tree.
        """
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        if len(path.parts) == 0:
            return self._data
        elif len(path.parts) == 1:
            return self._files[path.name]
        else:
            dtree = self._dirs[path.parts[0]]
            return dtree.find(path_strip(path,left=1))

    def listdir(self, path):
        """
            Returns a pair consisting of the list of subdirectories and the list of files
            of the directory `path` in the ManifestTree
        """
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)

        if len(path.parts) == 0:
            return self.list_dirs(), self.list_files()

        return self._dirs[path.parts[0]].listdir(path_strip(path,left=1))

    def list_files(self):
        """
            Lists the files contained in the node.
        """
        return self._files.keys()

    def list_dirs(self):
        """
            Lists the directories contained in the node.
        """
        return self._dirs.keys()

    def iter_files(self):
        for fname, data in self._files.items():
            yield (fname, data)

        for dirname, dirtree in self._dirs.items():
            for fname, data in dirtree.iter_files():
                yield (os.path.join(dirname, fname), data)

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def pretty_str(self, indent=0):
        istr = " "*indent*4
        files="".join([istr+" "+
                       fname+
                       "("+",".join(data.get('sources',[]))+")\n"
                       for fname, data in self._files.items()])
        dirs = "".join([istr+"-"+name+"\n"+d.pretty_str(indent+1) for name, d in self._dirs.items()])
        ret = []
        if len(files) > 0:
            ret.append(files)
        if len(dirs) > 0:
            ret.append(dirs)
        if len(ret) > 0:
            return "\n".join(ret)+"\n"
        else:
            return "(EMPTY)\n"

    def __str__(self):
        return self.pretty_str()


def conditionally_overrides(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self._manifest is None:
            return getattr(super(self.__class__, self), method.__name__)(*args, **kwargs)
        else:
            return method(self, *args, **kwargs)
    return wrapper


class ManifestStorage(storage.FileSystemStorage):
    """
    Manifest filesystem storage

    If the static directory doesn't contain a `manifest.json`
    file, this storage behaves exactly like :class:`FileSystemStorage`.
    Otherwise the `manifest.json` file has the following format (example):

    {
        # The top-level keys denote scopes/asset types
        # Use them as prefixes to the asset tag
        # e.g. {% asset 'app:javascript:bootstrap' %}

        'javascript': {
            'target_dir':'js',  # The name of the target directory where assets of this type are stored
            'target_ext':'.js', # The extension appended to all assets of this type
            'items': {          # A list of assets
                'bootstrap': {  # Asset name (used in the asset tag)
                    'sources': [# The asset is constructed by concatenating these files and
                                # optionally passing them through specified filters
                        'sass-bootstrap/js/tooltip.js',
                        'sass-bootstrap/js/popover.js',
                        'sass-bootstrap/js/tab.js',
                        'bootstrap-hover-dropdown/bootstrap-hover-dropdown.js'
                    ],
                    'filters':['jsmin'] # The filters to pass the source files through
                }
            }
        },

        'stylesheets': {
            'target_dir':'css',
            'target_ext':'css',
            'items': {
                'logika': {
                    'sources':['sass/logika.scss'],
                    'filters':['sass','cssmin']
                }
            }
        }
    }

    """

    def __init__(self, *args,  app_name="", **kwargs):
        super().__init__(*args, **kwargs)
        self._manifest = None
        if super().exists('manifest.json'):
            with open(self.path('manifest.json'), 'r') as IN:
                try:
                    manifest = json.load(IN)
                except Exception as ex:
                    raise Exception(str(ex)+" (when loading "+self.path('manifest.json')+")")
            self._app_name = app_name
            self._manifest_data = manifest
            self._manifest = append_to = ManifestTree()

            if len(self._app_name) > 0:
                append_to = ManifestTree(self._app_name)
                self._manifest.append_tree(append_to)

            # Iterate over asset types
            for tp in manifest.keys():
                target_dir = pathlib.Path(manifest[tp]['target_dir'])
                target_ext = manifest[tp].get('target_ext', '')
                troot, tleaf = ManifestTree.from_path(target_dir)
                append_to.append_tree(troot)
                if 'items' in manifest[tp]:
                    for name, meta in manifest[tp]['items'].items():
                        tleaf[name+target_ext] = {
                            'scope': tp,
                            'name': name,
                            'ext': target_ext,
                            'sources': meta['sources'],
                            'filters': meta.get('filters', []),
                            'watch': meta.get('watch', [])
                        }

                elif 'copy' in manifest[tp]:
                    file_pattern = re.compile(manifest[tp]['copy'].get('pattern', '.*'))
                    dir_pattern = re.compile(manifest[tp]['copy'].get('dir_pattern', '.*'))
                    target_pattern = manifest[tp]['copy'].get('target_pattern', None)
                    for source in manifest[tp]['copy']['sources']:
                        tleaf.load_dir(self.path(source), file_pattern=file_pattern, dir_pattern=dir_pattern, target_pattern=target_pattern, default_data={'scope': tp, 'filters': manifest[tp]['copy'].get('filters', [])})
            logging.info("Loaded: " + self.path('manifest.json'))

    @conditionally_overrides
    def _open(self, name, mode):
        if mode != 'r' and mode != 'rb':
            raise NotImplementedError("Manifest Storage only supports opening in 'r' mode, got '"+mode+"'.")
        item = self._manifest.find(name)
        data = b''
        cwd = self.path('')
        logger.info("Compiling '"+str(name)+"'")
        logger.info("  sources: "+str(item['sources']))
        logger.info("  filters: "+str(item.get('filters', [])))
        for src in item['sources']:
            cwd, _ = os.path.split(self.path(src))
            data = data+open(self.path(src), 'rb').read()
        for filt in item.get('filters', []):
            f = get_filter_by_name(filt)
            data = f(data, cwd=cwd)
        return ContentFile(data, name=name)

    @conditionally_overrides
    def delete(self, path):
        raise NotImplementedError("Manifest Storage does not support deleting.")

    @conditionally_overrides
    def listdir(self, path):
        return self._manifest.listdir(path)

    @conditionally_overrides
    def exists(self, name):
        try:
            item = self._manifest.find(name)
            return True
        except:
            return False

    @conditionally_overrides
    def size(self, name):
        raise NotImplementedError("Manifest Storage does not support the size call")

    @conditionally_overrides
    def get_accessed_time(self, name):
        item = self._manifest.find(name)
        latest_stamp = 0
        for s in item['sources']:
            stamp = os.path.getatime(self.path(s))
            if stamp > latest_stamp:
                latest_stamp = stamp
        return datetime.fromtimestamp(latest_stamp)

    @conditionally_overrides
    def get_modified_time(self, name):
        item = self._manifest.find(name)
        latest_stamp = 0
        for s in item['sources']:
            stamp = os.path.getmtime(self.path(s))
            if stamp > latest_stamp:
                latest_stamp = stamp
        return datetime.fromtimestamp(latest_stamp)

    @conditionally_overrides
    def get_created_time(self, name):
        raise NotImplementedError("Create time not available")

    def iter_files(self, path=''):
        if self._manifest is None:
            dirs, files = self.listdir(path)
            for f in files:
                yield (os.path.join(path,f), {'sources':[os.path.join(path,f)]})
            for d in dirs:
                try:
                    for f, data in self.iter_files(path=os.path.join(path,d)):
                        yield (f, data)
                except:
                    logger.error("Error listing directory "+os.path.join(path,d) + "("+self._app_name+")")
        else:
            for f, data in self._manifest.iter_files():
                yield f, data

    def watch_sources(self, inotify, mask):
        if self._manifest:
            logger.info("Registering watches for "+self.path(''))
        self._watch_map = {}
        for fname, data in self.iter_files():
            source_files = set([self.path(src) for src in data['sources']])
            source_dirs = set([os.path.dirname(f) for f in source_files])
            if 'watch' in data:
                for watch_pattern in data['watch']:
                    path = pathlib.Path('.')
                    for p in list_files(path, watch_pattern):
                        if p.is_file():
                            source_dirs.add(str(p.parent.absolute()))
                            source_files.add(str(p.absolute()))
            for src in source_dirs:
                inotify.add_watch(bytes(src,encoding='utf-8'),mask=mask)
            for src in source_files:
                self._watch_map[src] = fname

    def unwatch_sources(self, inotify):
        for p in self._watch_map.keys():
            inotify.remove_watch(bytes(p,encoding='utf-8'))

    def get_changed_file(self, inotify_event):
        header, type_names, watch_path, filename = inotify_event
        changed_src_path = os.path.join(watch_path.decode('utf-8'), filename.decode('utf-8')).rstrip('/')
        if changed_src_path in self._watch_map:
            target = self._watch_map[changed_src_path]
            if getattr(self, 'prefix', None):
                prefixed_path = os.path.join(self.prefix, target)
            else:
                prefixed_path = target
            logger.info("Change:"+str(prefixed_path))
            return prefixed_path, self.open(target)
        else:
            return None, None

