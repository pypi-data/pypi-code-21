from setuptools import setup, find_packages

setup(
    name='poonia',
    version='0.1.1',
    description='Collection of small utilities',
    author='proteus',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        p=poonia.__main__:main
    ''',
    license='GPLv3',
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities"
    ]
)