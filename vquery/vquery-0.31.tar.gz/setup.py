from setuptools import setup

setup(
	name = "vquery",
	version = "0.31",
	author = "Jakob Svanholm",
	author_email = "jakob@rymdlego.se",
	url = "https://github.com/rymdlego/vquery",
	description = "A tool for querying vCenter for various information.",
	keywords = "vSphere VMware vCenter",
	scripts=['vq'],
	packages=['vquery'],
	install_requires=['docopt', 'pyVmomi']
)
