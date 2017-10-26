try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


try:
    long_description = open('README.md').read()
except IOError:
    long_description = ""


with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='embed-python',
    packages=['embed', 'embed.parsers'],
    version='0.1.6',
    description='A simple python library to scrape any URL and return the most meaningful data from it',
    long_description=long_description,
    author='Thought Chimp',
    author_email='whoop@thoughtchimp.com',
    url='https://github.com/thoughtchimp/embed-python',
    keywords=['embed', 'scrapper', 'oembed', 'scrape', 'crawl'],
    classifiers=[
      "Development Status :: 4 - Beta",
      "Intended Audience :: Developers",
      "Operating System :: OS Independent",
      'Programming Language :: Python :: 3.5',
      "Operating System :: OS Independent",
      'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    license='MIT',
    install_requires=required,
)
