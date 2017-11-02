# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Script&Patch Manager
# :Created:   ven 14 ago 2009 13:09:28 CEST
# :Author:    Lele Gaifax <lele@nautilus.homeip.net>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2009, 2010, 2012, 2013, 2014, 2015, 2016, 2017 Lele Gaifax
#

from __future__ import absolute_import, unicode_literals

from io import open
import logging
from os.path import dirname, relpath
import sys

from toposort import toposort_flatten

from .patch import DependencyError


if sys.version_info.major >= 3:
    basestring = str


logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


class DuplicatedScriptError(Exception):
    "Indicates that a script is not unique."


class Missing3rdPartyModule(Exception):
    "Indicates that a 3rd party module is missing"


def toposort(constraints, items):
    "Implement an API similar to SQLAlchemy's topological.sort()"

    deps = {}
    iset = set(items)
    for left, right in constraints:
        deps.setdefault(right, set()).add(left)
    for item in items:
        deps.setdefault(item, set())
    return (item for item in toposort_flatten(deps, sort=False)
            if item in iset)


class _MissingPatchesIterator(object):
    def __init__(self, manager, context, constraints, always_first, missing, always_last):
        self.manager = manager
        self.context = context
        self.constraints = constraints
        self.always_first = always_first
        self.missing = missing
        self.always_last = always_last

    def __len__(self):
        return len(self.always_first) + len(self.missing) + len(self.always_last)

    def __iter__(self):
        manager = self.manager
        context = self.context
        constraints = self.constraints
        always_first = self.always_first
        missing = self.missing
        always_last = self.always_last

        if always_first:
            logger.info("Applying execute-always-first patches...")
            for pid, rev in toposort(constraints, always_first):
                yield manager[pid]

        logger.info("Applying missing patches...")
        for pid, rev in toposort(constraints, missing):
            if (pid, rev) in missing:
                currrev = context[pid]
                patch = manager[pid]

                if currrev is None and not patch.script:
                    # This is a "placeholder" patch and it has not been applied yet
                    logger.critical("Placeholder %s has not been applied yet", patch)
                    raise DependencyError('%s is a placeholder implemented elsewhere'
                                          ' and not yet applied' % patch)

                if currrev is None or currrev < rev:
                    ignore = False
                    if patch.brings or patch.drops:
                        for depid, deprev in patch.depends:
                            currdeprev = context[depid]
                            if currdeprev is None or currdeprev != deprev:
                                logger.debug("Ignoring %s, because it depends"
                                             " on '%s@%d' which is currently"
                                             " at revision %s",
                                             patch, depid, deprev, currdeprev)
                                ignore = True
                                break
                        else:
                            for depid, deprev in patch.drops:
                                currdeprev = context[depid]
                                if currdeprev is None:
                                    logger.debug("Ignoring %s, because it drops"
                                                 " '%s' which does not exist",
                                                 patch, depid)
                                    ignore = True
                                    break
                    if not ignore:
                        yield patch
                else:
                    logger.debug("Skipping %s, already applied", patch)
            else:
                logger.debug("Skipping '%s@%d', introduced by dependencies",
                             pid, rev)

        if always_last:
            logger.info("Applying execute-always-last patches...")
            for pid, rev in toposort(constraints, always_last):
                yield manager[pid]


class PatchManager(object):
    """
    An instance of this class collects a set of patches and acts as
    a dictionary. It's able to serialize the patches taking into
    account the dependencies.
    """

    def __init__(self):
        self.db = {}

    def __getitem__(self, patchid):
        """
        Return the patch given its `patchid`, or ``None`` if it does not exist.
        """
        return self.db.get(patchid)

    def __setitem__(self, patchid, patch):
        """
        Register the given `patch` identified by `patchid`.
        """
        self.db[patchid] = patch

    def neededPatches(self, context):
        """
        Return an iterator over *not yet applied* patches, in the
        right order to satisfy their inter-dependencies.
        """

        # SA topological sort relies on objects id(), doesn't hurt with toposort
        def uniquify(t, _uniquified={}):
            return _uniquified.setdefault(t, t)

        skippedcnt = 0
        constraints = set()
        missing = []
        always_first = []
        always_last = []

        logger.debug("Collecting and ordering patches...")
        for pid, patch in self.db.items():
            if not patch.always and patch.revision == context[pid]:
                logger.debug("Skipping %s, already applied", patch)
                continue

            patch.adjustUnspecifiedRevisions(self)

            if patch.verifyConditions(context.for_language(patch.language)):
                skip = False
                if patch.brings or patch.drops:
                    for depid, deprev in patch.depends:
                        current = context[depid]
                        if current is not None and current > deprev:
                            logger.debug("Ignoring %s because it depends on"
                                         " '%s@%d', currently at version %s",
                                         patch, depid, deprev, current)
                            skip = True
                            break
                if skip:
                    skippedcnt += 1
                    continue

                this = uniquify((patch.patchid, patch.revision))
                if patch.always:
                    if patch.always == 'first':
                        always_first.append(this)
                    else:
                        always_last.append(this)
                else:
                    missing.append(this)

                for dep in patch.depends:
                    constraints.add((uniquify(dep), this))
                for preceed in patch.preceeds:
                    constraints.add((this, uniquify(preceed)))
                for bring in patch.brings:
                    constraints.add((this, uniquify(bring)))
            else:
                logger.debug("Ignoring %s, because it does not satisfy the"
                             " conditions", patch)

        return _MissingPatchesIterator(self, context, constraints,
                                       always_first, missing, always_last)


class PersistentPatchManager(PatchManager):
    """
    Patch manager that uses a Pickle/YAML/JSON/AXON file as its persistent storage.
    """

    def __init__(self, storage_path=None):
        super(PersistentPatchManager, self).__init__()
        if isinstance(storage_path, basestring):
            self.storages = [storage_path]
        else:
            self.storages = storage_path

    def save(self):
        storage_path = self.storages[0]
        if storage_path is None:
            return

        logger.debug("Writing patches to %s", storage_path)
        spendswith = storage_path.endswith
        if spendswith('.yaml') or spendswith('.json') or spendswith('.axon'):
            storage = open(storage_path, 'w', encoding='utf-8')

            # Order patches by id, both for easier lookup and to
            # avoid VCs stress

            asdicts = [self.db[sid].asdict for sid in sorted(self.db)]
            spdir = dirname(storage_path)
            for script in asdicts:
                if script.get('source'):
                    script['source'] = relpath(script['source'], spdir)

            # Optimize for size and readability: store simple
            # dictionaries, with UTF-8 encoded strings; rename
            # "patchid" to "ID", as the latter will be the first key
            # in the YAML dictionary (entries are usually sorted
            # alphabetically).

            if spendswith('.yaml'):
                try:
                    from ruamel.yaml import dump_all
                except ImportError:
                    try:
                        from yaml import dump_all
                    except ImportError:
                        raise Missing3rdPartyModule('The operation requires either'
                                                    ' “ruamel.yaml” or “PyYAML”')
                content = dump_all(asdicts, default_flow_style=False, encoding=None)
            elif spendswith('.json'):
                from json import dumps
                content = dumps(asdicts, sort_keys=True, indent=1)
                if sys.version_info.major < 3 and not isinstance(content, unicode):
                    content = content.decode('utf-8')
            else:
                try:
                    from axon import dumps
                except ImportError:
                    raise Missing3rdPartyModule('The operation requires “pyaxon”')
                content = dumps(asdicts, pretty=1)

            with open(storage_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            from pickle import dump

            with open(storage_path, 'wb') as storage:
                dump(list(self.db.values()), storage)

        logger.debug("Done writing patches")

    def load(self):
        py2 = sys.version_info.major < 3
        db = self.db = {}
        loaded_from = {}
        for storage_path in self.storages:
            logger.debug("Reading patches from %s", storage_path)
            spendswith = storage_path.endswith
            if spendswith('.yaml') or spendswith('.json') or spendswith('.axon'):
                from .patch import make_patch

                with open(storage_path, 'r', encoding='utf-8') as storage:
                    if spendswith('.yaml'):
                        try:
                            from ruamel.yaml import load_all, Loader
                        except ImportError:
                            try:
                                from yaml import load_all, Loader
                            except ImportError:
                                raise Missing3rdPartyModule('The operation requires either'
                                                            ' “ruamel.yaml” or “PyYAML”')
                        asdicts = load_all(storage.read(), Loader=Loader)
                    elif spendswith('.json'):
                        from json import loads
                        asdicts = loads(storage.read())
                    else:
                        try:
                            from axon import loads
                        except ImportError:
                            raise Missing3rdPartyModule('The operation requires “pyaxon”')
                        asdicts = loads(storage.read())

                if py2:
                    patches = []
                    for d in asdicts:
                        for i in d:
                            if isinstance(d[i], str):
                                d[i] = d[i].decode('utf-8')
                        patches.append(make_patch(d['ID'], d['script'], d))
                else:
                    patches = [make_patch(d['ID'], d['script'], d) for d in asdicts]
            else:
                from pickle import load

                with open(storage_path, 'rb') as storage:
                    patches = load(storage)

            for patch in patches:
                if patch.patchid in db:
                    existing = db[patch.patchid]
                    if not patch.script:
                        existing.depends.extend(patch.depends)
                        existing.preceeds.extend(patch.preceeds)
                    elif not existing.script:
                        db[patch.patchid] = patch
                    else:
                        logger.critical("Duplicated %s: present in %s and %s",
                                        patch, loaded_from[patch.patchid], storage_path)
                        raise DuplicatedScriptError("%s already loaded!" % patch)
                else:
                    db[patch.patchid] = patch
                loaded_from[patch.patchid] = storage_path

        logger.debug("Done reading patches")


__manager = None


def patch_manager(storage_path, overwrite=False, autosave=False):
    global __manager

    if not __manager:
        __manager = PersistentPatchManager(storage_path)
        if storage_path is not None:  # used by doctests
            if not overwrite:
                __manager.load()
            if autosave:
                import atexit
                atexit.register(__manager.save)
    return __manager
