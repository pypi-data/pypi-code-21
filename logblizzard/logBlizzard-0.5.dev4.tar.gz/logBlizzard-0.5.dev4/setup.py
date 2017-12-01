

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='logBlizzard',


    version='0.5dev4',

    description='a distributed logging framework',
    long_description='The goal is to provide distributed logging aggregation points, initially for syslog with longer term plans for other on-box logs. Aggregation points can be implemented close to the logging source either on a network device or other 3rd party compute node. Logging can be segmented into clusters with a hierarchy in each cluster. Message back-up/availability is built into the cluster logging architecture. Message dedup is the function of the ‘search head’. Each cluster has its own northbound API front end as part of a search head to be integrated with other systems.'
,

    url='https://github.com/kriswans/logBlizzard',


    author='Kris Swanson',
    author_email='kriswans@cisco.com',


    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',


        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',


        'License :: OSI Approved :: MIT License',



        'Programming Language :: Python :: 3.6',
    ],


    keywords=['logging','syslog','IP Multicast'],

    python_requires='>=3.5',

    install_requires=['cryptography'],


    package_data={
        'logBlizzard': ['localcfg.json','network_cfg.json','pwf','salt'],
    },


    data_files=['localcfg.json','network_cfg.json','pwf','salt'],


)
