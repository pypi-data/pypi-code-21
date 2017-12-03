from setuptools import setup, find_packages

setup(name='pyrsos',
      version='0.2.2',
      description='PyTorch helper functions.',
      url='https://github.com/cbaziotis/pyrsos',
      author='Christos Baziotis',
      author_email='christos.baziotis@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['docs', 'tests*']),
      include_package_data=True
      )
