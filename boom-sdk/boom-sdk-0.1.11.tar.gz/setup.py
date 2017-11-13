from setuptools import setup, find_packages


classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries',
]

setup(
    name='boom-sdk',
    author='Jordan Ambra',
    author_email='jordan@serenitysoftware.io',
    url='https://github.com/boomletsgo/boom-sdk-python',
    version='0.1.11',
    classifiers=classifiers,
    description='SDK for interacting with Boom',
    keywords='boom',
    packages=["boom"],
    install_requires=["six>=1.0.0", "declaration>=0.2.5"],
    include_package_data=True,
    license='The Unlicense',
)
