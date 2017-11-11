from distutils.core import setup

setup(
    name="appendfilename",
    version="2017.11.11",
    description="Intelligent appending text to file names, considering file extensions and file tags",
    author="Karl Voit",
    author_email="tools@Karl-Voit.at",
    url="https://github.com/novoid/appendfilename",
    download_url="https://github.com/novoid/appendfilename/zipball/master",
    keywords=["file managing", "file management", "files", "date", "time", "time-stamps"],
    install_requires=["logging", "time", "sys", "optparse", "readline"],
    long_description="""\
appendfilename
-----------------------------
Intelligent appending text to file names, considering file extensions and file tags

Usage:
    ./appendfilename.py [<options>] <list of files>

This tool inserts text between the old file name and optional tags or file extension.


Text within file names is placed between the actual file name and
the file extension or (if found) between the actual file namd and
a set of tags separated with " -- ".
  Update for the Boss  <NEW TEXT HERE>.pptx
  2013-05-16T15.31.42 Error message <NEW TEXT HERE> -- screenshot projectB.png

Example usages:
  ./appendfilename.py --text="of projectA" "the presentation.pptx"
      ... results in "the presentation of projectA.pptx"
  ./appendfilename.py "2013-05-09T16.17_img_00042 -- fun.jpeg"
      ... with interactive input of "Peter" results in:
          "2013-05-09T16.17_img_00042 Peter -- fun.jpeg"

"""
)
