from setuptools import setup

setup(
	name = "vquery",
	version = "0.32",
	author = "Jakob Svanholm",
	author_email = "rymdlego@gmail.com",
	url = "https://github.com/rymdlego/vquery",
	description = "A tool for querying vCenter for various information.",
	keywords = "vSphere VMware vCenter",
	scripts=['vq'],
	packages=['vquery'],
	install_requires=['docopt', 'pyVmomi', 'future', 'six']
)
