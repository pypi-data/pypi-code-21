from setuptools import setup

setup(
	name='recall-cmds',
	version='0.0.4',
	url='https://github.com/mavcook/recall',
	author='Maverick Cook',
	author_email='mav@mavcook.com',
	description='A tool to view and edit templated commands that you forget.',


	scripts=['recall.py'],

	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
	],

	python_requires='>=3',
)
