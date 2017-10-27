from distutils.core import setup
VERSION='0.0.11'
setup(
	name='clearlove',
	version=VERSION,
	description='I will prove that I am the best jungle, no ,djangoer in the world',
	author='lovekano',
	author_email='814953866@qq.com',
	include_package_data=True,
	packages=['clearlove'],
	url='https://www.shadowflow.com',
	install_requires=[''],
	license='MIT Licence',
	zip_safe=False,
	entry_points={
        'console_scripts': [
            'clearlove=clearlove:clearlove',
        ]
    }
	)