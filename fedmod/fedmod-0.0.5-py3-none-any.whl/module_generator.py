from __future__ import absolute_import

import sys
import modulemd
import logging
import dnf
from . import _depchase, _repodata

def _name_only(rpm_name):
    name, version, release = rpm_name.rsplit("-", 2)
    return name

def _categorise_deps(all_rpm_deps, *, allow_bootstrap=False):
    module_deps = set()
    remaining_rpm_deps = set()
    for pkgname in all_rpm_deps:
        modname = _repodata.get_module_for_rpm(pkgname, allow_bootstrap=allow_bootstrap)
        if modname is not None:
            module_deps.add(modname)
        else:
            remaining_rpm_deps.add(pkgname)
    return module_deps, remaining_rpm_deps

class ModuleGenerator(object):

    def __init__(self, pkgs):
        self.pkgs = pkgs
        self.pkg = None
        self.mmd = modulemd.ModuleMetadata()

    def _calculate_dependencies(self, build_deps_iterations):
        pkgs = self.pkgs
        _repodata._populate_module_reverse_lookup()
        pool = _depchase.make_pool("x86_64")
        self.api_srpms = {_name_only(_depchase.get_srpm_for_rpm(pool, dep)) for dep in pkgs}
        run_deps = _depchase.ensure_installable(pool, pkgs)
        module_run_deps, rpm_run_deps = _categorise_deps(run_deps)
        self.module_run_deps = module_run_deps
        run_srpms, build_deps = _depchase.ensure_buildable(pool, rpm_run_deps)
        module_build_deps = set()
        resolved_build_deps = set()
        build_srpms = set()
        for i in range(build_deps_iterations+1):
            # Give up on making the module self-hosting after the requested
            # number of iterations
            new_module_build_deps, remaining_build_deps = _categorise_deps(build_deps, allow_bootstrap=True)
            module_build_deps |= new_module_build_deps
            resolved_build_deps |= (build_deps - remaining_build_deps)
            build_deps -= resolved_build_deps
            if build_deps and i < build_deps_iterations:
                new_build_srpms, remaining_build_deps = _depchase.ensure_buildable(pool, build_deps)
                build_srpms |= new_build_srpms
                resolved_build_deps |= (build_deps - remaining_build_deps)
                build_deps -= resolved_build_deps
            if not build_deps:
                break
        else:
            if build_deps_iterations:
                logging.warn(f"Failed to close out build dependencies after {build_deps_iterations} iterations")
        self.module_run_deps = module_run_deps
        self.module_build_deps = module_build_deps
        run_srpm_names = {_name_only(n) for n in run_srpms}
        build_srpm_names = {_name_only(n) for n in build_srpms}
        self.run_srpms = run_srpm_names - build_srpm_names
        self.build_srpms = build_srpm_names - run_srpm_names
        self.build_and_run_srpms = run_srpm_names & build_srpm_names
        self.unresolved_build_rpms = {n for n in build_deps}


    def _get_pkg_info(self):
        """Function loads package from dnf"""
        # TODO: Get this from the _depchase metadata, not the system metadata
        logging.info("Getting package info from DNF")
        b = dnf.Base()
        b.read_all_repos()
        b.fill_sack()
        q = b.sack.query().filter(name=self.pkgs, reponame='fedora', latest=True)
        if len(q) > 1:
            raise ValueError('Name of package is not unique')
        if len(q) == 0:
            raise ValueError('No package found in repo')
        self.pkg = q[0]

    def _save_module_md(self, output_fname):
        """
        Function writes modulemd to either stdout or the given filename
        :return:
        """

        if len(self.pkgs) == 1:
            file_name = self.pkgs[0] + '.yaml'
        else:
            file_name = "modulemd-output.yaml"
        if output_fname is not None:
            self.mmd.dump(file_name)
            print('Generated modulemd file: %r' % output_fname)
        else:
            print(self.mmd.dumps())
        return True

    def _update_module_md(self):
        """
        Function updates modulemd file with dependencies
        are information taken from SPEC file.
        :return:
        """
        self.mmd.add_module_license("MIT")

        if len(self.pkgs) == 1:
            self.mmd.summary = str(self.pkg.summary)
            self.mmd.description = str(self.pkg.description)

            # Default license for the module metadata, same as default Fedora
            # content license.

            self.mmd.add_content_license(str(self.pkg.license))

        # Declare the public API
        for pkg in self.api_srpms:
            self.mmd.api.add_rpm(pkg)
            self.mmd.components.add_rpm(pkg, "Package in api", buildorder=self._get_build_order(pkg))

        # Declare module level dependencies
        for modname in self.module_build_deps:
            self.mmd.buildrequires[modname] = "f27"
        for modname in self.module_run_deps:
            self.mmd.requires[modname] = "f27"

        # Add any other RPMs not available from existing modules as components
        for pkg in self.build_and_run_srpms:
            self.mmd.components.add_rpm(pkg, "Build and runtime dependency.", buildorder=self._get_build_order(pkg))

        for pkg in self.run_srpms:
            self.mmd.components.add_rpm(pkg, "Runtime dependency.", buildorder=self._get_build_order(pkg))

        for pkg in self.build_srpms:
            self.mmd.components.add_rpm(pkg, "Build dependency.", buildorder=self._get_build_order(pkg))
            # Filter out any build-only packages
            # TODO: This won't filter out all the RPMs, only the one matching the SRPM name
            #       See https://pagure.io/modulemd/issue/54 for discussion
            self.mmd.filter.add_rpm(pkg)

        # TODO: Emit something for non-empty self.unresolved_build_rpms
        #       rather than relying solely on the warnings emitted on stderr


    def _get_build_order(self, pkg):
        if pkg in self.mmd.api.rpms:
            return 10
        else:
            return 0

    def run(self, output_fname, build_deps_iterations):
        if len(self.pkgs) == 1:
            self._get_pkg_info()
        self._calculate_dependencies(build_deps_iterations)
        self._update_module_md()
        self._save_module_md(output_fname)
