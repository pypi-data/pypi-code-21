from setuptools import setup, find_packages

setup(
    name='cxmate',
    version='0.13.0',
    description='SDK for creating cxMate services',
    long_description="""
    cxmate-py provides a Python SDK for interacting with [cxMate](https://github.com/ericsage/cxmate), an adapter that allows Cytoscape to talk to network services. This SDK enables quick and painless development of a cxMate service, follow the Getting Started guide to learn more about the process.
    """,
    url='https://github.com/cxmate/cxmate-py',
    author='Eric Sage, Brett Settle',
    author_email='eric.david.sage@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='cytoscape networkx network biology cxmate',
    packages=find_packages(),
    install_requires=['grpcio', 'networkx==1.11'],
)
