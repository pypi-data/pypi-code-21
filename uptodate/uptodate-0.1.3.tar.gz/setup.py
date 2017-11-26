from setuptools import setup


setup(
    name='uptodate',
    packages=['uptodate'],  # this must be the same as the name above
    version='0.1.3',
    description='Command line script checking if your requirements are uptodate',  # noqa
    author='Paweł Jastrzębski',
    author_email='pj@napcode.eu',
    url='https://gitlab.com/havk/uptodate',  # use the URL to the github repo
    keywords=[
        'requirements',
        'requirements.txt',
        'uptodate',
    ],  # arbitrary keywords
    license='MIT',
    classifiers=[],
    install_requires=[
        'click==6.7',
        'requests==2.18.4',
        'texttable==1.1.1'
    ],
    entry_points={
        'console_scripts': [
            'uptodate=uptodate.cli:up_to_date'
        ]
    }
)
