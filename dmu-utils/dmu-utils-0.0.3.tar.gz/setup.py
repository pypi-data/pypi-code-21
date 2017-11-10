from setuptools import setup


version = '0.0.3'

setup(
    name='dmu-utils',
    version=version,
    description='DMU Utils',
    author='Dmitry Mugtasimov',
    author_email='dmugtasimov@gmail.com',
    url='https://github.com/dmugtasimov/dmu-utils',
    packages=['dmu_utils'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'six==1.11.0',
    ],
    extras_require={
        'schematics': ['schematics==2.0.0a1'],
        'sqlalchemy': ['SQLAlchemy==1.1.9', 'SQLAlchemy-Utils==0.32.14'],
        'configuration': ['PyYAML==3.12', 'ObjDict==0.4.4'],
        'dev': ['pytest==3.0.7', 'mock==2.0.0', 'pytest-mock==1.6.0', 'pytest-cov==2.4.0']
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
)
