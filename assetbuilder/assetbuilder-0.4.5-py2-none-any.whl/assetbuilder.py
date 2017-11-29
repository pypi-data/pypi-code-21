# Copyright 2017 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
from collections import defaultdict
from collections import namedtuple
from email.utils import parsedate_tz, mktime_tz
from wsgiref.util import application_uri
import hashlib
import logging
import mimetypes
import os
import pathlib
import subprocess
import time

import portalocker

logger = logging.getLogger(__name__)
ustr = type(u'')

if ustr is str:
    def getenv(environ, key, default='', enc='UTF-8'):
        return environ.get(key, default).encode('iso-8859-1').decode(enc)

else:
    def getenv(environ, key, default='', enc='UTF-8'):
        return environ.get(key, default).decode(enc)


BuildCommand = namedtuple('BuildCommand', 'command chdir cwd shell env')


class AssetBuilder(object):

    def __init__(self, baseurl, directory, depdirs=None, autobuild=False):
        """
        :param baseurl: base url for serving assets.
                        this must correspond to the URL the AssetBuilder WSGI
                        application is mounted on.
                        If only the path section is given, a fully qualified
                        URL will be generated from the WSGI environ when
                        generating asset urls with AssetBuilder.urlfor.
        :param directory: directory to search for asset files
        :param depdirs: list of directories to search for asset dependencies
        """

        if not baseurl.endswith('/'):
            baseurl += '/'
        self.baseurl = baseurl
        self.depdirs = [pathlib.Path(d) for d in (depdirs or [directory])]
        self.directory = pathlib.Path(directory).resolve()
        self.autobuild = autobuild

        #: Mapping of asset virtual paths to asset Path
        self.served = {}

        #: Mapping of asset virtual paths to dependencies
        self.dependencies = {}
        self.dependencies_cache = {}

        #: Mapping of asset virtual paths to a set of files to exclude
        #: from the dependency list
        self.negative_deps = defaultdict(set)

        #: Mapping of tags to asset virtual paths
        self.tags = {}

        #: Mapping of asset virtual paths to (mtime, cachebuster querystring)
        self.cachebusters = {}

        #: Mapping of asset virtual paths to BuildCommand objects
        self.build_commands = {}

        #: List of files which are considered dependencies for *all* assets
        self.global_deps = []

        #: Set of asset virtual paths which have never successfully been built
        #: Membership of this set prevents the assetbuilder from retrying
        #: the build command (which otherwise would run on every request,
        #: potentially causing signifant server load).
        self.unbuildable = set()

        self.default_build_command = None
        self.rebuild_all_command = None

    def set_default_build_command(self,
                                  command,
                                  chdir=False,
                                  cwd=None,
                                  env=None,
                                  shell=True):
        self.default_build_command = BuildCommand(
            command, chdir, cwd, shell, env)

    def set_rebuild_all_command(self,
                                command,
                                cwd=None,
                                env=None,
                                shell=True):
        """
        Configure a command to rebuild all assets in one go.
        If this is left unset, each registered asset file will be rebuilt
        individually.
        """
        self.rebuild_all_command = BuildCommand(
            command, False, cwd, shell, env)

    def add_path(self, tag, p, deps=[], **kwargs):
        p = p.lstrip('/')

        def generate_deps():
            inc_globs = (d for d in deps if not d.startswith('!'))
            exc_globs = (d[1:] for d in deps if d.startswith('!'))

            expand_globs = lambda globs: {f
                                          for pattern in globs
                                          for d in self.depdirs
                                          for f in d.glob(pattern)}
            return (expand_globs(self.global_deps) |
                    (expand_globs(inc_globs) - expand_globs(exc_globs)))

        self.served[p] = self.directory.joinpath(p)
        self.dependencies[p] = generate_deps

        self.tags.setdefault(tag, []).append(p)
        if 'command' in kwargs:
            self.build_commands[p] = BuildCommand(
                command=kwargs.pop('command'),
                chdir=kwargs.pop('chdir', False),
                cwd=kwargs.pop('cwd', None),
                env=kwargs.pop('env', None),
                shell=kwargs.pop('shell', True))
        else:
            self.build_commands[p] = self.default_build_command

    def add_global_dep(self, dep):
        self.global_deps.append(dep)

    def update_cachebuster(self, assetfile):
        self.cachebusters[assetfile] = self.calculate_cachebuster(assetfile)

    def urlfor(self, assetfile, baseurl):
        return baseurl + assetfile + '?' + self.get_cachebuster(assetfile)

    def urls(self, tag, environ=None):
        if environ is not None and '://' not in self.baseurl:
            baseurl = (application_uri(environ).rstrip('/') +
                       '/' +
                       self.baseurl.lstrip('/'))
        else:
            baseurl = self.baseurl
        for af in self.tags[tag]:
            yield self.urlfor(af, baseurl)

    def paths(self, tag):
        return (self.served[virtual] for virtual in self.tags[tag])

    def rebuild_all(self, clean=False):
        """
        Trigger a rebuild of all asset files.

        :param clean: If ``True``, unlink asset files before
                      rebuilding (ie this will DELETE the file).

        If the ``rebuild_all_command`` property is set, this will be used to
        build all assets in a single step. Otherwise the build command for each
        registered asset will be called in turn.

        This method also clears the ``unbuildable`` set, causing previously
        unbuilt assets to be retried.
        """
        logger.debug("Getting build lock before rebuilding all")
        with portalocker.Lock('.assetbuilder.lock'):
            self.unbuildable.clear()
            if clean:
                for assetfile, path in self.served.items():
                    logger.info("Unlinking %r", path)
                    try:
                        os.unlink(str(path))
                    except OSError:
                        pass

            if self.rebuild_all_command:
                self._run_build_command(self.rebuild_all_command)
            else:
                for assetfile, path in self.served.items():
                    self.ensure_up_to_date(assetfile, lock=False)

    def ensure_up_to_date(self, assetfile, lock=None):
        """
        Ensures that the given assetfile is up to date.
        """
        logger.debug("Checking %r is up to date", assetfile)

        if assetfile in self.unbuildable:
            logger.debug("%r is marked as unbuildable", assetfile)
            return

        if lock:
            logger.debug("Getting build lock for %r", assetfile)
            with portalocker.Lock('.assetbuilder.lock'):
                self.ensure_up_to_date(assetfile, False)
                return

        if assetfile in self.unbuildable:
            return
        path = self.served[assetfile]
        if not path.exists():
            self._make(assetfile)
            if not path.exists():
                logger.warn("Tried to build %r, "
                            "but no file was created!\n"
                            "    build_command is %r",
                            path, self.build_commands[assetfile])

                self.unbuildable.add(assetfile)
            self.update_cachebuster(assetfile)
            return

        mtime = path.stat().st_mtime
        try:
            deps = self.dependencies_cache[assetfile]
        except KeyError:
            deps = self.dependencies[assetfile]()
            self.dependencies_cache[assetfile] = deps
        deps = deps - self.negative_deps[assetfile]

        for d in sorted(deps):
            if d.stat().st_mtime > mtime:
                logger.info("%r is newer than %r, rebuilding", d, path)
                success = self._make(assetfile)
                if success and path.stat().st_mtime == mtime:
                    logger.warn("Tried to build %r, "
                                "but file was not updated!\n", path)
                    logger.info("Removing %r from dependency list for %r",
                                d, path)
                    self.negative_deps[assetfile].add(d)
                break
            else:
                logger.debug("%s: dependency %r is unchanged", assetfile, d)

        self.update_cachebusters()

    def update_cachebusters(self):
        """
        Check all cachebusters and update any that are out of date
        """
        for assetfile, path in self.served.items():
            try:
                mtime, _ = self.cachebusters[assetfile]
            except KeyError:
                mtime = 0
            try:
                if mtime < path.stat().st_mtime:
                    self.update_cachebuster(assetfile)
            except FileNotFoundError:
                pass

    def _make(self, assetfile):
        path = self.served[assetfile]
        build_command = self.build_commands[assetfile]
        logger.info("Building %r", path)
        return self._run_build_command(build_command, path)

    def _run_build_command(self, build_command, relpath=None):
        if relpath and build_command.chdir:
            cwd = str(relpath.parent)
        else:
            cwd = build_command.cwd or os.getcwd()

        logger.info("Calling: %r in %r", build_command.command, cwd)
        returncode = subprocess.call([build_command.command],
                                     shell=build_command.shell,
                                     cwd=cwd,
                                     env=build_command.env)
        if returncode != 0:
            logger.error("Command %r exited with status %r "
                         "(cwd=%s; env=%r)",
                         build_command.command,
                         returncode,
                         cwd,
                         build_command.env)
            return False
        return True

    def get_cachebuster(self, assetfile):
        if self.autobuild:
            self.ensure_up_to_date(assetfile)
        if assetfile not in self.cachebusters:
            self.update_cachebuster(assetfile)
        return self.cachebusters.get(assetfile, [0, ''])[1]

    def calculate_cachebuster(self, assetfile):
        mtime = 0
        try:
            mtime = self.served[assetfile].stat().st_mtime
            h = hashlib.sha1()
            with self.served[assetfile].open('rb') as f:
                while True:
                    chunk = f.read(8192)
                    if chunk == b'':
                        break
                    h.update(chunk)
            return mtime, h.hexdigest()[:8]
        except OSError:
            return mtime, ''

    def __call__(self, environ, start_response):
        path = getenv(environ, 'PATH_INFO')
        path = path.lstrip('/')
        if path.strip('/') == 'update' and self.autobuild:
            qs = environ.get('QUERY_STRING', '')
            self.rebuild_all(clean=(qs.lower() == 'clean'))
            start_response('204 no content', [])
            return []
        p = None
        if path in self.served:
            p = self.served[path]
            if self.autobuild:
                self.ensure_up_to_date(path)
        else:
            try:
                p = self.directory.joinpath(path).resolve()
                if not p.is_file():
                    p = None
            except OSError:
                p = None

        if p is None:
            start_response('404 not found',
                           [('Content-Type', 'text/plain')])
            return [b'not found.']

        return serve_static_file(p, environ, start_response)


def serve_static_file(path, environ, start_response, bufsize=8192):
    """
    Serve a static file located at ``path``.
    """

    try:
        stat = path.stat()
    except OSError:
        logger.debug("Could not stat %r", path)
        start_response('404 not found', [('Content-Type', 'text/plain')])
        return [b"not found."]

    mod_since = environ.get('HTTP_IF_MODIFIED_SINCE')
    if mod_since is not None:
        try:
            mod_since = mktime_tz(parsedate_tz(mod_since))
        except (TypeError, OverflowError):
            start_response('400 bad request', [('Content-Type', 'text/plain')])
            return ["invalid if-modified-since value."]

        if int(stat.st_mtime) <= int(mod_since):
            start_response('304 not modified', [])
            return []

    ct = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'

    try:
        file = path.open('rb')
    except IOError:
        start_response('403 forbidden', [('Content-Type', 'text/plain')])
        return ["access denied."]

    headers = [('Content-Type', ct),
               ('Content-Length', str(stat.st_size)),
               ('Cache-Control', 'max-age=700000000,public'),
               ('Date', format_date(time.gmtime())),
               ('Last-Modified', format_date(time.gmtime(stat.st_mtime))),
               ('Expires', 'Wed, 20 Jan 2038 00:00:00 GMT'),
               ]

    file_wrapper = environ.get('wsgi.file_wrapper')
    if file_wrapper is not None:
        content_iterator = lambda f=file, bufsize=bufsize: file_wrapper(f, bufsize)
    else:
        def content_iterator(f=file, bufsize=bufsize):
            try:
                while True:
                    c = f.read(bufsize)
                    if c == b'':
                        break
                    yield c
            finally:
                f.close()

    start_response('200 OK', headers)
    return content_iterator()


def format_date(utctimetuple):
    return '%s, %02d %s %04d %02d:%02d:%02d GMT' % (
        ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')[utctimetuple[6]],
        utctimetuple[2],
        ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
         'Nov', 'Dec')[utctimetuple[1] - 1],
        utctimetuple[0],
        utctimetuple[3],
        utctimetuple[4],
        utctimetuple[5],
    )
