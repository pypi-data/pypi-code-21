# coding: utf-8
from setuptools import setup
from os import path
from setuptools.command.install import install

here = path.abspath(path.dirname(__file__))


class MyInstall(install):
    def run(self):
        print("-- installing... (powered by lesscli) --")
        install.run(self)


setup(
        name = 'lesscli',
        version='0.0.1',
        description='Tookit for generating command line interfaces 「嘞是CLI」',
        long_description='\n\nREADME: https://github.com/qorzj/lesscli',
        url='https://github.com/qorzj/lesscli',
        author='qorzj',
        author_email='inull@qq.com',
        license='MIT',
        platforms=['any'],

        classifiers=[
            ],
        keywords='lesscli cli fire',
        packages = ['lesscli'],
        install_requires=[],

        cmdclass={'install': MyInstall},
        entry_points={
            'console_scripts': [
                'lesscli = lesscli.cli:main',
                ],
            },
    )
