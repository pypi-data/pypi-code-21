from os.path import join, dirname

from setuptools import setup, find_packages

PACKAGE = "async_task_processor"
NAME = "async-task-processor"
DESCRIPTION = "Simple package to run async tasks"
AUTHOR = "Klimov Konstantin"
AUTHOR_EMAIL = "moelius1983@gmail.com"
URL = "https://github.com/moelius/async-task-processor"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages=find_packages(exclude=["tests.*", "tests"]),
    install_requires=[
        'uvloop==0.8.1',
        'asynctnt-queue==0.0.5',
        'tarantool==0.5.5',
        'janus==0.3.0',
    ],
    zip_safe=False,
)
