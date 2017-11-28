from setuptools import setup, __version__

# see StackOverflow/458550
exec(open('converter/version.py').read())

setup(name='ExcelConverter',
      version=__version__,
      packages=['converter'],
      description='A library for compiling excel spreadsheets to python code',
      tests_require=['nose >= 1.2'],
      test_suite='nose.collector',
      install_requires=['networkx', 'openpyxl'],
      author='Bydehand.com',
      author_email='info@bydehand.com',
      long_description="""ExcelConverter is a small python library that can translate an Excel spreadsheet into executable python code which can be run independently of Excel. The python code is based on a graph and uses caching & lazy evaluation to ensure (relatively) fast execution.""",
      classifiers=[
        'Intended Audience :: Developers',
        ]
      )


