import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="passivetotal2",
    version="1.0.1",
    description="PassiveTotal client, version 2",
    author="Johan Nestaas, Nate Falke",
    author_email='johan.nestaas@riskiq.net, nate.falke@riskiq.net',
    license="Copyright RiskIQ",
    keywords="",
    url="https://www.bitbucket.org/riskiq/passivetotal_client",
    packages=['passivetotal2', 'passivetotal2.cli', 'passivetotal2.client'],
    package_dir={'passivetotal2': 'passivetotal2',
                 'passivetotal2.cli': 'passivetotal2/cli',
                 'passivetotal2.client': 'passivetotal2/client'},
    long_description=read('README.md'),
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    install_requires=[
        'confutil',
        'requests',
        'tabulate==0.7.7',
    ],
    entry_points={
        'console_scripts': [
            'passivetotal=passivetotal2:main',
        ],
    },
)
