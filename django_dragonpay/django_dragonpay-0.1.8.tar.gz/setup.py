from setuptools import setup

setup(
    name='django_dragonpay',
    version='0.1.8',
    description='DragonPay plugin for Django',
    author='Ivan Dominic Baguio',
    author_email='baguio.ivan@gmail.com',
    url='https://github.com/ibaguio/django_dragonpay',
    packages=[
        'django_dragonpay', 'django_dragonpay.api',
        'django_dragonpay.migrations'],
    install_requires=[
        'requests>=2.11.1',
        'Django>=1.8.0',
        'lxml==3.7.3',
        'pycrypto>=2.6.1',
    ],
    keywords='django dragonpay payment',
    license='MIT',
    include_package_data=True,
)

__author__ = 'Ivan Dominic Baguio'
