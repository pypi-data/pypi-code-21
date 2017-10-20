import os
from setuptools import setup


def read():
    return open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='hockey_scraper',
    version='1',
    description="""This project is designed to allow people to scrape Play by Play and Shift data off of the National
                Hockey League (NHL) API and website for all regular season and playoff games since the 2010-2011 
                season""",
    long_description=read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        'Intended Audience :: Science/Research',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3'
    ],
    keywords='NHL',
    url='https://github.com/HarryShomer/Hockey-Scraper',
    author='Harry Shomer',
    author_email='Harryshomer@gmail.com',
    license='MIT',
    packages=['scrape'],
    install_requires=['pandas', 'BeautifulSoup4', 'requests', 'lxml'],
    include_package_data=True,
    zip_safe=False
)
