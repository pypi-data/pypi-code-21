from setuptools import setup, find_packages

setup(
    name = "pytdxupdate",
    version = "0.2",
    author= 'Adam.ding',
    description='update data from pytdx',
    packages = find_packages(),
    author_email='dxf813@126.com',
    url='http://www.cnblogs.com/dxf813/',
	install_requires=[
        'numpy',
        'pandas',
        'bcolz',
        'pytdx',
		'click',
    ],
    entry_points={
        'console_scripts': [
            'pytdx-update=update_bcolz_data.update_min_data:run',
        ]
    }
)
