from setuptools import setup, find_packages
from codecs import open
import versioneer

with open('README.rst', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    requires = f.read()

with open('LICENSE.txt', 'r') as f:
    license = f.read()

setup(
        name='epic-code',
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),

        description='Another MCMC sampler for Cosmology',
        long_description=long_description,

        url='https://bitbucket.org/rmarcondes/epic',
        license=license, # new BSD with clause for arXiv citation

        author='Rafael Marcondes',
        author_email='rafael.marcondes@outlook.com',

        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            ],
        install_requires=requires.split(),
        packages=find_packages(),
        include_package_data=True,
        )



