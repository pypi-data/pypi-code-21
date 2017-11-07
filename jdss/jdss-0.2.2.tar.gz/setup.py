from distutils.core import setup

setup(
    name='jdss',
    packages=['jdss'],
    version='0.2.2',
    description='A command line tool for generating Jenkins summary reports for data science activities',
    author='Andy Kuszyk',
    author_email='pairofsocks@hotmail.co.uk',
    url='https://github.com/andykuszyk/jenkins-data-science-summary',
    keywords=['jenkins', 'data-science'],
    classifiers=[],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'jdss=jdss.cli:main',
        ],
    },
)
