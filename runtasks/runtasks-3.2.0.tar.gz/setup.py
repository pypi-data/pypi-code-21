
from distutils.cmd import Command
from distutils.core import setup


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys, subprocess
        cmdline = '-m unittest discover -s tests -v'
        sys.exit(subprocess.call([sys.executable] + cmdline.split()))


def _getversion():
    """
    The version is maintained in runtasks/version.py.
    """
    m = __import__('runtasks.version')
    return m.version


setup(
    name='runtasks',
    description='A simple task runner for Python',
    version=_getversion(),
    author='Michael Kleehammer',
    author_email='michael@kleehammer.com',
    url='https://gitlab.com/mkleehammer/runtasks',
    packages=['runtasks'],
    scripts=['scripts/run', 'scripts/run.cmd'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools'
    ],
    cmdclass=dict(test=TestCommand)
)
