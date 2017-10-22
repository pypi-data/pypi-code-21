from setuptools import setup

setup(
    name="p3_bitbucket",
    packages=['p3_bitbucket'],
    modules=['p3_bitbucket'],
    version="0.1.15",
    description="Bitbucket API",
    author="Andy Hsieh",
    author_email="andy.hsieh@hotmail.com",
    license='LICENSE.txt',
    scripts=['bin/p3_bitbucket'],
    url='https://github.com/bealox/p3-bitbucket',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests >= 2.18.3",
        'setuptools'
    ]

)
