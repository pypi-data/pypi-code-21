from setuptools import setup, find_packages

setup(
    name='djcolour',
    description='Automatically use `colour.Color` in Python, `django.db.models.CharField` on the database, and `<input type="color">` on the forms.',
    url='https://github.com/jansegre/djcolour',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'colour>=0.1.4,<0.2',
    ],
    author='Jan Segre',
    author_email='jan@segre.in',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.11',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
