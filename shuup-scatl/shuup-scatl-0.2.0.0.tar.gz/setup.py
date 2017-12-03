import setuptools

from setup_commands import collect_commands


def main():
    setuptools.setup(
        name='shuup-scatl',
        version='0.2.0.0',
        description='Catalog filters addon for Shuup E-Commerce Platform',
        url='https://gitlab.com/nilit/shuup-scatl',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Framework :: Django :: 1.9',
            'Intended Audience :: Developers',
            'Intended Audience :: Financial and Insurance Industry',
            'Topic :: Software Development',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Office/Business',
        ],
        keywords=['shuup', 'attributes'],
        packages=setuptools.find_packages(),
        include_package_data=True,
        entry_points={'shuup.addon': 'scatl=scatl'},
        cmdclass=collect_commands(),
        install_requires=[
            'shuup == 2.0',
            'shuup-attrim >= 0.13, < 0.14',
            'psycopg2 >= 2.6.2, < 3',
            'django-solo == 1.1.2',
            
            'parameterized >= 0.6.1, < 0.7',
            'shuup-testutils >=  0.12, < 0.13',
            'shuup-utils >= 0.7, < 0.8',
        ],
    )


if __name__ == '__main__':
    main()
