import glob
import os

from setuptools import setup


if __name__ == '__main__':

    try:
        with open('readme.rst') as f:
            long_description = f.read()
    except FileNotFoundError:
        long_description = 'Configuration for python made easy'

    from man.manconfig import ManConfig

    config = ManConfig()

    setup(
        name='{libname}',
        version=config.version,
        packages=config.packages,
        url='https://github.com/{github_username}/{libname}',
        license='MIT',
        author='{fullname}',
        author_email='{email}',
        description='{description}',
        long_description=long_description,
        install_requires=config.dependancies,
        package_data=dict((pkg, list(set(file for pat in paterns for file in glob.glob(os.path.join(pkg, pat), recursive=True)))) for(pkg, paterns) in config.package_data.items()),
        data_files=[(dir, list(set(file for patern in pats for file in glob.glob(patern, recursive=True)))) for (dir, pats) in config.data_files]
    )
