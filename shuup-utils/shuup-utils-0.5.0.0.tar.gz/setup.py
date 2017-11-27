import setuptools


setuptools.setup(
    name='shuup-utils',
    version='0.5.0.0',
    description='Some personal dev utils for Shuup E-commerce Platform',
    url='https://gitlab.com/nilit/shuup-utils',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Office/Business',
    ],
    keywords='shuup',
    packages=setuptools.find_packages(),
    install_requires=[
        'shuup == 2.0',
    ],
    extras_require={
        'dev': [
            'wheel >= 0.29.0',
            'twine >= 1.8.1, < 2',
        ],
    },
    include_package_data=True,
)
