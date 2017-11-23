from setuptools import find_packages
from setuptools import setup

setup(name='python-git-pkgManager',
      version="v0.511",
      description="Import extension from github directly into your project.",
      author='Benny Elgazar',
      url='https://github.com/bennyelg/git_import',
      author_email='elgazarbenny@gmail.com',
      install_requires=[
          'gitpython'
      ],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
      ],
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      platforms='any')


