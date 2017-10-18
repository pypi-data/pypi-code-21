from setuptools import setup, find_packages


required = []
try:
    with open('requirements.txt') as f:
        required = f.read().splitlines()
except FileNotFoundError:
    pass

setup(
    name="Terrene",
    version="0.0.12",
    description="Terrene's Python SDK",
    url="https://docs.terrene.co",
    author="Terrene",
    author_email="developers@terrene.co",
    license='MIT',
    keywords="terrene",
    packages=find_packages(exclude=["test"]),
    install_requires=required,
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
