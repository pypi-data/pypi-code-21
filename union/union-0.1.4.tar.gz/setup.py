from setuptools import setup, find_packages


VERSION = (0, 1, 4)
version = '.'.join(map(str, VERSION))

setup(
    name='union',
    version=version,
    author='Union Inc.',
    author_email='hello@unionbilling.com',
    description='A Python library for accessing the Union Billing API.',
    url='https://github.com/unionbilling/union-python',
    license='MIT',
    keywords='union billing api',
    packages=find_packages(),

    install_requires=[
        'setuptools',
        'requests>=2.7.0',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

)

