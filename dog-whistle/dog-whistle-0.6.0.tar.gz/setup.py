import sys
import re
from setuptools import setup, find_packages


def get_version():
    with open('dog_whistle/__version__.py') as version_file:
        return re.search(r"""__version__\s+=\s+(['"])(?P<version>.+?)\1""",
                         version_file.read()).group('version')

install_requires = [
    'mock>=1.3.0',
    'coverage==4.0.3',
    'nose>=1.3.7',
    'statsd==3.2.1',
    'datadog==0.15.0',
    'future==0.16.0',
    'six==1.10.0',
]

lint_requires = [
    'pep8',
    'pyflakes'
]

tests_require = [
    'mock==1.3.0',
]

dependency_links = []
setup_requires = []
extras_require = {
    'test': tests_require,
    'all': install_requires + tests_require,
    'docs': ['sphinx'] + tests_require,
    'lint': lint_requires
}

if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='dog-whistle',
    version=get_version(),
    description='For Easy Integration of DataDog and LogFactory',
    author='Madison Bahmer',
    author_email='madison.bahmer@istresearch.com',
    license='MIT',
    url='https://github.com/istresearch/',
    keywords=['datadog', 'logfactory'],
    packages=find_packages(exclude=["samples.*", "samples"]),
    package_data={},
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require=extras_require,
    dependency_links=dependency_links,
    zip_safe=True,
    include_package_data=True,
)