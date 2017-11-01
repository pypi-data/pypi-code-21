import re
from os import path
from setuptools import setup


here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'aionationstates/__init__.py')) as f:
    #print(f.read())
    version_match = re.search("__version__ = '(.+?)'", f.read())
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")


setup(
    name='aionationstates',

    version=version,

    description='An asyncio wrapper for the NationStates API',
#    long_description=long_description,

    url='https://github.com/micha030201/aionationstates',

    author='Михаил Лебедев',
    author_email='micha030201@gmail.com',

    license='GPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Internet',
        'Topic :: Games/Entertainment :: Simulation',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3.6',
    ],

    keywords='API nationstates',

    packages=['aionationstates'],

    install_requires=['aiohttp'],
)
