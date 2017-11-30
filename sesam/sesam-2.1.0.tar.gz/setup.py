from setuptools import setup

setup(
    name='sesam',
    version='2.1.0',
    packages=['sesam'],
    package_data={
        'sesam': ['wsdl/*.wsdl']
    },
    url='https://github.com/ovidner/python-sesam',
    license='MIT',
    author='Olle Vidner',
    author_email='olle@vidner.se',
    description='',
    install_requires=[
        'attrs==17.*',
        'zeep==2.4.*'
    ]
)
