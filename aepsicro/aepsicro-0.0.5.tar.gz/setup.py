from setuptools import setup, find_packages

setup(
	name = 'aepsicro',
	version = '0.0.5',
	author = 'Antonio Eduardo Téllez Santos',
	author_email = 'aironmail@gmail.com',
	description = 'Psicrometría / Psychrometrics',
	long_description = open('README.rst').read(),
	license = 'GNU GPLv3',
	url = 'https://pypi.python.org/pypi/aepsicro',
	packages = find_packages(),
    keywords =['psychrometrics', 'psicrometría', ],
	install_requires=['numpy', 'scipy', 'matplotlib', ],
	test_suite = 'tests',
	classifiers = [
    	'Development Status :: 3 - Alpha',
    	'Intended Audience :: Science/Research',
    	'Intended Audience :: Developers',
    	'Programming Language :: Python',
    	'Programming Language :: Python :: 3.3',
    	'Programming Language :: Python :: 3.4',
    	'Programming Language :: Python :: 3.5',
    	'Topic :: Scientific/Engineering',
    	'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    	]
	)
