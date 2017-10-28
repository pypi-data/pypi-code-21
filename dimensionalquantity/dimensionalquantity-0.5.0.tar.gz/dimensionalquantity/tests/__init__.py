"""
The tests in tests/ are written with py.test in mind.
This means, change directory to tests/ and run py.test.
I suggest to work with entr [#entr-proj]_, thus execute the following:
    $ ls -d ../*.py *.py | entr -d py.test
This allows you to run the tests every time you save a file.

Furthermore, this module is tested using py.test in combination with the code coverage being checked using the pytest-cov extension [#pytest-cov].
Easiest you run the ./runautomatictests.sh, it does everything you need.

[#entr-proj] http://entrproject.org/
[#pytest-cov] https://pypi.python.org/pypi/pytest-cov
"""
