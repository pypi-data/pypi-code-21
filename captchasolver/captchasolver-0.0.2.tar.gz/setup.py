from setuptools import setup, find_packages

from captchasolver.__init__ import version

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(
    name='captchasolver',
    version=version,
    author='Rafael Alves Ribeiro',
    author_email='rafael.alves.ribeiro@gmail.com',
    packages=['captchasolver'],
    install_requires=[requires],
    include_package_data=True,
    package_data={'captchasolver': ['./data/model.pkl']},
    entry_points={
            'console_scripts': [
                    'captchasolver = captchasolver.cmdline:main',
                ],
        }
)
