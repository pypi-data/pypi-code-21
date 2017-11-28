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
        name = 'pybuilder_emr_plugin',
        version = '1.0.0',
        description = 'PyBuilder plugin to handle Amazon EMR functionality',
        long_description = '',
        author = 'Janne K. Olesen',
        author_email = 'janne.olesen@oberbaum-concept.com',
        license = 'Apache',
        url = 'https://github.com/OberbaumConcept/pybuilder_emr_plugin.git',
        scripts = [],
        packages = ['pybuilder_emr_plugin'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Operating System :: POSIX :: Linux',
            'Topic :: System :: Software Distribution',
            'Topic :: System :: Systems Administration',
            'Topic :: System :: Archiving :: Packaging',
            'Topic :: Utilities'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'boto3',
            'httpretty'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
