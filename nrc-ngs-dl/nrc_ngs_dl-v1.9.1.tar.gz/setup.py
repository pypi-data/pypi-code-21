from setuptools import setup, find_packages
 
with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    requires = f.read()

setup(
    name='nrc_ngs_dl',
    description='software for downloading and handling sequence data from NRC-LIMS website',
    long_description=readme,
    version='v1.9.1',
    author='Chunfang Zheng',
    author_email='chunfang.zheng@canada.ca',
    license=license,
    packages = find_packages(exclude=('test')),
    install_requires = requires,
    scripts = ['config.ini.sample'],
    entry_points={
        'console_scripts': [
            'lims_downloader = nrc_ngs_dl.lims_downloader:main',
            ],
    }
)
