import setuptools

# until we make printing pretty
# noinspection PyPep8
setuptools.setup(
    name='pyclassifiers',
    version='0.0.3',
    description='classifiers from pypi',
    long_description='classifiers from pypi',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    maintainer='Mark Veltzer',
    maintainer_email='mark.veltzer@gmail.com',
    keywords=['classifiers', 'python', 'pypi', 'setuptools', 'distutils'],
    url='https://veltzer.github.io/pyclassifiers',
    download_url='https://github.com/veltzer/pyclassifiers',
    license='MIT',
    platforms=['python3'],
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=['Development Status :: 4 - Beta', 'Environment :: Console', 'Operating System :: OS Independent', 'Programming Language :: Python', 'Programming Language :: Python :: 3', 'Topic :: Utilities'],
    data_files=[],
    entry_points={'console_scripts': []},
)
