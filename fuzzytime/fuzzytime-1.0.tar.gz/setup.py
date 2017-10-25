from setuptools import setup

def readme():
    with open('README.rst') as r:
        return r.read()

setup(name='fuzzytime',
      version='1.0',
      description='Turns input datetime into fuzzy timestamp format',
      keywords='date time datetime timeago fuzzy',
      url='https://github.com/harshildp/fuzzytime',
      author='Harshil P.',
      author_email='harshilp@uw.edu',
      packages=['fuzzytime'],
      zip_safe=False)
