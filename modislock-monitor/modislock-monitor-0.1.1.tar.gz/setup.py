# Setup tools
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

# Misc
import re


with open('./README.md', encoding='utf-8') as f:
    readme = f.read()


class PostDevelopCommand(develop):
    """Develop command for setuptools

    """
    def run(self):
        # TODO Post install script here or call a function
        develop.run(self)


class PostInstallCommand(install):
    """Install command for setuptools

    """
    def _exec_sql_file(self, cursor, sql_file):
        from pymysql.err import ProgrammingError, OperationalError
        print("\n[INFO] Executing SQL script file: {}".format(sql_file))
        statement = ""

        for line in open(sql_file):
            if re.match(r'--', line):  # ignore sql comment lines
                continue
            if not re.search(r'[^-;]+;', line):  # keep appending lines that don't end in ';'
                statement = statement + line
            else:  # when you get a line ending in ';' then exec statement and reset for next statement
                statement = statement + line
                print("\n\n[DEBUG] Executing SQL statement:\n{}".format(statement))
                try:
                    cursor.execute(statement)
                except (OperationalError, ProgrammingError) as e:
                    print("\n[WARN] MySQLError during execute statement \n\tArgs: {}".format(str(e.args)))

                statement = ""

    def _pre_install(self):
        pass

    def _post_install(self):
        from pymysql import connect
        from pymysql.cursors import DictCursor
        from pymysql.err import InternalError

        connection = None

        try:
            connection = connect(host='localhost',
                                 user='root',
                                 password='',
                                 db='modislock',
                                 charset='utf8mb4',
                                 cursorclass=DictCursor)
        except InternalError:
            connection = connect(host='localhost', user='root', password='')
            self._exec_sql_file(connection.cursor(), '/etc/modis/modislock_init.sql')
        finally:
            connection.close()

    def run(self):
        # Pre-install
        self._pre_install()
        # Install
        install.run(self)
        # Post-install
        self._post_install()


setup(
    name='modislock-monitor',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1.1',

    description='Monitors slave status, door sensors, and provides validation to slave requests',
    long_description=readme,

    # The project's main homepage.
    url='https://github.com/Modis-GmbH/ModisLock-Monitor',

    # Choose your license
    license='GPL',

    # Author details
    author='Richard Lowe',
    author_email='richard@modislab.com',

    # What does your project relate to?
    keywords=['modis', 'raspberry pi', 'lock', 'serial port monitor'],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security"
    ],

    platforms=['Linux', 'Raspberry Pi'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'PyMySQL>=0.7.11',
        'SQLAlchemy[pymysql]>=1.2.0b2',
        'pyserial>=3.4',
        'watchedserial>=1.0.1',
        'RPi.GPIO>=0.6.3',
        'pycrypto==2.6.1',
        'yubico-client==1.10.0',
        'onetimepass==1.0.1',
        'cryptography==2.0.3',
        'systemd-python==234',
        'celery[redis]==4.1.0',
        'redis==2.10.6',
        'appdirs==1.4.3',
        'frozendict==1.2',
        'packaging==16.8',
        'requests==2.13.0',
        'six==1.10.0',
        'transitions==0.6.0'
    ],

    # If your project only runs on certain Python versions, setting the python_requires argument to the appropriate
    # PEP 440 version specifier string will prevent pip from installing the project on other Python versions.
    python_requires='>=3.5',

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[('/etc/supervisor/conf.d', ['deploy/modis_monitor.conf']),
                ('/etc/modis', ['deploy/modislock_init.sql'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'modis_monitor = modislock_monitor.run_monitor:main',
            'modis_monitor_worker = modislock_monitor.celery_worker:main'
        ]
    },

    cmdclass={'develop': PostDevelopCommand,
              'install': PostInstallCommand}
)
