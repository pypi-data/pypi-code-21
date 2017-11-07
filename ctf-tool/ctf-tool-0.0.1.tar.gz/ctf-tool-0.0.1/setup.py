from setuptools import find_packages, setup

setup(
    name='ctf-tool',
    version='0.0.1',
    author='Jose Francisco Arriagada A',
    author_email='jfarriagada91@gmail.com',
    description=('A simple capture the flag tool.'),
    long_description='',
    license='BSD',
    keywords='ctc capture the flag tool',
    url='https://github.com/jfarriagada/ctftool',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    package_data={
        'ctf-tool': ['*.txt']
    },
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.2',
        'Topic :: Utilities'
    ]
)
