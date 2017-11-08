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
        name = 'melange',
        version = '2.0.9',
        description = '',
        long_description = '',
        author = '',
        author_email = '',
        license = '',
        url = '',
        scripts = [],
        packages = [
            'melange',
            'melange.domain_event_bus',
            'melange.aws',
            'melange.infrastructure'
        ],
        namespace_packages = [],
        py_modules = ['__init__'],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'boto3',
            'marshmallow',
            'pyopenssl'
        ],
        dependency_links = ['git+https://github.com/Rydra/redis-simple-cache.git/@master#egg=redis-simple-cache-0'],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
