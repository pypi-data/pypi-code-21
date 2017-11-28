import setuptools

# import fastentrypoints

requirements = [
    'click==6.7',
]

setuptools.setup(
    name='zenv',
    version='0.0.1',
    description="",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'zenv=zenv.cli:main',
            'zv=zenv.cli:main',
        ],
    },
    include_package_data=True,
)
