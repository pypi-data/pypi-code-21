import configparser
import itertools
import logging
import os
import sys
import tempfile
import smartcols
import solv

from . import _repodata

log = logging.getLogger(__name__)

def setup_pool(arch, repos=()):
    pool = solv.Pool()
    #pool.set_debuglevel(2)
    pool.setarch(arch)
    pool.set_loadcallback(_repodata.load_stub)

    for repo in repos:
        repo.metadata_path = repo.metadata_path.format(arch=arch)

    for repo in repos:
        assert repo.load(pool)
        if "override" in repo.name:
            repo.handle.priority = 99

    addedprovides = pool.addfileprovides_queue()
    if addedprovides:
        for repo in repos:
            repo.updateaddedprovides(addedprovides)

    pool.createwhatprovides()

    return pool

def fix_deps(pool):
    to_fix = (
        # Weak libcrypt-nss deps due to https://github.com/openSUSE/libsolv/issues/205
        ("glibc", solv.Selection.SELECTION_NAME,
         solv.SOLVABLE_RECOMMENDS, lambda s: s.startswith("libcrypt-nss"), solv.SOLVABLE_SUGGESTS),
        # Shim is not buildable
        ("shim", solv.Selection.SELECTION_NAME | solv.Selection.SELECTION_WITH_SOURCE,
         solv.SOLVABLE_REQUIRES, lambda s: s in ("gnu-efi = 3.0w", "gnu-efi-devel = 3.0w"), None),
    )
    for txt, flags, before, func, after in to_fix:
        for s in pool.select(txt, flags).solvables():
            deps = s.lookup_deparray(before)
            fixing = [dep for dep in deps if func(str(dep))]
            for dep in fixing:
                deps.remove(dep)
                if after is not None:
                    s.add_deparray(after, dep)
            # Use s.set_deparray() once will be available
            s.unset(before)
            for dep in deps:
                s.add_deparray(before, dep)

def get_sourcepkg(p, s=None, only_name=False):
    if s is None:
        s = p.lookup_sourcepkg()[:-4]
    if only_name:
        return s
    # Let's try to find corresponding source
    sel = p.pool.select(s, solv.Selection.SELECTION_CANON | solv.Selection.SELECTION_SOURCE_ONLY)
    sel.filter(p.repo.appdata.srcrepo.handle.Selection())
    assert not sel.isempty(), "Could not find source package for {}".format(s)
    solvables = sel.solvables()
    assert len(solvables) == 1
    return solvables[0]

def print_transaction(pool, transaction):
    candq = transaction.newpackages()
    if log.getEffectiveLevel() <= logging.INFO:
        tb = smartcols.Table()
        tb.title = "DEPENDENCY INFORMATION"
        cl = tb.new_column("INFO")
        cl.tree = True
        cl_match = tb.new_column("MATCH")
        for p in candq:
            ln = tb.new_line()
            ln[cl] = str(p)
            for dep in p.lookup_deparray(solv.SOLVABLE_REQUIRES):
                lns = tb.new_line(ln)
                lns[cl] = str(dep)
                matches = set(s for s in candq if s.matchesdep(solv.SOLVABLE_PROVIDES, dep))
                if not matches and str(dep).startswith("/"):
                    # Append provides by files
                    # TODO: use Dataiterator for getting filelist
                    matches = set(s for s in pool.select(str(dep), solv.Selection.SELECTION_FILELIST).solvables() if s in candq)
                # It was possible to resolve set, so something is wrong here
                assert matches
                first = True
                for m in matches:
                    if first:
                        lnc = lns
                    else:
                        lnss = tb.new_line(lns)
                        lnc = lnss
                        first = False
                    lnc[cl_match] = str(m)
        log.info(tb)

def _solve(solver, pkgnames):
    """Given a set of package names, returns a list of solvables to install"""
    pool = solver.pool

    # We have to =(
    fix_deps(pool)

    jobs = []
    # Initial jobs, no conflicting packages
    for n in pkgnames:
        if "." in n:
            search_criteria = solv.Selection.SELECTION_CANON
        else:
            search_criteria = solv.Selection.SELECTION_NAME | solv.Selection.SELECTION_DOTARCH
        sel = pool.select(n, search_criteria)
        if sel.isempty():
            log.warn("Could not find package for {}".format(n))
            continue
        jobs += sel.jobs(solv.Job.SOLVER_INSTALL)
    problems = solver.solve(jobs)
    if problems:
        for problem in problems:
            log.warn(problem)

    print_transaction(pool, solver.transaction())
    result = set()
    for s in solver.transaction().newpackages():
        if s.name.startswith("fedora-release"):
            # Relying on the F27 metadata injects irrelevant fedora-release deps
            continue
        if s.arch in ("src", "nosrc"):
            continue
        # Ensure the solvables don't outlive the solver that created them
        result.add(s.name)
    return result

def ensure_buildable(pool, pkgnames):
    """Given a set of solvables, returns a set of source packages & build deps"""
    # The given package set may not be installable on its own
    # That's OK, since other modules will provide those packages
    # The goal of *this* method is to report the SRPMs that need to be
    # built, and their build dependencies
    sources = set(get_srpm_for_rpm(pool, n) for n in pkgnames)
    builddeps = ensure_installable(pool, sources)
    return sources, builddeps

def make_pool(arch):
    return setup_pool(arch, _repodata.setup_repos())

_DEFAULT_HINTS = ("glibc-minimal-langpack",)

def ensure_installable(pool, pkgnames, hints=_DEFAULT_HINTS, recommendations=False):
    """Iterate over the resolved dependency set for the given packages

    *hints*:  Packages that have higher priority when more than one package
              could satisfy a dependency.
    *recommendations*: Whether or not to report recommended dependencies as well
                 as required dependencies (Default: required deps only)
    """
    if pool is None:
        pool = make_pool("x86_64")
    # Set up initial hints
    favorq = []
    for n in hints:
        sel = pool.select(n, solv.Selection.SELECTION_NAME)
        favorq += sel.jobs(solv.Job.SOLVER_FAVOR)
    pool.setpooljobs(favorq)

    solver = pool.Solver()
    if not recommendations:
        # Ignore weak deps
        solver.set_flag(solv.Solver.SOLVER_FLAG_IGNORE_RECOMMENDED, 1)

    return _solve(solver, pkgnames)

def print_reldeps(pool, pkg):
    sel = pool.select(pkg, solv.Selection.SELECTION_NAME | solv.Selection.SELECTION_DOTARCH)
    assert not sel.isempty(), "Package can't be found"
    found = sel.solvables()
    assert len(found) == 1, "More matching solvables were found, {}".format(found)
    s = found[0]

    reldep2str = {solv.SOLVABLE_REQUIRES: "requires",
                  solv.SOLVABLE_RECOMMENDS: "recommends",
                  solv.SOLVABLE_SUGGESTS: "suggests",
                  solv.SOLVABLE_SUPPLEMENTS: "supplements",
                  solv.SOLVABLE_ENHANCES: "enhances"}
    for reltype, relstr in reldep2str.items():
        for dep in s.lookup_deparray(reltype):
            print("{}: {}".format(relstr, dep))

def get_srpm_for_rpm(pool, pkg):
    sel = pool.select(pkg, solv.Selection.SELECTION_NAME | solv.Selection.SELECTION_DOTARCH)
    if sel.isempty():
        return f"unknown-component-{pkg}"
    found = sel.solvables()
    num_results = len(found)
    s = None
    if num_results == 1:
        s = found[0]
    elif num_results == 2:
        # Handle x86 32-bit vs 64-bit multilib packages
        first, second = found
        if first.arch == "x86_64" and second.arch == "i686":
            s = first
        elif first.arch == "i686" and second.arch == "x86_64":
            s = second
    if s is None:
            raise RuntimeError("More matching solvables were found, {}".format(found))
    s = found[0]

    return get_sourcepkg(s, only_name=True)

def get_rpms_for_srpms(pool, pkgnames):

    sources = set()
    for n in pkgnames:
        sel = pool.select(n, solv.Selection.SELECTION_NAME | solv.Selection.SELECTION_DOTARCH | solv.Selection.SELECTION_WITH_SOURCE)
        if not sel.isempty():
            found = sel.solvables()
            for rpm in found:
                if rpm.arch in ("src", "nosrc"):
                    sources.add(str(found[0]))
                    break
            else:
                # Multilib means we may see multiple binary RPMs with the same name
                sources.add(get_sourcepkg(rpm, only_name=True))

    # This search is O(N) where N = the number of packages in Fedora
    # so it would be nice to find a more algorithmically efficient approach
    # OTOH, we only run this when *fetching* metadata, so it isn't too bad
    result = set()
    for p in (s for s in pool.solvables if s.arch not in ("src", "nosrc")):
        if get_sourcepkg(p, only_name=True) in sources:
            result.add(p.name)
    return result
