from setuptools import setup, find_packages

__author__ = 'ikarishinjigao'

setup(
    name='uec',
    version='1.0.0',
    description='Scripts for getting UEC student info and lectures info.',
    author='ikarishinjigao',
    author_email='ikarishinjigao@gmail.com',
    url='https://github.com/ikarishinjigao/UEC-Scraping',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    packages=find_packages(),
    include_package_data=True,
    keywords=['uec', 'UEC', 'GPA', 'gpa'],
    license='MIT License',
    install_requires=[
        'click',
        'lxml',
        'prettytable',
        'bs4',
        'selenium',
        'requests',
        'progressbar2',
    ],
    entry_points="""
        [console_scripts]
        uec = uec.uec:cli
    """,
)