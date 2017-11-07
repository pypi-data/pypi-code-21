from setuptools import find_packages
from tcell_agent.version import VERSION

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

MODULE = Extension(
    '_libinjection', [
        'tcell_agent/libinjection/libinjection_wrap.c',
        'tcell_agent/libinjection/libinjection_sqli.c',
        'tcell_agent/libinjection/libinjection_html5.c',
        'tcell_agent/libinjection/libinjection_xss.c'
    ],
    swig_opts=['-Wextra', '-builtin'],
    define_macros=[],
    include_dirs=[],
    libraries=[],
    library_dirs=[],
)

setup(name='tcell_agent',
      version=VERSION,
      description='tCell.io Agent',
      url='https://tcell.io',
      author='tCell.io',
      author_email='support@tcell.io',

      ext_package='tcell_agent.libinjection',
      ext_modules=[MODULE],
      license='Free-to-use, proprietary software.',
      install_requires=[
          "requests[security]",
          "future",
          "pyyaml"
      ],
      tests_require=[
          "requests[security]",
          "future",
          "nose",
          "gunicorn",
          "Django",
          "httmock",
          "Flask"
      ],
      test_suite='nose.collector',
      scripts=['tcell_agent/bin/tcell_agent'],
      packages=find_packages() + ['tcell_agent/pythonpath'],
      package_data={
          'tcell_agent.appsensor.rules': ['*.json'],
          'tcell_agent.rust': ['libtcellagent-*.so', 'libtcellagent-*.dylib', 'tcellagent-*.dll']})
