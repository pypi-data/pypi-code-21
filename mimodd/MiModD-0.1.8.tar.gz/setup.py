import sys, os
import xml.etree.ElementTree as ET

if 'setuptools' in sys.modules:
    # setuptools got injected - presumably by pip.
    # In this case, and only then, enable installation via setuptools.
    # We do not want to use setuptools just because it is installed
    # because a pure setuptools egg-install prevents use of the MiModD
    # upgrade tool.
    from setuptools import setup, Extension
else:
    from distutils.core import setup, Extension


PKG_VERSION = '0.1.8'
PKG_INFO = {
    'name': 'MiModD',
    'version': PKG_VERSION,
    'description': 'Tools for Mutation Identification in Model Organism '
                   'Genomes using Desktop PCs',
    'author': 'Wolfgang Maier',
    'author_email': 'wolfgang.maier@biologie.uni-freiburg.de',
    'url': 'http://sourceforge.net/projects/mimodd/',
    'download_url': 'http://sourceforge.net/projects/mimodd/',
    'license': 'GPL',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        ],
    }


# compute paths to package components
HERE = os.path.abspath(os.path.dirname(__file__))
SNAP_SOURCE = os.path.join(HERE, 'snap')
SAMTOOLS_SOURCES = os.path.join(HERE, 'pysam')
SAMTOOLS_LEGACY = os.path.join(SAMTOOLS_SOURCES, 'samtools')
SAMTOOLS_1_0 = os.path.join(SAMTOOLS_SOURCES, 'samtools-1.x')
BCFTOOLS_1_0 = os.path.join(SAMTOOLS_SOURCES, 'bcftools-1.x')
HTSLIB_1_0 = os.path.join(SAMTOOLS_SOURCES, 'htslib-1.x')
PYSAM = os.path.join(SAMTOOLS_SOURCES, 'pysam')
SCRIPTS = os.path.join(HERE, 'scr')
PY_LIB = os.path.join(HERE, 'lib', 'MiModD')
GALAXY_DATA = os.path.join(HERE, 'galaxy_data')
GALAXY_WRAPPERS = os.path.join(GALAXY_DATA, 'mimodd')
GALAXY_TMP_DEST = os.path.join(HERE, 'lib', 'MiModD', 'galaxy_data')
WRAPPERS_TMP_DEST = os.path.join(GALAXY_TMP_DEST, 'mimodd')
EXECUTABLES_TMP_DEST = os.path.join(HERE, 'lib', 'MiModD' , 'bin')
EXECUTABLES = ['samtools', 'bcftools', 'snap', 'mimodd']
LOG_FILE = os.path.join(HERE, 'setup.log')


# Add package description from README file to PKG_INFO.
# Encoding logic throughout this file:
# When we manipulate package source files,
# we read and write utf-8 since this is what we distribute.
# Only the installation log file is using the system's default encoding
# for the convenience of the user.
with open(os.path.join(HERE, 'README.txt'), 'r', encoding='utf-8') as file:
    PKG_INFO.update(long_description=file.read())


PKG_LAYOUT = {
    'packages': [
        'MiModD',
        'MiModD.install_utils',
        'MiModD.pysam',
        'MiModD.pysam.include',
        'MiModD.pysam.include.samtools',
        'MiModD.pysam.include.samtools.bcftools'
        ],
    'package_dir': {
        '': 'lib',
        'MiModD.install_utils': 'install_utils',
        'MiModD.pysam': 'pysam/pysam',
        'MiModD.pysam.include.samtools':'pysam/samtools'
        },
    'package_data': {
        '': ['bin/*',
             '../templates/*',
             'galaxy_data/*.xml',
             'galaxy_data/mimodd/*.xml',
             'galaxy_data/mimodd/test-data/*',
             '../help_topics/*',
             '.cfg',
             '.__first_run__'],
        'MiModD.pysam' : ['*.pxd', '*.h'],
        'MiModD.install_utils' : ['*.zip',
                                  '*.pem',
                                  'setuptools*-info/*']
        },
    'scripts': ['scr/mimodd'],
    'ext_modules': [
        Extension(
            name="MiModD.pysam.csamtools",              
            sources=[
                os.path.join(PYSAM, x) for x in ('csamtools.c', 'pysam_util.c')
                ], 
            library_dirs=[],
            include_dirs=[SAMTOOLS_LEGACY,
                          os.path.join(SAMTOOLS_SOURCES, 'pysam')],
            libraries=[ "z", ],
            language="c",
            # pysam code is not ISO-C90 compliant,
            # so ensure it compiles independently of default compiler flags.
            extra_compile_args=["-Wno-error=declaration-after-statement"],
            define_macros = [('_FILE_OFFSET_BITS','64'),
                             ('_USE_KNETFILE','')],
            )
        ],
    }


#+++++++ custom build/install code ++++++++++

import glob
import shutil
import fnmatch
import stat
import subprocess
import contextlib

from distutils.core import Command
from distutils.command.build import build as _build
from distutils.command.build_py import build_py as _build_py
from distutils.command.build_ext import build_ext as _build_ext
from distutils.command.build_scripts import build_scripts as _build_scripts
from distutils.command.install_lib import install_lib as _install_lib
from distutils.command.clean import clean as _clean


class build (_build):
    """Orchestrate the MiModD custom build process.

    Triggers the custom build_dep and build_galaxy_data phases,
    which we need to run before build_py, then delegates to the standard
    build process.
    """

    sub_commands = [('build_dep', None),
                    ('build_galaxy_data', None),
                    ('build_scripts', None)
                    ] + [c for c in _build.sub_commands
                         if c[0] != 'build_scripts']

    def run (self):
        print()
        print()
        print('Going to build MiModD version {0}.'.format(PKG_VERSION))
        print()
        print('Please be patient while the installer is building installation '
              'components.')
        print('This may take a minute or two.')
        print()
        _build.run(self)


class build_dep (Command):
    """Custom builder for MiModD's wrapped C/C++ dependencies."""

    description = 'build wrapped dependencies of MiModD'
    user_options = []
    
    def initialize_options (self):
        pass

    def finalize_options (self):
        pass
    
    def run (self):
        if not os.path.isdir(EXECUTABLES_TMP_DEST):
            os.mkdir(EXECUTABLES_TMP_DEST)
            
        # compile samtools, bcftools and snap from source
        # using their own Makefiles
        for sourcedir, command, toolname in zip(
            (HTSLIB_1_0, SAMTOOLS_1_0, BCFTOOLS_1_0, SNAP_SOURCE),
            (['make'], ['make', 'HTSDIR=' + HTSLIB_1_0],
             ['make', 'HTSDIR=' + HTSLIB_1_0], ['make']), 
            ('htslib', 'samtools', 'bcftools', 'snap')
            ):
            print('Building {0} ..'.format(toolname), end = ' ')
            with open(LOG_FILE, 'a') as log:
                p = subprocess.Popen(
                    command, cwd=sourcedir, stdout=log, stderr=log)
                if p.wait():
                    print('FAILED!')
                    raise MiModDInstallationError(
                        'Building step failed. Aborting.')
                else:
                    print('Succeeded.')
                
        # copy all binaries to a temporary 'bin' directory to include 
        # in the build         
        shutil.copy(os.path.join(SAMTOOLS_1_0, 'samtools'),
                    EXECUTABLES_TMP_DEST)
        shutil.copy(os.path.join(BCFTOOLS_1_0, 'bcftools'),
                    EXECUTABLES_TMP_DEST)
        shutil.copy(os.path.join(SNAP_SOURCE, 'snap'), EXECUTABLES_TMP_DEST)

        print('All source compilation successful.')


class build_galaxy_data (Command):
    """Custom builder that prepares MiModD's Galaxy wrappers for installation."""

    description = 'build .xml files for integration of MiModD into Galaxy'
    user_options = []
    
    def initialize_options (self):
        pass

    def finalize_options (self):
        pass

    def run (self):
        # Make sure we start with a clean build environment or trying
        # to copy the Galaxy data directory tree could fail.
        shutil.rmtree(GALAXY_TMP_DEST, ignore_errors=True)
        # copy all Galaxy data
        shutil.copytree(
            GALAXY_DATA, GALAXY_TMP_DEST, copy_function=shutil.copy
            )

        # create a copy of galaxy tool wrapper macro file
        # (overwriting the file just copied above)
        # with the stated required MiModD version changed to a
        # unique identifier of MiModD manual installations.
        macro_file = 'macros.xml'
        with open(os.path.join(GALAXY_WRAPPERS, macro_file),
                  'r', encoding='utf-8') as wrapper_in:
            macro_xml = ET.parse(wrapper_in)

        for elem in macro_xml.getroot().findall('token'):
            if elem.get('name') == '@MIMODD_VERSION_REQUIRED@':
                if elem.text != PKG_VERSION:
                    raise RuntimeError(
                        'Version mismatch between package and tool wrappers '
                        'detected! Aborting ...'
                        )
                elem.text = 'externally_managed'
                break
        else:
            raise RuntimeError(
                'Compromised version requirement line in Galaxy tool wrapper '
                'macro file! Aborting ...'
                )

        with open(os.path.join(WRAPPERS_TMP_DEST, macro_file),
                  'wb') as wrapper_out:
            macro_xml.write(wrapper_out)
            

class build_py (_build_py):
    def run (self):
        # Copy the first run code.
        # By doing so we can make the copied file part of the package data,
        # which ensures it gets removed by pip when uninstalling the package.
        shutil.copy(os.path.join(PY_LIB, '__first_run__.py'),
                    os.path.join(PY_LIB, '.__first_run__'))

        with open(LOG_FILE, 'a') as log:
            with redirect_output_streams(log):
                _build_py.run(self)


class build_ext (_build_ext):
    """MiModD custom source builder."""
    
    # Prepares all required binaries of wrapped software and
    # the modified samtools C files required by pysam before 
    # calling the standard build.

    def run (self):
        # adjust samtools source files before building pysam                
        self.prepare_ext()
        
        print('Building pysam ...',
              end=' ')
        with open(LOG_FILE, 'a') as log: 
            with redirect_output_streams(log):
                try:
                    _build_ext.run (self)
                except:
                    raise MiModDInstallationError('Failed. Aborting.')
        print('Succeeded.')
        print()

    def prepare_ext (self):        
        # prepare pysam part of installation
        # modified from pysam's setup.py
        # redirect stderr to pysamerr and replace bam.h with a stub.
        print('Preparing pysam for building ..', end=' ')        
        SAMTOOLS_EXCLUDE = ("bamtk.c", "razip.c", "bgzip.c", 
                     "main.c", "calDepth.c", "bam2bed.c",
                     "wgsim.c", "md5fa.c", "maq2sam.c",
                     "bamcheck.c",
                     "chk_indel.c")
        for filename in locate('*.c', SAMTOOLS_LEGACY):
            if os.path.basename(filename) in SAMTOOLS_EXCLUDE: continue
            if not filename or filename.endswith('.pysam.c'): continue
            dest = filename + '.pysam.c'
            if not os.path.exists(dest):
                with open(filename, encoding='utf-8') as infile:
                    with open(dest, 'w', encoding='utf-8') as outfile:
                        outfile.write('#include "pysam.h"\n\n')
                        outfile.writelines(
                            line.replace('stderr', 'pysamerr')
                            for line in infile)
        pysam_h_file = os.path.join(SAMTOOLS_LEGACY, "pysam.h")
        if not os.path.exists(pysam_h_file):
            with open(pysam_h_file, 'w', encoding='utf-8') as outfile:
                outfile.write(
"""#ifndef PYSAM_H
#define PYSAM_H
#include "stdio.h"
extern FILE * pysamerr;
#endif
""")
        # add the newly created files to the list of samtools Extension
        # source files
        add_csamtools_sources(
            glob.glob(os.path.join(SAMTOOLS_LEGACY, "*.pysam.c"))
            + glob.glob(os.path.join(SAMTOOLS_LEGACY, "*", "*.pysam.c"))
            )

        print('Succeeded.')


class build_scripts (_build_scripts):
    def run (self):
        with open(LOG_FILE, 'a') as log:
            with redirect_output_streams(log):
                _build_scripts.run(self)
                
        # Copy mimodd main script to bin to have it available even
        # if installation as a script fails (this can happen with
        # wheel files and when using the upgrade tool).
        if not os.path.isdir(EXECUTABLES_TMP_DEST):
            os.mkdir(EXECUTABLES_TMP_DEST)

        shutil.copy(os.path.join(SCRIPTS, 'mimodd'), EXECUTABLES_TMP_DEST)


class install_lib (_install_lib):
    def run (self):
        with open(LOG_FILE, 'a') as log:
            with redirect_output_streams(log):
                _install_lib.run(self)

        # make MiModD binaries executable by everyone
        permissions = stat.S_IRWXU | stat.S_IRGRP | \
                      stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
        for fn in self.get_outputs():
            if os.path.basename(fn) in EXECUTABLES:
                os.chmod(fn, permissions)

        
class clean (_clean):
    """MiModD custom clean command."""
    
    # The standard clean command will wipe out our csamtools Extension
    # build files, but we need to handle our wrapped software build files.
    
    def run (self):
        with open(LOG_FILE, 'a') as log:
            with redirect_output_streams(log):
                _clean.run(self)
                
        # clear source directories of wrapped software
        with open(LOG_FILE, 'a') as log:
            for sourcedir, options in zip(
                (HTSLIB_1_0,
                 SAMTOOLS_1_0,
                 BCFTOOLS_1_0,
                 SAMTOOLS_LEGACY,
                 SNAP_SOURCE),
                ([],
                 ['HTSDIR=' + HTSLIB_1_0],
                 ['HTSDIR=' + HTSLIB_1_0],
                 [],
                 [])):
                p = subprocess.Popen(
                    ['make', 'clean'] + options,
                    cwd=sourcedir, stdout=log, stderr=log)
                if p.wait():
                    print(
                    'Warning: Could not remove all temporary files from {0}.'
                    .format(sourcedir))
        print('Done.')


class distclean (clean):
    """MiModD custom source distribution cleaner."""
    
    # This extends the clean command to restore a pristine source
    # distribution, i.e., everything that gets computed during a
    # build or an install is discarded.
    # The setuptools distclean command would do part of the job for us,
    # but this implementation works correctly independent of setuptools.

    description = 'Restore pristine distribution with no build/install traces'

    def run (self):
        clean.run(self)

        # If any of the following attempts to remove a file or folder
        # fail because of insufficient rights (OSError errno 13), distclean
        # should abort and notify the user of the cause.
        # All other OSErrors (most likely due to non-existing files) get
        # ignored.
        
        print('Discarding computed pysam source files ...', end=' ')
        # remove pysam.c files
        pysamcfiles = locate('*.pysam.c', SAMTOOLS_LEGACY)
        for f in pysamcfiles:
            try:
                os.remove(f)
            except OSError as e:
                if e.errno == 13:
                    raise
                else:
                    pass
        # remove pysam.h
        try:
            os.remove(os.path.join(SAMTOOLS_LEGACY, 'pysam.h'))
        except OSError as e:
            if e.errno == 13:
                raise
            else:
                pass
        print('Done.')

        print('Removing executable folder ...', end= ' ')
        try:
            shutil.rmtree(EXECUTABLES_TMP_DEST)
        except OSError as e:
            if e.errno == 13:
                raise
            else:
                pass
        print('Done.')

        print('Removing modified Galaxy data ...', end= ' ')
        try:
            shutil.rmtree(GALAXY_TMP_DEST)
        except OSError as e:
            if e.errno == 13:
                raise
            else:
                pass
        print('Done.')

        print('Resetting copy of first_run script ...', end= ' ')
        try:
            with open(os.path.join(PY_LIB, '.__first_run__'), 'w') as tmp:
                pass
        except OSError as e:
            if e.errno == 13:
                raise
            else:
                pass
        print('Done.')

        print('Removing build folder ...', end= ' ')
        try:
            shutil.rmtree(os.path.join(HERE, 'build'))
        except OSError as e:
            if e.errno == 13:
                raise
            else:
                pass
        print('Done.')

        print('Removing egg-info ...', end= ' ')
        try:
            shutil.rmtree(os.path.join(HERE, 'lib', 'MiModD.egg-info'))
        except OSError as e:
            if e.errno == 13:
                raise
            else:
                pass
        print('Done.')

        print('Resetting log file ..', end=' ')
        try:
            with open(LOG_FILE, 'w') as log:
                pass
        except OSError as e:
            if e.errno == 13:
                raise
            else:
                pass
        print('Done.')


# register the custom command classes defined above
cmdclass = {'build': build,
            'build_dep': build_dep,
            'build_galaxy_data': build_galaxy_data,
            'build_py': build_py,
            'build_ext': build_ext,
            'build_scripts': build_scripts,
            'install_lib': install_lib,
            'clean': clean,
            'distclean': distclean}


#+++++++++++ helper functions and classes +++++++++++

class MiModDInstallationError (RuntimeError):
    pass


@contextlib.contextmanager
def redirect_output_streams (target):
    oldstdout = oldstderr = None
    sys.stdout.flush()
    sys.stderr.flush()
    oldstdout = os.dup(sys.stdout.fileno())
    oldstderr = os.dup(sys.stderr.fileno())
    try:
        os.dup2(target.fileno(), sys.stdout.fileno())
        os.dup2(target.fileno(), sys.stderr.fileno())
        yield
    finally:
        os.dup2(oldstdout, sys.stdout.fileno())
        os.dup2(oldstderr, sys.stderr.fileno())    


# from the pysam installer
def locate (pattern, root=os.curdir):
    """Locate all files matching supplied filename pattern in and below
    supplied root directory."""
    for path, dirs, files in os.walk(os.path.abspath(root)):
       for filename in fnmatch.filter(files, pattern):
          yield os.path.join(path, filename)


def add_csamtools_sources (source_files):
    for extension in PKG_LAYOUT['ext_modules']:
        if extension.name == 'MiModD.pysam.csamtools':
            extension.sources += source_files


if __name__ == '__main__':
    # Check that this is running in a suitable environment
    assert sys.version_info[:2] >= (3,3), 'MiModD requires Pyhon3.3 +'

    if not os.path.samefile(HERE, os.getcwd()):
        raise MiModDInstallationError(
            'setup.py needs to be run from within the folder containing it.'
            )

    # ok, lets set things up
    setup_args_dict = {'cmdclass': cmdclass}
    setup_args_dict.update(PKG_INFO)
    setup_args_dict.update(PKG_LAYOUT)
    try:    
        setup(**setup_args_dict)
    except MiModDInstallationError as error:
        print(error.args[0])
        print()
        try:
            # Show tail lines of the log file to help diagnosing the error.
            with open(LOG_FILE, 'r') as logged:
                print('Displaying end of installation log file for debugging:')
                print()
                lines = logged.readlines()
            for line in lines[-15:]:
                print(line, end = '')
            print()
            # With a pip install, the installation log ends up in a
            # temporary copy of the distribution, which pip will delete
            # as soon as we return.
            # To preserve the file we try to delete pip's marker file that
            # would trigger the removal of the directory.
            # If we succeed, the log file is saved from getting deleted, but
            # we need to take care of removing the rest of the distribution
            # files ourselves.
            pip_delete_file = os.path.join(HERE,
                                           'pip-delete-this-directory.txt')
            try:
                os.remove(pip_delete_file)
            except:
                pass
            else:
                for file in os.listdir(HERE):
                    fpath = os.path.join(HERE, file)
                    if fpath != LOG_FILE:
                        os.remove(fpath)
            # Let the user know where to find the log file in case it's needed.
            print('The full installation log file can be found at: {0}'
                  .format(LOG_FILE)
                  )
            print()
        except (IOError, OSError):
            pass
        sys.exit(1)
