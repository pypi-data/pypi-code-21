from setuptools import setup

setup(name='BaselineWanderRemoval',
      version='2017.10.25',
      description='Python port of BaselineWanderRemovalMedian.m from ECG-kit',
      url='https://bitbucket.org/atpage/baselinewanderremoval',
      author='Alex Page',
      author_email='alex.page@rochester.edu',
      license='GPLv2',
      packages=['BaselineWanderRemoval'],
      install_requires=['numpy', 'scipy'],
      keywords='ECG EKG baseline wander',
      zip_safe=False)
