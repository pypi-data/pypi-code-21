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
        name = 'simple-container-runtime',
        version = '0.0.3',
        description = 'Simple-Container-Runtime - simply run docker containers',
        long_description = 'Simple-Container-Runtime - simply run docker containers',
        author = 'Marco Hoyer',
        author_email = 'marco_hoyer@gmx.de',
        license = 'APACHE LICENSE, VERSION 2.0',
        url = 'https://github.com/cfn-sphere/simple-container-runtime',
        scripts = ['scripts/scr'],
        packages = [
            'simple_container_runtime',
            'simple_container_runtime.aws',
            'simple_container_runtime.modules'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {
            'console_scripts': ['cf=simple_container_runtime.cli:main']
        },
        data_files = [],
        package_data = {},
        install_requires = [
            'PyYAML',
            'boto3',
            'click',
            'pathlib2',
            'requests',
            'sh'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
