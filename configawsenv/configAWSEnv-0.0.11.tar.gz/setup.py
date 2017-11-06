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
        name = 'configAWSEnv',
        version = '0.0.11',
        description = 'A utility to stop and start AWS environments',
        long_description = 'This utility stops and starts AWS environments (group of instances according to tags) from an external scheduler',
        author = 'Ittiel',
        author_email = 'ittiel@gmail.com',
        license = 'Apache License',
        url = 'https://github.com/taykey/schedule-aws-env',
        scripts = ['scripts/configEnv.py'],
        packages = ['configAWSEnv'],
        namespace_packages = [],
        py_modules = ['__init__'],
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
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
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing'
        ],
        entry_points = {
            'console_scripts': ['configAWSEnv=configAWSEnv:config_ec2_env.main']
        },
        data_files = [],
        package_data = {
            'pybuilder': ['LICENSE']
        },
        install_requires = [
            'argparse==1.4.0',
            'boto3==1.4.7'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
