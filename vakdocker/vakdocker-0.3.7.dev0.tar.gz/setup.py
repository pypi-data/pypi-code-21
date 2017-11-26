from setuptools import setup, find_packages

#http://python-packaging.readthedocs.io/en/latest/minimal.html
#https://stackoverflow.com/questions/45207128/failed-to-upload-packages-to-pypi-410-gone

setup(
	name='vakdocker',
	version='0.3.7dev',
        packages = find_packages(),
        include_package_data=True,

        scripts=['vakdocker/bin/vakdocker'],

        setup_requires=[ "setuptools_git >= 0.3", ],

        install_requires=[
            'pycrypto',
            'pyopenssl',
            'docker'
            ],

        author = "Pankaj Garg",
        author_email = "garg.pankaj83@gmail.com",
        description = "Vaksana Utility to Manage Secure Docker",
        long_description=open('README.md').read(),
        license = "PSF",
        keywords = "Vaksana",
        url = "http://vaksana.com/docker"
)
