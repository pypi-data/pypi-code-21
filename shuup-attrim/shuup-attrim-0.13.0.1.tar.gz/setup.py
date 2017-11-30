import setuptools

from setup_commands import collect_commands


def main():
    setuptools.setup(
        name='shuup-attrim',
        version='0.13.0.1',
        description='Multi-value attributes addon for Shuup E-Commerce Platform',
        url='https://gitlab.com/nilit/shuup-attrim',
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
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Office/Business',
        ],
        keywords=['shuup', 'attributes'],
        packages=setuptools.find_packages(),
        include_package_data=True,
        entry_points={'shuup.addon': 'attrim=attrim'},
        cmdclass=collect_commands(),
        install_requires=[
            'shuup == 2.0',
            'psycopg2 >= 2.6.2, < 3',
            'shuup-testutils >= 0.12, < 0.13',
            'shuup-utils >= 0.7, < 0.8',
        ],
    )


if __name__ == '__main__':
    main()
