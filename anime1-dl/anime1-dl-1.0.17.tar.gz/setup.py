from setuptools import setup, find_packages

setup(
    name="anime1-dl",
    version="1.0.17",
    description="A simple downloader for http://www.anime1.com",
    long_description="",
    author="Dragneel1234",
    author_email="blwal7057@gmail.com",
    url="https://github.com/Dragneel1234",
    license="MPL-2.0",
    packages=["anime1dl"],
    entry_points={
          'console_scripts': [
              'anime1-dl = anime1dl.__main__:main'
          ]
      },
    classifiers = [
        'Environment :: Console',
        'Topic :: Utilities'
    ]
)