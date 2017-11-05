from setuptools import setup

installation_requirements = ['requests', 'requests-toolbelt', 'six']

try:
    import enum
    del enum
except ImportError:
    installation_requirements.append('enum')

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    required = requirements.read().splitlines()


setup(
    name='Morrison',
    packages=['morrison'],
    version='0.9.0',
    install_requires=required,
    description="Python Wrapper for Facebook Messenger Platform",
    long_description=long_description,
    author='The Columbia Lion',
    author_email='operations@columbialion.com',
    url='https://github.com/thecolumbialion/Morrison',
    license='MIT',
    download_url='https://github.com/thecolumbialion/Morrison/archive/0.9.0.tar.gz',
    keywords=[
        'facebook messenger', 'python', 'wrapper', 'bot', 'messenger bot', 'python wrapper', 'chatbots'
    ],
    classifiers=[], )