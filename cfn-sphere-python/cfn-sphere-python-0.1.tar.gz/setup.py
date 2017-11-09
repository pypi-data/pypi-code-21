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
        name = 'cfn-sphere-python',
        version = '0.1',
        description = '''cfn-sphere-python Python Wrapper for AWS CloudFormation management tool cfn-sphere''',
        long_description = '''cfn-sphere-python - A python wrapper for cfn-sphere to simplify the use of cfn-sphere stacks configs in python.''',
        author = "Felix Borchers",
        author_email = "felix.borcher@gmail.com",
        license = 'APACHE LICENCE, VERSION 2.0',
        url = 'https://github.com/ImmobilienScout24/cfn-sphere-python',
        scripts = [],
        packages = ['cfn_sphere_python'],
        py_modules = [],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Topic :: System :: Systems Administration'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = ['cfn-sphere'],
        dependency_links = [],
        zip_safe=True,
        cmdclass={'install': install},
    )
