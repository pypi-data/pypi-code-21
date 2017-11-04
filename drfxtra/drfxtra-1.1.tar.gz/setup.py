from setuptools import setup, find_packages

import drfxtra

setup(name='drfxtra',
    version=drfxtra.__version__,
    description="Extra features for Django Rest Framework viewsets and serializers",
    long_description=open('description.rst').read(),
    author='Paul Martin',
    author_email='greatestloginnameever@gmail.com',
    url='https://github.com/primal100/drf-xtra',
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)