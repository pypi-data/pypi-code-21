from distutils.core import setup
from pip.req import parse_requirements

install_req = parse_requirements('requirements/core.txt', session='skip')
req = [str(ir.req) for ir in install_req]


def read(filename):
    with open(filename) as fp:
        return fp.read()


setup(
    name='django_mock_queries',
    packages=['django_mock_queries'],
    version='1.0.3',
    description='A django library for mocking queryset functions in memory for testing',
    long_description=read('README.md'),
    author='Phivos Stylianides',
    author_email='stphivos@gmail.com',
    url='https://github.com/stphivos/django-mock-queries',
    keywords='django orm mocking unit-testing tdd',
    classifiers=[],
    install_requires=req
)
