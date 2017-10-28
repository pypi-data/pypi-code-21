#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'pybuilder',
        version = '0.11.11',
        description = 'PyBuilder',
        long_description = 'PyBuilder\n=========\n\n`PyBuilder <http://pybuilder.github.io>`__\n\n|Build Status| |Windows build status| |PyPI version| |Coverage Status|\n|Ready in backlog| |Open bugs|\n\nPyBuilder is a software build tool written in 100% pure Python, mainly\ntargeting Python applications.\n\nPyBuilder is based on the concept of dependency based programming, but\nit also comes with a powerful plugin mechanism, allowing the\nconstruction of build life cycles similar to those known from other\nfamous (Java) build tools.\n\nPyBuilder is running on the following versions of Python: 2.6, 2.7, 3.3,\n3.4, 3.5 and PyPy.\n\nSee the `Travis Build <https://travis-ci.org/pybuilder/pybuilder>`__ for\nversion specific output.\n\nInstalling\n----------\n\nPyBuilder is available using pip:\n\n::\n\n    $ pip install pybuilder\n\nFor development builds use:\n\n::\n\n    $ pip install --pre pybuilder \n\nSee the `Cheeseshop\npage <https://warehouse.python.org/project/pybuilder/>`__ for more\ninformation.\n\nGetting started\n---------------\n\nPyBuilder emphasizes simplicity. If you want to build a pure Python\nproject and use the recommended directory layout, all you have to do is\ncreate a file build.py with the following content:\n\n.. code:: python\n\n    from pybuilder.core import use_plugin\n\n    use_plugin("python.core")\n    use_plugin("python.unittest")\n    use_plugin("python.coverage")\n    use_plugin("python.distutils")\n\n    default_task = "publish"\n\nSee the `PyBuilder homepage <http://pybuilder.github.com/>`__ for more\ndetails.\n\nPlugins\n-------\n\nPyBuilder provides a lot of plugins out of the box that utilize tools\nand libraries commonly used in Python projects:\n\n-  `python.coverage <http://pybuilder.github.com/documentation/plugins.html#Measuringunittestcoverage>`__\n   - Uses the standard\n   `coverage <https://warehouse.python.org/project/coverage/>`__ module\n   to calculate unit test line coverage.\n-  `python.distutils <http://pybuilder.github.com/documentation/plugins.html#BuildingaPythonpackage>`__\n   - Provides support to generate and use\n   `setup.py <https://warehouse.python.org/project/setuptools/>`__\n   files.\n-  **python.django** - Provides support for developing\n   `Django <https://www.djangoproject.com/>`__ applications.\n-  `python.frosted <http://pybuilder.github.io/documentation/plugins.html#Frostedplugin>`__\n   - Lint source files with\n   `frosted <https://github.com/timothycrosley/frosted>`__\n-  `python.flake8 <http://pybuilder.github.io/documentation/plugins.html#Flake8plugin>`__\n   - Provides support for\n   `flake8 <https://warehouse.python.org/project/flake8/>`__\n-  `python.pep8 <http://pybuilder.github.io/documentation/plugins.html#Pep8plugin>`__\n   - Provides support for\n   `pep8 <https://warehouse.python.org/project/pep8/>`__\n-  `python.install\\_dependencies <http://pybuilder.github.io/documentation/plugins.html#Installingdependencies>`__\n   - Installs the projects build and runtime dependencies using ``pip``\n-  `python.pychecker <http://pybuilder.github.io/documentation/plugins.html#Pycheckerplugin>`__\n   - Provides support for\n   `pychecker <http://pychecker.sourceforge.net/>`__\n-  `python.Pydev <http://pybuilder.github.io/documentation/plugins.html#ProjectfilesforEclipsePyDev>`__\n   - Generates project files to import projects into `Eclipse\n   PyDev <http://pydev.org/>`__\n-  `python.PyCharm <http://pybuilder.github.io/documentation/plugins.html#ProjectfilesforJetbrainsPyCharm>`__\n   - Generates project files to import projects into `Jetbrains\n   PyCharm <http://www.jetbrains.com/pycharm/>`__\n-  `python.pylint <http://pybuilder.github.io/documentation/plugins.html#Pylintplugin>`__\n   - Executes `pylint <https://bitbucket.org/logilab/pylint/>`__ on your\n   sources.\n-  `python.pymetrics <http://pybuilder.github.io/documentation/plugins.html#Pymetricsplugin>`__\n   - Calculates several metrics using\n   `pymetrics <http://sourceforge.net/projects/pymetrics/>`__\n-  `python.unittest <http://pybuilder.github.com/documentation/plugins.html#RunningPythonUnittests>`__\n   - Executes\n   `unittest <http://docs.python.org/library/unittest.html>`__ test\n   cases\n-  `python.integrationtest <http://pybuilder.github.com/documentation/plugins.html#RunningPythonIntegrationTests>`__\n   - Executes python scripts as integrations tests\n-  `python.pytddmon <http://pybuilder.github.io/documentation/plugins.html#Visualfeedbackfortests>`__\n   - Provides visual feedback about unit tests through\n   `pytddmon <http://pytddmon.org/>`__\n-  `python.cram <http://pybuilder.github.io/documentation/plugins.html#RunningCramtests>`__\n   - Runs `cram <https://warehouse.python.org/project/cram/>`__ tests\n-  `python.sphinx <http://pybuilder.github.io/documentation/plugins.html#Creatingdocumentationwithsphinx>`__\n   - Build your documentation with `sphinx <http://sphinx-doc.org/>`__\n-  `python.sonarqube <http://pybuilder.github.io/documentation/plugins.html#SonarQubeintegration>`__\n   - Analyze your project with\n   `SonarQube <http://www.sonarqube.org/>`__.\n-  python.snakefood - Analyze your code dependencies with\n   `snakefood <https://bitbucket.org/blais/snakefood>`__.\n\nIn addition, a few common plugins are provided:\n\n-  `copy\\_resources <http://pybuilder.github.io/documentation/plugins.html#Copyingresourcesintoadistribution>`__\n   - Copies files.\n-  `filter\\_resources <http://pybuilder.github.io/documentation/plugins.html#Filteringfiles>`__\n   - Filters files by replacing tokens with configuration values.\n-  `source\\_distribution <http://pybuilder.github.io/documentation/plugins.html#Creatingasourcedistribution>`__\n   - Bundles a source distribution for shipping.\n\nExternal plugins: \\*\n`pybuilder\\_aws\\_plugin <https://github.com/immobilienscout24/pybuilder_aws_plugin>`__\n- handle AWS functionality\n\nRelease Notes\n-------------\n\nThe release notes can be found\n`here <http://pybuilder.github.com/releasenotes/>`__. There will also be\na git tag with each release. Please note that we do not currently\npromote tags to GitHub "releases".\n\nDevelopment\n-----------\n\nSee `developing\nPyBuilder <http://pybuilder.github.io/documentation/developing_pybuilder.html>`__\n\n.. |Build Status| image:: https://secure.travis-ci.org/pybuilder/pybuilder.png?branch=master\n   :target: http://travis-ci.org/pybuilder/pybuilder\n.. |Windows build status| image:: https://ci.appveyor.com/api/projects/status/e8fbgcyc7bdqbko3?svg=true\n   :target: https://ci.appveyor.com/project/mriehl/pybuilder\n.. |PyPI version| image:: https://badge.fury.io/py/pybuilder.png\n   :target: https://warehouse.python.org/project/pybuilder/\n.. |Coverage Status| image:: https://coveralls.io/repos/pybuilder/pybuilder/badge.png?branch=master\n   :target: https://coveralls.io/r/pybuilder/pybuilder?branch=master\n.. |Ready in backlog| image:: https://badge.waffle.io/pybuilder/pybuilder.png?label=ready&title=Ready\n   :target: https://waffle.io/pybuilder/pybuilder\n.. |Open bugs| image:: https://badge.waffle.io/pybuilder/pybuilder.png?label=bug&title=Open%20Bugs\n   :target: https://waffle.io/pybuilder/pybuilder\n',
        author = 'Alexander Metzner, Maximilien Riehl, Michael Gruber, Udo Juettner, Marcel Wolf, Arcadiy Ivanov, Valentin Haenel',
        author_email = 'alexander.metzner@gmail.com, max@riehl.io, aelgru@gmail.com, udo.juettner@gmail.com, marcel.wolf@me.com, arcadiy@ivanov.biz, valentin@haenel.co',
        license = 'Apache License',
        url = 'http://pybuilder.github.io',
        scripts = ['scripts/pyb'],
        packages = [
            'pybuilder',
            'pybuilder.pluginhelper',
            'pybuilder.plugins',
            'pybuilder.plugins.python'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Software Development :: Build Tools',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing'
        ],
        entry_points = {
            'console_scripts': ['pyb_ = pybuilder.cli:main']
        },
        data_files = [],
        package_data = {
            'pybuilder': ['LICENSE']
        },
        install_requires = [
            'pip>=7.1',
            'setuptools~=35.0',
            'tblib',
            'wheel'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '!=3.0,!=3.1,!=3.2,<3.7,>=2.6',
        obsoletes = [],
    )
