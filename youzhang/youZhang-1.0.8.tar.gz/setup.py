from distutils.core import setup
import os
NAME = 'youZhang'
_MAJOR = 1
_MINOR = 0
_MICRO = 8
VERSION = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
DESCRIPTION = "youtube-download-tools @ZHANG Xu-long"
SEP=os.sep

def long_description():
    readme = open('README.md', 'r').read()
    changelog = open('CHANGELOG.md', 'r').read()
    return changelog + '\n\n' + readme


setup(
    packages=['youZhang'],
    data_files=[('.'+SEP, ['CHANGELOG.md', 'README.md'])]
    ,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description(),
    author="ZHANG Xu-long",
    author_email="fudan0027zxl@gmail.com",
    license="BSD",
    url="http://zhangxulong.site",
    keywords='audio music sound',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",

    ],
    install_requires=['numpy', 'tqdm',
                      'pyPdf', 'PyYAML',
                      ],
)
