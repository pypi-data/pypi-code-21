# Author: Joshua Bourquin
# Email: josh.bourquin@digitalglobe.com

from setuptools import setup, find_packages
from aiobot import __version__

setup(
	name = 'aiobot',
	version = __version__,
	packages = find_packages(),

	install_requires = [
		'aiohttp'
	],

	# metadata
	author = 'Joshua Bourquin',
	description = 'Build Slack Bots using asyncio.',
    url = 'https://gitlab.com/pymatics/aiobot'
)