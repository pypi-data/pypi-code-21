from setuptools import setup, find_packages
import codecs
import os
import flyshare


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


LONG_DESCRIPTION = """
Flyshare
===============

* easy to use as most of the data returned are pandas DataFrame objects
* can be easily saved as csv, excel or json files
* can be inserted into MySQL or Mongodb

Target Users
--------------

* financial market analyst
* learners of financial data analysis with pandas/NumPy
* people who are interested in financial data of China, HongKong, US, etc.

Installation
--------------

    pip install flyshare

Upgrade
---------------

    pip install flyshare --upgrade

Quick Start
--------------

::

    import flyshare as fs

    fs.get_hist_data('600848')

return::

             open   high  close    low     volume  price_change  p_change  \
date
2017-10-27  31.45  33.20  33.11  31.45  333824.31          0.70      2.16
2017-10-26  29.30  32.70  32.41  28.92  501915.41          2.68      9.01
2017-10-25  27.86  30.45  29.73  27.54  328947.31          1.68      5.99
2017-10-24  28.20  28.75  28.05  27.22  313290.41         -1.74     -5.84
2017-10-23  29.00  31.16  29.79  28.90  466494.47          1.46      5.15
2017-10-20  29.20  29.83  28.33  27.85  411570.12          1.17      4.31
2017-10-19  25.61  27.20  27.16  25.61  180490.47          1.47      5.72
2017-10-18  25.63  26.41  25.69  25.50  109353.35          0.26      1.02
2017-10-17  25.30  25.88  25.43  25.23   67649.41          0.24      0.95
2017-10-16  26.40  26.48  25.19  25.03  113208.69         -1.16     -4.40
2017-10-13  26.26  26.54  26.35  26.14   54308.65          0.09      0.34
2017-10-12  26.28  26.51  26.26  25.92   85889.09         -0.05     -0.19
2017-10-11  27.26  27.37  26.31  26.02  128767.41         -0.81     -2.99

"""
MAINTAINER = 'duanrb'
MAINTAINER_EMAIL = 'rubing.duan@gmail.com'


if __name__ == "__main__":
    setup(
        name='flyshare',
        version=flyshare.__version__,
        description='A utility for providing historical and Real-time Quotes data of China stocks',
        long_description=LONG_DESCRIPTION,
        author='Rubing Duan',
        author_email='rubing.duan@gmail.com',
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        license='BSD',
        url='http://flyshare.org',
        keywords='China stock data',
        classifiers=['Development Status :: 4 - Beta',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3.2',
                     'Programming Language :: Python :: 3.3',
                     'Programming Language :: Python :: 3.4',
                     'License :: OSI Approved :: BSD License'],
        install_requires=['tushare>=0.92','pandas_datareader>=0.5.0'],
        packages=['flyshare', 'flyshare.stock'],
        package_data={'': ['*.csv']},
    )