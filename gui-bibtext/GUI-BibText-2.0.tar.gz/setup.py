from setuptools import setup
 
setup(
	name='GUI-BibText',    
	version='2.0',                          
	url="https://github.com/himanshuRepo/Bibtex-Key-with-GUI",
	py_modules=['gBibText','Bibtext','extract','gscholar'],
	entry_points={
    	'console_scripts': [
        	'gBibText=gBibText:main',
    	],
	},

	)