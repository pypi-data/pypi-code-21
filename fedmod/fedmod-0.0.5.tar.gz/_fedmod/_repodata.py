"""Helpers for metadata management"""
import sys
import tempfile
import os.path
import requests
import click
import gzip
import logging
import modulemd
import solv
import json
from attr import attributes, attrib
from requests_toolbelt.downloadutils.tee import tee_to_file
from fnmatch import fnmatch
from urllib.parse import urljoin
from lxml import etree

XDG_CACHE_HOME = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
CACHEDIR = os.path.join(XDG_CACHE_HOME, "fedmod")

log = logging.getLogger(__name__)

FALLBACK_STREAM = 'master'
STREAM = 'f27'
ARCH = 'x86_64'
_F27_BIKESHED_REPO = "https://dl.fedoraproject.org/pub/fedora/linux/modular/development/bikeshed/Server/"
_F27_MAIN_REPO = "https://dl.fedoraproject.org/pub/fedora/linux/development/27/Everything/"
_F27_UPDATES_REPO = "https://dl.fedoraproject.org/pub/fedora/linux/updates/27/"
_F27_BOOTSTRAP_MODULEMD = "https://src.fedoraproject.org/modules/bootstrap/raw/master/f/bootstrap.yaml"

@attributes
class RepoPaths:
    remote_repo_url = attrib(str)
    remote_metadata_url = attrib(str)
    local_cache_path = attrib(str)
    local_metadata_path = attrib(str)

def _define_repo(remote_prefix, local_cache_name, arch=None):
    if arch is None:
        local_arch_path = "source"
        if "updates" in remote_prefix:
            remote_arch_path = "SRPMS"
        else:
            remote_arch_path = "source/tree/"
    else:
        local_arch_path = arch
        if "updates" in remote_prefix:
            remote_arch_path = arch
        else:
            remote_arch_path = os.path.join(arch, "os/")
    remote_repo_url = os.path.join(remote_prefix, remote_arch_path)
    remote_metadata_url = os.path.join(remote_repo_url, "repodata/")
    local_cache_path = os.path.join(CACHEDIR, "repos", local_cache_name, local_arch_path)
    local_metadata_path = os.path.join(local_cache_path, "repodata/")
    return RepoPaths(remote_repo_url, remote_metadata_url,
                     local_cache_path, local_metadata_path)

_x86_64_MODULE_INFO = _define_repo(_F27_BIKESHED_REPO, "f27-modules", ARCH)
_SOURCE_MODULE_INFO = _define_repo(_F27_BIKESHED_REPO, "f27-modules")
_x86_64_PACKAGE_INFO = _define_repo(_F27_MAIN_REPO, "f27-packages", ARCH)
_SOURCE_PACKAGE_INFO = _define_repo(_F27_MAIN_REPO, "f27-packages")
_x86_64_UPDATES_INFO = _define_repo(_F27_UPDATES_REPO, "f27-updates", ARCH)
_SOURCE_UPDATES_INFO = _define_repo(_F27_UPDATES_REPO, "f27-updates")
_ALL_REPOS = (
    _x86_64_MODULE_INFO,
    _SOURCE_MODULE_INFO,
    _x86_64_PACKAGE_INFO,
    _SOURCE_PACKAGE_INFO,
    _x86_64_UPDATES_INFO,
    _SOURCE_UPDATES_INFO,
)
_BOOTSTRAP_MODULEMD = os.path.join(CACHEDIR, "f27-bootstrap.yaml")
_BOOTSTRAP_REVERSE_LOOKUP_CACHE = os.path.join(CACHEDIR, "f27-bootstrap-cache.json")

METADATA_SECTIONS = ("filelists", "primary", "modules")

_REPOMD_XML_NAMESPACE = {"rpm": "http://linux.duke.edu/metadata/repo"}
def _read_repomd_location(repomd_xml, section):
    location = repomd_xml.find(f"rpm:data[@type='{section}']/rpm:location", _REPOMD_XML_NAMESPACE)
    if location is not None:
        return location.attrib["href"]
    return None

def _download_one_file(remote_url, filename):
    if os.path.exists(filename) and not filename.endswith((".xml", ".yaml")):
        print(f"  Skipping download; {filename} already exists")
        return
    response = requests.get(remote_url, stream=True)
    try:
        print(f"  Downloading {remote_url}")
        chunksize = 65536
        expected_chunks = int(response.headers["content-length"]) / chunksize
        downloader = tee_to_file(response, filename=filename, chunksize=chunksize)
        show_progress = click.progressbar(downloader, length=expected_chunks)
        with show_progress:
            for chunk in show_progress:
                pass
    finally:
        response.close()
    print(f"  Added {filename} to cache")

def _download_metadata_files(repo_paths):
    local_path = repo_paths.local_cache_path
    local_metadata_path = repo_paths.local_metadata_path
    os.makedirs(local_metadata_path, exist_ok=True)
    repomd_url = urljoin(repo_paths.remote_metadata_url, "repomd.xml")
    print(f"Remote metadata: {repomd_url}")
    response = requests.get(repomd_url)
    response.raise_for_status()
    repomd_filename = os.path.join(local_metadata_path, "repomd.xml")
    with open(repomd_filename, "wb") as f:
        f.write(response.content)
    print(f"  Cached metadata in {repomd_filename}")
    repomd_xml = etree.parse(repomd_filename)
    files_to_fetch = set()
    for section in METADATA_SECTIONS:
        relative_href = _read_repomd_location(repomd_xml, section)
        if relative_href is not None:
            files_to_fetch.add(relative_href)
    predownload = set(os.listdir(local_path))
    for relative_href in files_to_fetch:
        absolute_href = urljoin(repo_paths.remote_repo_url, relative_href)
        filename = os.path.join(local_path, relative_href)
        # This could be parallelised with concurrent.futures, but
        # probably not worth it (it makes the progress bars trickier)
        _download_one_file(absolute_href, filename)
    postdownload = set(os.listdir(local_path))
    # Prune any old metadata files automatically
    if len(postdownload) >= (len(predownload) + len(METADATA_SECTIONS)):
        # TODO: Actually prune old metadata files
        pass

def _download_bootstrap_modulemd():
    from ._depchase import make_pool, get_rpms_for_srpms
    print("Downloading build bootstrap module details")
    _download_one_file(_F27_BOOTSTRAP_MODULEMD, _BOOTSTRAP_MODULEMD)
    # TODO: Cache the modulemd file hash, and only regenerate the cache
    # if that has changed
    mmd = modulemd.ModuleMetadata()
    mmd.load(_BOOTSTRAP_MODULEMD)
    pool = make_pool("x86_64")
    bootstrap_rpms = {}
    rpms = get_rpms_for_srpms(pool, mmd.components.rpms)
    for rpmname in rpms:
        bootstrap_rpms[rpmname] = "bootstrap"
    for srpmname in mmd.components.rpms:
        bootstrap_rpms[srpmname] = "bootstrap"
    with open(_BOOTSTRAP_REVERSE_LOOKUP_CACHE, "w") as cachefile:
        json.dump(bootstrap_rpms, cachefile)
    print(f"  Added {_BOOTSTRAP_REVERSE_LOOKUP_CACHE} to cache")

def download_repo_metadata():
    """Downloads the latest repo metadata"""
    for repo_definition in _ALL_REPOS:
        _download_metadata_files(repo_definition)
    _download_bootstrap_modulemd()

_SRPM_REVERSE_LOOKUP = {}  # SRPM name : module name
_RPM_REVERSE_LOOKUP = {}   # RPM name : module name
_BOOTSTRAP_REVERSE_LOOKUP = {}
def _populate_module_reverse_lookup():
    # TODO: Cache the reverse mapping as a JSON file, as with _BOOTSTRAP_REVERSE_LOOKUP_CACHE
    if _RPM_REVERSE_LOOKUP:
        return
    metadata_dir = os.path.join(_x86_64_MODULE_INFO.local_cache_path)
    repomd_fname = os.path.join(metadata_dir, "repodata", "repomd.xml")
    repomd_xml = etree.parse(repomd_fname)
    repo_relative_modulemd = _read_repomd_location(repomd_xml, "modules")
    if repo_relative_modulemd is None:
        raise RuntimeError(f"No 'modules' entry found in {repomd_fname}. Is the metadata for a non-modular repo?")
    repo_modulemd_fname = os.path.join(metadata_dir, repo_relative_modulemd)
    with gzip.open(repo_modulemd_fname, "r") as modules_yaml_gz:
        modules_yaml = modules_yaml_gz.read()
    modules = modulemd.loads_all(modules_yaml)
    for module in modules:
        for srpmname in module.components.rpms:
            # This isn't entirely valid, as it doesn't account for multiple
            # modules that include the same source RPM with different output
            # filters (e.g. python3-ecosystem vs python2-ecosystem)
            _SRPM_REVERSE_LOOKUP[srpmname] = module.name
        for rpmname in module.artifacts.rpms:
            # This is only valid for module sets that are guaranteed to be
            # fully coinstallable, and hence only allow any given RPM to be
            # published by at most one module
            rpmprefix = rpmname.split(":", 1)[0].rsplit("-", 1)[0]
            _RPM_REVERSE_LOOKUP[rpmprefix] = module.name
    # Read the extra RPM bootstrap metadata
    with open(_BOOTSTRAP_REVERSE_LOOKUP_CACHE, "r") as cachefile:
        _BOOTSTRAP_REVERSE_LOOKUP.update(json.load(cachefile))


def get_module_for_rpm(rpm_name, *, allow_bootstrap=False):
    result = _RPM_REVERSE_LOOKUP.get(rpm_name)
    if allow_bootstrap and result is None:
        _BOOTSTRAP_REVERSE_LOOKUP.get(rpm_name)
    return result

class Repo(object):
    def __init__(self, name, metadata_path):
        self.name = name
        self.metadata_path = metadata_path
        self.handle = None
        self.cookie = None
        self.extcookie = None
        self.srcrepo = None

    @staticmethod
    def calc_cookie_fp(fp):
        chksum = solv.Chksum(solv.REPOKEY_TYPE_SHA256)
        chksum.add("1.1")
        chksum.add_fp(fp)
        return chksum.raw()

    @staticmethod
    def calc_cookie_ext(f, cookie):
        chksum = solv.Chksum(solv.REPOKEY_TYPE_SHA256)
        chksum.add("1.1")
        chksum.add(cookie)
        chksum.add_fstat(f.fileno())
        return chksum.raw()

    def cachepath(self, ext=None):
        path = "{}-{}".format(self.name.replace(".", "_"), self.metadata_path)
        if ext:
            path = "{}-{}.solvx".format(path, ext)
        else:
            path = "{}.solv".format(path)
        return os.path.join(CACHEDIR, path.replace("/", "_"))

    def usecachedrepo(self, ext, mark=False):
        try:
            repopath = self.cachepath(ext)
            f = open(repopath, "rb")
            f.seek(-32, os.SEEK_END)
            fcookie = f.read(32)
            if len(fcookie) != 32:
                return False
            cookie = self.extcookie if ext else self.cookie
            if cookie and fcookie != cookie:
                return False
            if not ext:
                f.seek(-32 * 2, os.SEEK_END)
                fextcookie = f.read(32)
                if len(fextcookie) != 32:
                    return False
            f.seek(0)
            f = solv.xfopen_fd(None, f.fileno())
            flags = 0
            if ext:
                flags = solv.Repo.REPO_USE_LOADING | solv.Repo.REPO_EXTEND_SOLVABLES
                if ext != "DL":
                    flags |= solv.Repo.REPO_LOCALPOOL
            if not self.handle.add_solv(f, flags):
                return False
            if not ext:
                self.cookie = fcookie
                self.extcookie = fextcookie
            if mark:
                # no futimes in python?
                try:
                    os.utime(repopath, None)
                except Exception:
                    pass
        except IOError:
            return False
        return True

    def writecachedrepo(self, ext, repodata=None):
        tmpname = None
        try:
            if not os.path.isdir(CACHEDIR):
                os.mkdir(CACHEDIR, 0o755)
            fd, tmpname = tempfile.mkstemp(prefix=".newsolv-", dir=CACHEDIR)
            os.fchmod(fd, 0o444)
            f = os.fdopen(fd, "wb+")
            f = solv.xfopen_fd(None, f.fileno())
            if not repodata:
                self.handle.write(f)
            elif ext:
                repodata.write(f)
            else:
                # rewrite_repos case, do not write stubs
                self.handle.write_first_repodata(f)
            f.flush()
            if not ext:
                if not self.extcookie:
                    self.extcookie = self.calc_cookie_ext(f, self.cookie)
                f.write(self.extcookie)
            if not ext:
                f.write(self.cookie)
            else:
                f.write(self.extcookie)
            f.close
            if self.handle.iscontiguous():
                # switch to saved repo to activate paging and save memory
                nf = solv.xfopen(tmpname)
                if not ext:
                    # main repo
                    self.handle.empty()
                    flags = solv.Repo.SOLV_ADD_NO_STUBS
                    if repodata:
                        # rewrite repos case, recreate stubs
                        flags = 0
                    if not self.handle.add_solv(nf, flags):
                        sys.exit("internal error, cannot reload solv file")
                else:
                    # extension repodata
                    # need to extend to repo boundaries, as this is how
                    # repodata.write() has written the data
                    repodata.extend_to_repo()
                    flags = solv.Repo.REPO_EXTEND_SOLVABLES
                    if ext != "DL":
                        flags |= solv.Repo.REPO_LOCALPOOL
                    repodata.add_solv(nf, flags)
            os.rename(tmpname, self.cachepath(ext))
        except (OSError, IOError):
            if tmpname:
                os.unlink(tmpname)

    def load(self, pool):
        assert not self.handle
        self.handle = pool.add_repo(self.name)
        self.handle.appdata = self
        f = self.read_repo_metadata("repodata/repomd.xml", False, None)
        if not f:
            self.handle.free(True)
            self.handle = None
            return False
        self.cookie = self.calc_cookie_fp(f)
        if self.usecachedrepo(None, True):
            return True
        self.handle.add_repomdxml(f)
        fname, fchksum = self.find("primary")
        if not fname:
            return False
        f = self.read_repo_metadata(fname, True, fchksum)
        if not f:
            return False
        self.handle.add_rpmmd(f, None)
        self.add_exts()
        self.writecachedrepo(None)
        # Must be called after writing the repo
        self.handle.create_stubs()
        return True

    def read_repo_metadata(self, fname, uncompress, chksum):
        f = open("{}/{}".format(self.metadata_path, fname))
        return solv.xfopen_fd(fname if uncompress else None, f.fileno())

    def find(self, what):
        di = self.handle.Dataiterator_meta(solv.REPOSITORY_REPOMD_TYPE, what, solv.Dataiterator.SEARCH_STRING)
        di.prepend_keyname(solv.REPOSITORY_REPOMD)
        for d in di:
            dp = d.parentpos()
            filename = dp.lookup_str(solv.REPOSITORY_REPOMD_LOCATION)
            chksum = dp.lookup_checksum(solv.REPOSITORY_REPOMD_CHECKSUM)
            if filename:
                if not chksum:
                    print("No {} file checksum!".format(filename))
                return filename, chksum
        return None, None

    def add_ext_keys(self, ext, repodata, handle):
        if ext == "FL":
            repodata.add_idarray(handle, solv.REPOSITORY_KEYS, solv.SOLVABLE_FILELIST)
            repodata.add_idarray(handle, solv.REPOSITORY_KEYS, solv.REPOKEY_TYPE_DIRSTRARRAY)
        else:
            raise NotImplementedError

    def add_ext(self, repodata, what, ext):
        filename, chksum = self.find(what)
        if not filename:
            return
        handle = repodata.new_handle()
        repodata.set_poolstr(handle, solv.REPOSITORY_REPOMD_TYPE, what)
        repodata.set_str(handle, solv.REPOSITORY_REPOMD_LOCATION, filename)
        repodata.set_checksum(handle, solv.REPOSITORY_REPOMD_CHECKSUM, chksum)
        self.add_ext_keys(ext, repodata, handle)
        repodata.add_flexarray(solv.SOLVID_META, solv.REPOSITORY_EXTERNAL, handle)

    def add_exts(self):
        repodata = self.handle.add_repodata()
        self.add_ext(repodata, "filelists", "FL")
        repodata.internalize()

    def load_ext(self, repodata):
        repomdtype = repodata.lookup_str(solv.SOLVID_META, solv.REPOSITORY_REPOMD_TYPE)
        if repomdtype == "filelists":
            ext = "FL"
        else:
            assert False
        if self.usecachedrepo(ext):
            return True
        filename = repodata.lookup_str(solv.SOLVID_META, solv.REPOSITORY_REPOMD_LOCATION)
        filechksum = repodata.lookup_checksum(solv.SOLVID_META, solv.REPOSITORY_REPOMD_CHECKSUM)
        f = self.read_repo_metadata(filename, True, filechksum)
        if not f:
            return False
        if ext == "FL":
            self.handle.add_rpmmd(f, "FL", solv.Repo.REPO_USE_LOADING | solv.Repo.REPO_EXTEND_SOLVABLES | solv.Repo.REPO_LOCALPOOL)
        self.writecachedrepo(ext, repodata)
        return True

    def updateaddedprovides(self, addedprovides):
        if self.handle.isempty():
            return
        # make sure there's just one real repodata with extensions
        repodata = self.handle.first_repodata()
        if not repodata:
            return
        oldaddedprovides = repodata.lookup_idarray(solv.SOLVID_META, solv.REPOSITORY_ADDEDFILEPROVIDES)
        if not set(addedprovides) <= set(oldaddedprovides):
            for id in addedprovides:
                repodata.add_idarray(solv.SOLVID_META, solv.REPOSITORY_ADDEDFILEPROVIDES, id)
            repodata.internalize()
            self.writecachedrepo(None, repodata)

def load_stub(repodata):
    repo = repodata.repo.appdata
    if repo:
        return repo.load_ext(repodata)
    return False

def setup_repos():

    srcrepo = Repo("f27-source", _SOURCE_PACKAGE_INFO.local_cache_path)
    repo = Repo("f27", _x86_64_PACKAGE_INFO.local_cache_path)
    repo.srcrepo = srcrepo
    updates_srcrepo = Repo("f27-updates-source", _SOURCE_UPDATES_INFO.local_cache_path)
    updates_repo = Repo("f27-updates", _x86_64_UPDATES_INFO.local_cache_path)
    updates_repo.srcrepo = updates_srcrepo
    return [repo, srcrepo, updates_repo, updates_srcrepo]
