from setuptools import setup

def readme():
    with open('README.rst', 'r') as f:
        return f.read()

setup(
    name='subgrab',
    version='0.17',
    description='A python script for automating subtitles downloading.',
    long_description=readme(),
    url='https://github.com/RafayGhafoor/Subscene-Subtitle-Grabber',
    author='Rafay Ghafoor',
    author_email='rafayghafoor@protonmail.com',
    packages=['subgrab', 'subgrab.providers', 'subgrab.utils'],
    entry_points = {'console_scripts': ['subgrab = subgrab.__main__:main']},
    zip_safe = False,
    license='GPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords='subtitle automation subscene opensubtitles media',
    install_requires=['requests', 'bs4', 'lxml'],
)
