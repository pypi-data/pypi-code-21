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
        name = 'micro-utilities',
        version = '0.1.6',
        description = '',
        long_description = '',
        author = '',
        author_email = '',
        license = '',
        url = '',
        scripts = [],
        packages = [
            'micro_utilities',
            'micro_utilities.aws',
            'micro_utilities.config',
            'micro_utilities.http',
            'micro_utilities.notification',
            'micro_utilities.testing'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'requests',
            'boto',
            'Flask'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
