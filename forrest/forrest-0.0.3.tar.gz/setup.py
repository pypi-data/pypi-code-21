from setuptools import setup, find_packages

setup(
    name='forrest',
    version='0.0.3',
    description='Utility for run ephemeral applications on cloud instances',
    author='Hector Vergara',
    author_email='hvergara@gmail.com',
    license='MIT',
    scripts = ['bin/forrest'],
    packages=find_packages(),
    install_requires = [
        'awscli'
    ]
)
