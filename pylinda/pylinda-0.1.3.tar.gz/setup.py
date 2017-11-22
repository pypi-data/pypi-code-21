from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='pylinda',
    version='0.1.3',
    description='',
    author_email='appa@engineer.com',
    license='MIT',
    packages=['pylinda'],
    scripts=['bin/pylinda-svr'],
    install_requires=[
    '',
    ],
    zip_safe=False
    )
