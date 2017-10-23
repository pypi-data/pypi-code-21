from setuptools import setup, find_packages

setup(
    name='trunity_3_client',
    version='0.5',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
      ],
    url='',
    license='MIT',
    author='hunting',
    author_email='VicHuntig@yandex.ua',
    description='API client for Trunity 3 learning platform and more'
)
