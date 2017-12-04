# install requirements
try:
    import configparser
except:
    import pip
    pip.main(['install', 'configparser'])
try:
    import requirements
except:
    import pip
    pip.main(['install', 'git+https://github.com/davidfischer/requirements-parser.git#egg=requirements_parser'])

# import
import os
import setuptools
import pkg_utils

# package name
name = 'pkg_utils'
dirname = os.path.dirname(__file__)

# convert README.md to README.rst
pkg_utils.convert_readme_md_to_rst(dirname)

# get package metadata
md = pkg_utils.get_package_metadata(dirname, name)

# install package
setuptools.setup(
    name=name,
    version=md.version,
    description=("Utilities for linking setuptools with version metadata, "
                 "README files, requirements files, and restoring overridden entry points"),
    long_description=md.long_description,
    url="https://github.com/KarrLab/" + name,
    download_url='https://github.com/KarrLab/' + name,
    author="Karr Lab",
    author_email="karr@mssm.com",
    license="MIT",
    keywords='setuptools, pip, requirements, GitHub, pandoc',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    package_data={
        name: [
            'VERSION',
        ],
    },
    install_requires=md.install_requires,
    extras_require=md.extras_require,
    tests_require=md.tests_require,
    dependency_links=md.dependency_links,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
