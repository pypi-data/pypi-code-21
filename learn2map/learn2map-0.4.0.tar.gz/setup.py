"""
Setup learn2map package.
"""

from setuptools import setup, find_packages

setup(
    name='learn2map',
    version='0.4.0',
    description='Spatial mapping from remote sensing data',
    url='https://gitlab.com/alanxuliang/a1610_learn2map',

    author='Alan Xu',
    author_email='bireme@gmail.com',

    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='DRC Forest Biomass',
    # package_dir={'': 'src'},
    # packages=find_packages(where='src', exclude=['data', 'docs', 'tests']),
    packages=find_packages(exclude=['data', 'docs', 'tests']),

    install_requires=[
        'numpy',
        'pandas',
        'GDAL>=2.0',
        'lxml',
        'scikit-learn>=0.18',
    ],

    entry_points={
        'console_scripts': [
            'rf_estimator=learn2map.rf_estimator:main',
            'csv_output=learn2map.rf_estimator:csv_output',
        ],
    },
)
