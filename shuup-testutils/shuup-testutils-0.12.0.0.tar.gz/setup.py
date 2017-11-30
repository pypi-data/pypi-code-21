import setuptools


def main():
    setuptools.setup(
        name='shuup-testutils',
        version='0.12.0.0',
        description='Some personal testutils for Shuup E-commerce Platform',
        url='https://gitlab.com/nilit/shuup-testutils',
        license='MIT',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Framework :: Django :: 1.9',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Topic :: Software Development',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Testing',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Office/Business',
        ],
        keywords='shuup',
        packages=setuptools.find_packages(),
        install_requires=[
            'shuup == 2.0',
            'shuup-utils >= 0.7, < 0.8',
            'beautifulsoup4 >= 4.5.3, < 4.6',
        ],
        extras_require={
            'dev': [
                'wheel >= 0.29.0',
                'twine >= 1.8.1, < 2',
            ],
        },
        include_package_data=True,
    )


if __name__ == '__main__':
    main()
