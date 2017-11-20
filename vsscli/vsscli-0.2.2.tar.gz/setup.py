from setuptools import setup, find_packages
import os
import vsscli


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fo:
        return fo.read()


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='vsscli',
      version=vsscli.__version__,
      description='EIS Virtual Cloud Command Line Interface',
      author='University of Toronto - EIS - VSS',
      author_email='jm.lopez@utoronto.ca',
      maintainer='Virtualization & Storage Services',
      maintainer_email='vss-py@eis.utoronto.ca',
      url='https://gitlab-ee.eis.utoronto.ca/vss/vsscli',
      install_requires=required,
      packages=find_packages(exclude=['tests*']),
      include_package_data=True,
      scripts=['bin/vss_bash_completer'],
      package_data={'vsscli': ['bin/*']},
      entry_points='''
        [console_scripts]
        vss=vsscli.cli:cli
        ''',
      license='MIT License',
      long_description=read('README.rst'),
      classifiers=[
          "Development Status :: 4 - Beta",
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Natural Language :: English',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 2.7'
      ],
      platforms=['Linux', 'Solaris', 'Mac OS-X', 'Unix'],
      zip_safe=False
      )
