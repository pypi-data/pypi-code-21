from setuptools import setup


REQUIREMENTS = []
TEST_REQUIREMENTS = []


setup(name='psstguy',
    version='0.1.0',
    description='',
    long_description='',
    author='Chris Schomaker',
    author_email='cshoe@protonmail.com',
    install_requires=REQUIREMENTS,
    include_package_data=True,
    entry_points='''
        [console_scripts]
        psstguy=psstguy:cli
    ''',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6'
    ]
)
