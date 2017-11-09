import setuptools
from distutils.core import setup, Extension

setup(
    name = 'nadds',
    version = '0.1.2',
    license="GNU LGPL",
    keywords=['python', 'api'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    author = 'Orlof',
    author_email = 'orlof@users.noreply.github.com',

    url = 'https://github.com/orlof/python-nadds/',
    download_url = 'https://github.com/orlof/python-nadds/archive/0.1.2.tar.gz',

    packages = ['nadds'],
    ext_package="nadds",
    ext_modules=[
        Extension(
            module,
            ["nadds/%s.c" % module],
            extra_compile_args=['-Werror']
        ) for module in ('recvmsg', 'sendmsg', 'socketpair', '_tuntap', 'socket_const')],

    description='Low level linux api calls for python',
    long_description="""
Nadds is a library of Python extensions that complement the standard
libraries in parts where full support for the UNIX API (or the Linux
API) is missing.

Most of the functions wrapped by Nadds are low-level, dirty, but
absolutely necessary functions for real systems programming. These 
functions are mostly added to mainstream Python3.

Current list of features included:

- recvmsg(2) and sendmsg(2), including use of cmsg(3)

- socketpair(2)

- support for TUN/TAP virtual network interfaces
""".strip()
)