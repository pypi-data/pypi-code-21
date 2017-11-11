from setuptools import setup, find_packages

setup(
    name='avilabsutils',
    version='1.2.1',
    description='Common utilities used by Avilay Labs',
    author='Avilay Parekh',
    author_email='avilay@avilaylabs.net',
    license='MIT',
    url='https://bitbucket.org/avilay/utils',
    packages=find_packages(),
    install_requires=['termcolor', 'colorama', 'numpy'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)
