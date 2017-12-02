from setuptools import setup, find_packages
from tensorci.version import version

setup(name='tensorci',
      version=version,
      description='TensorCI CLI',
      author='Ben Whittle',
      author_email='benwhittle31@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        'click',
        'awesome-slugify',
        'requests',
        'tinynetrc',
        'pyyaml',
        'gitpython'
      ],
      entry_points='''
        [console_scripts]
        tensorci=tensorci.main:cli
      ''')