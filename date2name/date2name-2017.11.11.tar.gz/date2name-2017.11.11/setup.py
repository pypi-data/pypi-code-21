from distutils.core import setup

setup(
    name="date2name",
    version="2017.11.11",
    description="Handling time-stamps and date-stamps in file names",
    author="Karl Voit",
    author_email="tools@Karl-Voit.at",
    url="https://github.com/novoid/date2name",
    download_url="https://github.com/novoid/date2name/zipball/master",
    keywords=["file managing", "file management", "files", "date", "time", "time-stamps"],
    install_requires=["logging", "time", "sys", "optparse"],
    long_description="""\
filetags
-----------------------------
This Python script adds, removes, and manages date- and time-stamps in file names.

    2013-05-09 a file name with ISO date stamp in name -- tag1.jpg

    2013-05-09T16.17 file name with time stamp -- tag3.csv

Usage:
         date2name [options] file ...

Per default, date2name gets the modification time of matching files
and directories and adds a datestamp in standard ISO 8601+ format
YYYY-MM-DD (http://datestamps.org/index.shtml) at the beginning of
the file- or directoryname.
If an existing timestamp is found, its style will be converted to the
selected ISO datestamp format but the numbers stays the same.
Executed with an examplefilename "file" this results e.g. in
"2008-12-31_file".
Note: Other that defined in ISO 8601+ the delimiter between hours,
minutes, and seconds is not a colon but a dot. Colons are causing
several problems on different file systems and are there fore replaced
with the (older) DIN 5008 version with dots.

Run date2name --help for usage hints

Options:
  -h, --help         show this help message and exit
  -d, --directories  modify only directory names
  -f, --files        modify only file names
  -C, --compact      use compact datestamp             (YYYYMMDD)
  -M, --month        use datestamp with year and month (YYYY-MM)
  -w, --withtime     use datestamp including seconds   (YYYY-MM-DDThh.mm.ss)
  -m, --mtime        take modification time for datestamp [default]
  -c, --ctime        take creation time for datestamp
  -q, --quiet        do not output anything but just errors on console
  -v, --verbose      enable verbose mode
  --nocorrections    do not convert existing datestamps to new format
  -s, --dryrun       enable dryrun mode: just simulate what would happen, do
                     not modify files or directories
  --version          display version and exit

Please read https://github.com/novoid/filetags/ for further information and descriptions.
"""
)
