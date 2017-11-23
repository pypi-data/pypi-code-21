from setuptools import setup


classifiers = """
Topic :: Multimedia :: Sound/Audio
Programming Language :: Python :: 2
Programming Language :: Python :: 3
"""

classifiers = [classif for classif in classifiers.split('\n') if classif]


setup(name='ctcsound',
      version='0.0.2',
      description='Python bindings to the Csound API using ctypes', 
      classifiers=classifiers,
      author='Francois Pinot',
      py_modules=['ctcsound', 'csoundSession'],
)



