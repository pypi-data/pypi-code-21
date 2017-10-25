from setuptools import setup, find_packages


__VERSION__ = '0.1.9'


setup(
    name='bakerstreet',
    version=__VERSION__,
    description="The place where most characters meet",
    long_description="RPC defnition for our services",
    url='https://github.com/appknox/bakerstreet',
    author='dhilipsiva',
    author_email='dhilipsiva@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='appknox rpc bakerstreet',
    packages=find_packages(),
    install_requires=[
        "grpcio==1.4.0",
        "grpcio-tools",
    ],
    zip_safe=False,
    extras_require={
        'dev': [''],
        'test': [''],
    },
)
