from setuptools import setup, find_packages

setup(
    name='forrest',
    version='0.0.1',
    description='',
    author='Hector Vergara',
    author_email='hvergara@gmail.com',
    license='MIT',
    scripts = ['bin/forrest'],
    packages=find_packages(),
    install_requires = [
        'awscli'
    ]
)