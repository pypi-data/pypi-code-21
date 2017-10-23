import setuptools
import subprocess
import sys
import os


with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'zeroconf',
]

test_requirements = [
    # TODO: put package test requirements here
]


class Venv(setuptools.Command):
    user_options = []

    def initialize_options(self):
        """Abstract method that is required to be overwritten"""

    def finalize_options(self):
        """Abstract method that is required to be overwritten"""

    def run(self):
        venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'venv', 'happy')
        if sys.version_info[0] >= 3:
            venv_cmd = ['python3', '-m', 'venv']
        else:
            venv_cmd = ['virtualenv']
            if self.python:
                venv_cmd.extend(['-p', self.python])
        venv_cmd.append(venv_path)
        print('Creating virtual environment in ', venv_path)
        subprocess.check_call(venv_cmd)
        print('Linking `activate` to top level of project.\n')
        print('To activate, simply run `source activate`.')
        try:
            os.symlink(
                os.path.join(venv_path, 'bin', 'activate'),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'activate')
            )
        except OSError:
            print('Unable to create symlink, you may have a stale symlink from a previous invocation.')


setuptools.setup(
    name='hap-py',
    version='0.0.1',
    description="A Python implementation of the HomeKit Application Protocol.",
    long_description=readme,
    author="Loren M. Carvalho",
    author_email='me@loren.pizza',
    url='https://github.com/sixninetynine/happy',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='happy',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='test',
    tests_require=test_requirements,
    cmdclass={'venv': Venv},
)
