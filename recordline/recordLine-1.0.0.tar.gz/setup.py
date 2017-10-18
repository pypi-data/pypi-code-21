"""
RecordLine
--------

RecordLine is a line data recorder!

RecordLine is Fun
```````````````

::

    >>> import recordLine as rl

    >>> db = rl.load('test.db')

    >>> db.new('somthing data')
	True

    >>> db.show()
    [...,
    ...,
    ...,
    'somthing data']


And Easy to Install
```````````````````

::

    $ pip install recordLine

Links
`````

* `project repo <https://github.com/amiralinull/recordLine/>`_

"""

from distutils.core import setup

setup(name = "recordLine",
    version="1.0.0",
    description="simple line data recorder",
    author="Amirali Esfandiari",
    author_email="incoming+amiralinull/recordLine@gitlab.com",
    license="GPLv3",
    url="https://amiralinull.github.io/recordLine/",
    long_description=__doc__,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers"
    ],
    py_modules=['recordLine'],
    install_requires=[])
