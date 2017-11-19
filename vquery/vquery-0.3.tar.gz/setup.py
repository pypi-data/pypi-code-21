from setuptools import setup

setup(
	name = "vquery",
	version = "0.3",
	author = "Jakob Svanholm",
	author_email = "jakob@rymdlego.se",
	description = "A tool for querying vCenter for various useful information.",
	keywords = "vSphere VMware vCenter",
	scripts=['vq'],
	packages=['vquery'],
	install_requires=['docopt', 'pyVmomi']
)
