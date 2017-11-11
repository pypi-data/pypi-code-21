# -*- coding: utf-8 -*-


from distutils.core import setup


setup(
    name='restchain',
    py_modules=['restful'],
    version='0.2.2',
    description='restful',
    author='zakzou',
    author_email='zakzou@gmail.com',
    keywords=['restful'],
    install_requires=[
        "requests",
        "dotmap",
    ],
    classifiers=[],
)
