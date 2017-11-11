from distutils.core import setup

setup(
    name="filetags",
    version="2017.11.11",
    description="Management of simple tags within file names",
    author="Karl Voit",
    author_email="tools@Karl-Voit.at",
    url="https://github.com/novoid/filetags",
    download_url="https://github.com/novoid/filetags/zipball/master",
    keywords=["tagging", "tags", "file managing", "file management", "files", "tagtrees", "tagstore", "tag-based navigation", "tag-based filter"],
    install_requires=["importlib", "logging", "operator", "difflib", "readline", "codecs", "argparse", "math", "clint", "shutil", "subprocess", "platform", "time", "itertools", "re", "sys", "os"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        ],
    long_description="""\
filetags
-----------------------------
This Python script adds, removes, and manages tags in file names as in following examples:

    file without time stamp in name -- tag2.txt

    file name with several tags -- tag1 tag2.jpeg

    another example file name with multiple example tags -- fun videos kids.mpeg

    2013-05-09 a file name with ISO date stamp in name -- tag1.jpg

    2013-05-09T16.17 file name with time stamp -- tag3.csv

There are many more cool features of this tool.
Please read https://github.com/novoid/filetags/ for further information and descriptions.
"""
)
