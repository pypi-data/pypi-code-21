from setuptools import setup, find_packages

setup(
    name='imagerater',    					# This is the name of your PyPI-package.
    version='0.1.2',                          # Update the version number for new releases
    scripts=['imagerater'],                  # The name of your script, and also the command you'll be using for calling it
    description='Simple cmd line tool to display, rate images and then save an imageAndRating matrix.',
    long_description='Simple cmd line tool to display, rate images and then save an imageAndRating matrix.',
    url='https://github.com/jaza10/imagerater.git',
    author='Jan Zawadzki',
	author_email='jaza10@me.com',
	license='MIT',
	classifiers=[
    	# How mature is this project? Common values are
    	#   3 - Alpha
    	#   4 - Beta
    	#   5 - Production/Stable
    	'Development Status :: 3 - Alpha',

    	# Indicate who your project is intended for
    	'Intended Audience :: Developers',
    	'Topic :: Software Development :: Build Tools',

    	# Pick your license as you wish (should match "license" above)
     	'License :: OSI Approved :: MIT License',

    	# Specify the Python versions you support here. In particular, ensure
    	# that you indicate whether you support Python 2, Python 3 or both.
    	'Programming Language :: Python :: 2',
    	'Programming Language :: Python :: 2.6',
    	'Programming Language :: Python :: 2.7',
    	'Programming Language :: Python :: 3',
    	'Programming Language :: Python :: 3.2',
    	'Programming Language :: Python :: 3.3',
    	'Programming Language :: Python :: 3.4',
	],
	keywords='image rating classification neural network data gathering imagerater imagerating',
	packages=find_packages(),
	#install_requires=['numpy','glob','matplotlib','sys','getopt'],
	python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
	py_modules=["imagerater"],
	entry_points={
    'console_scripts': [
        'sample=sample:main',
    	],
	},
)
