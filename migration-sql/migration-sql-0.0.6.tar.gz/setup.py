from setuptools import setup

setup(
    name='migration-sql',
    packages=['migration_sql'],
    version='0.0.6',

    install_requires=[
        'PyMySQL>=0.7.10',
        'SQLAlchemy>=1.1.6',
        'pytz>=2016.10'
    ],

    description='SQL Migration',
    long_description='Support sql migration using pure sql. Only support MySQL for now.',
    url='https://bitbucket.org/work-well/migration-sql',
    author='Workwell',
    author_email='friends@workwell.io',
    license='MIT',

    keywords=[
        'migration', 'sql', 'mysql'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
    ],

)
