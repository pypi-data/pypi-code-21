from setuptools import setup, find_packages

requires = [
    'beautifulsoup4==4.6.0',
    'simple_table'
]

setup(
    name='douban_rating',
    version='0.0.2',
    description='Get douban rating in terminal.',
    url='https://github.com/Frederick-S/douban-rating',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'douban-rating = douban_rating.main:main'
        ]
    },
    install_requires=requires,
    test_suite="tests"
)
