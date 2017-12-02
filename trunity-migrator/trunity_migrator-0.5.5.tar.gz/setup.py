from setuptools import setup, find_packages


setup(
    name='trunity_migrator',
    version='0.5.5',
    packages=find_packages(),
    scripts=['trunity_migrator/bin/trunity-migrator'],
    install_requires=[
        'requests',
        'beautifulsoup4',
        'trunity-3-client',
      ],
    url='',
    license='MIT',
    author='hunting',
    author_email='VicHunting@yandex.ua',
    description='Library for migrating content from Trunity 2 to Trunity 3 learning platform.'
)
