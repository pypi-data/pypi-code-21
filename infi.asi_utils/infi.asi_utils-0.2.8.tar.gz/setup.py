
SETUP_INFO = dict(
    name = 'infi.asi_utils',
    version = '0.2.8',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://git.infinidat.com/host-opensource/infi.asi_utils',
    license = 'BSD',
    description = """an alternative to sg3-utils""",
    long_description = """cross-platform implementation of sg3-utils on top of infi.asi""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'docopt',
'hexdump',
'infi.asi>=0.3.33',
'infi.os_info',
'infi.pyutils',
'infi.sgutils',
'setuptools'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [
'asi-utils = infi.asi_utils:main'
],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

