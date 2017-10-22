from distutils.core import setup

VERSION = '0.2.2'

setup(
    name='geocrawl',
    packages=['geocrawl'],
    version=VERSION,
    license='MIT',
    description='A library to stream geocaching related entities from the official website',
    author='Kristian Scholze',
    author_email='Scholze.Kristian@gmail.com',
    url='https://github.com/nalch/geo-crawl',
    download_url='https://github.com/nalch/geo-crawl/archive/{}.tar.gz'.format(VERSION),
    keywords=['scrapy', 'geocaching', 'cache'],
    classifiers=[],
    install_requires=[
        'scrapy==1.4.0'
    ],
)
