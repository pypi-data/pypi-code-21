from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name					= 'isimage'
	, version				= '0.1.2'
	, packages				= find_packages()
	, entry_points			= {'console_scripts':['analyse_image = isimage.analyse_image:main'
												, 'select_images = isimage.select_images:main'
												]}
	, author				= 'Ilya Patrushev'
	, author_email			= 'ilya.patrushev@gmail.com'
	, description			= 'A module and scripts for analysis of whole-mount in-situ hybridisation images.'
	, long_description		= read('README')
	, license				= 'GPL v2.0'
	, package_data			= {'isimage.analyse_image':['test_images/*'], 'isimage.select_images':['*.dump', '*.txt', 'test_images/*.*', 'test_images/*/*.*']}
	, url					= 'https://github.com/ilyapatrushev/isimage'
	
	, install_requires 		= ['Pillow>=2.9.0'
							 , 'matplotlib>=1.4.3'
							 , 'numpy>=1.9.2'
							 , 'pandas>=0.16.0'
							 , 'scikit-learn>=0.15.2'
							 , 'scipy>=0.15.1'
							 , 'python-pptx>=0.5.7'
							 , 'pbr>=0.11'
							 , 'six>=1.7'
							 , 'funcsigs>=0.4'
							 ]
)
