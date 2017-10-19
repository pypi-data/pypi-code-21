from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
	
setup(
    name='SpiderBone',

    version='1.1.1',

    description='Differently Spider frame',
    long_description=long_description,

    url='https://github.com/HiredMagician/SpiderBone/',

    author='HiredMagician',
    author_email='badjoke@aliyun.com',

    license='MIT',

    classifiers=[

        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python'
    ],
	keywords='web spider frame',

    packages=['SpiderBone'],

    install_requires=['bs4','requests'],
)