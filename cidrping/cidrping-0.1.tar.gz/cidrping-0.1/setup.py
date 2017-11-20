from setuptools import setup

setup(
	name = "cidrping",
	version = "0.1",
	author = "Jakob Svanholm",
	author_email = "jakob@rymdlego.se",
	url = "https://github.com/rymdlego/pingvin",
	description = "A simple script for pinging hosts by CIDR-notation.",
	keywords = "network ping cidr",
	scripts=['cidrping'],
	install_requires=['ipcalc', 'six']
)
