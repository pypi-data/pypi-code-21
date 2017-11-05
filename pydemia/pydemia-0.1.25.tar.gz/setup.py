from setuptools import setup, find_packages


long_desc = """
This is made for some specific environment.
This contains some db connection tools & analysis tools. 
"""

setup(name='pydemia',
	version='0.1.25',
	description='Useful tools for Analysis',
	long_description=long_desc,
	url='http://github.com/pydemia/pydemia',
	author='Young Ju Kim',
	author_email='pydemia@gmail.com',
	license='MIT License',
	classifiers=[
		# How Mature: 3 - Alpha, 4 - Beta, 5 - Production/Stable
		'Development Status :: 3 - Alpha',
		'Programming Language :: Python :: 3.5'
		],
	packages=find_packages(exclude=['contrib', 'docs', 'tests']),
	install_requires=[
			  'scikit-image', 'pandas', 'numpy', 'scipy', 'statsmodels', 
				'pymysql', 'psycopg2', 'sqlalchemy',
				'ibm_db_sa', 'opencv-python' 
				#'cx_Oracle'
					],
	zip_safe=False)

