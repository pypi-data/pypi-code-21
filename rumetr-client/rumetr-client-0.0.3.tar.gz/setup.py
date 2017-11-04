from setuptools import find_packages, setup

setup(
    name='rumetr-client',
    version='0.0.3',
    description="Client for rumetr.com API",
    keywords=[],
    url="https://github.com/f213/rumetr-client/",
    author="Fedor Borshev",
    author_email="f@f213.in",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        'requests',
        'scrapy',
    ],
    include_package_data=True,
    zip_safe=False,
)
