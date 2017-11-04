import os

from setuptools import setup, find_packages, Command


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info; py.cleanup -d')


here = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()
except IOError:
    VERSION = README = ''

install_requires = [
    'argon2-cffi==16.3.0',
    'asn1crypto==0.23.0',
    'bcrypt==3.1.4',
    'blinker==1.4',
    'cbor2==4.0.1',
    'cffi==1.11.2',
    'click==6.7',
    'cryptography==2.1.1',
    'enum34==1.1.6',
    'Flask==0.10.1',
    'hupper==1.0',
    'idna==2.6',
    'ipaddress==1.0.18',
    'itsdangerous==0.24',
    'Jinja2==2.9.6',
    'MarkupSafe==1.0',
    'msgpack-python==0.4.8',
    'passlib==1.7.1',
    'PasteDeploy==1.5.2',
    'pathlib==1.0.1',
    'plaster==1.0',
    'plaster-pastedeploy==0.4.1',
    'pycparser==2.18',
    'pymongo==3.5.1',
    'pyramid==1.9.1',
    'python-json-logger==0.1.8',
    'pytz==2017.2',
    'PyYAML==3.12',
    'redis==2.10.6',
    'repoze.lru==0.7',
    'six==1.11.0',
    'SQLAlchemy==1.1.14',
    'translationstring==1.3',
    'typing==3.6.2',
    'venusian==1.1.0',
    'WebOb==1.7.3',
    'Werkzeug==0.12.2',
    'WTForms==2.1',
    'zope.deprecation==4.3.0',
    'zope.interface==4.4.3'
]

setup(
    name='yosaipy2',
    version='0.3.3',
    description="Yosai is a powerful security framework with an intuitive api.",
    long_description=README,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='security rbac session authentication authorization',
    author='jellybean4',
    author_email='xulongfetion@163.com',
    url='http://yosaiproject.github.io/yosai',
    license='Apache License 2.0',
    packages=find_packages('.', exclude=['ez_setup', 'test*']),
    install_requires=install_requires,
    zip_safe=False,
    cmdclass={'clean': CleanCommand}
)
