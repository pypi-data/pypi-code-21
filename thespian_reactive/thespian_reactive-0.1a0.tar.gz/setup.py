from setuptools import setup, find_packages

long_description = """
Python reactive and enterprise data extensions for the Thespian project.
https://github.com/asevans48/ReactiveThespian
"""

setup(
    name = 'thespian_reactive',
    #description='Reactive extensions for Python Thespian',
    long_description=long_description,
    version = '0.1a',
    description = 'Reactive Streams for Python',
    author = 'Andrew Evans',
    author_email = 'aevans48@simplrinsites.com',
    python_requires='~=3.5',
    keywords='reactive thespian actor etl stream',
    packages=find_packages(exclude=['reactive','tests']),
    install_requires=['atomos', 'thespian', 'dill','pytest','pika'],
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ])


