from setuptools import setup

setup(name='chem_G5',
      version='1.0',
      description='Elementray reaction and reversible reaction',
      url='https://github.com/CS207-G5/cs207-FinalProject',
      author='Brianna, Thomas, Yujiao, Yi',
      author_email='yi_zhai@g.harvard.edu',
      license='MIT',
      packages=['chem_G5'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'])