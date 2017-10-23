from setuptools import setup, find_packages

setup(
    name='sf_tools',
    author='sfarrens',
    author_email='samuel.farrens@gmail.com',
    version='1.1',
    url='https://github.com/sfarrens/sf_tools',
    download_url='https://github.com/sfarrens/sf_tools/archive/0.1.tar.gz',
    packages=find_packages(),
    license='MIT',
    long_description=open('README.txt').read(),
)
