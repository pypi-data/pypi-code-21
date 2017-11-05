# coding=utf-8
import os

from setuptools import setup

setup(
    name='django-simple-shop',
    version='0.2.3',
    zip_safe=False,
    description='Generic e-commerce application for Django',
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    author='Evgeny Barbashov',
    author_email='evgenybarbashov@yandex.ru',
    url='https://github.com/bzzzzzz/django-simple-shop',
    packages=[
        'django_shop',
        'django_shop.tests',
        'django_shop.migrations',
        'django_shop.templatetags',
        'django_shop.utils',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
    install_requires=[
        'Django>=1.8',
        'django-phonenumber-field>=1.0',
        'Pillow>=3.0',
        'django-ckeditor'
    ],
)
