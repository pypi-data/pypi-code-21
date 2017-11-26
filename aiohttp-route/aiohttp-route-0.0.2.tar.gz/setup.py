from setuptools import setup


setup(
    name='aiohttp-route',
    version='0.0.2',
    description=("@route decorator for aiohttp.web"),
    long_description=(
        "@route decorator for aiohttp.web that needs no global variables"
    ),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: AsyncIO',
    ],
    author='Kolokotronis Panagiotis',
    url='https://github.com/panagiks/aiohttp-route/',
    license='MIT',
    packages=['aiohttp_route'],
    install_requires=[
        'aiohttp>=2.0.0'
    ],
)
