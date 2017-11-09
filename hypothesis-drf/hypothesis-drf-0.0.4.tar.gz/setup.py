import os

from setuptools import setup, find_packages

# We use the README as the long_description
# TODO md -> rst
readme_path = os.path.join(os.path.dirname(__file__), "README.md")

tests_require = ['pytest~=3.2', 'Django<2', 'flake8<4']


setup(
    name='hypothesis-drf',
    use_scm_version=True,
    url='https://gitlab.com/schmidt.simon/hypothesis-drf',
    author='Simon Schmidt',
    author_email='schmidt.simon@gmail.com',
    description='Hypothesis DRF',
    long_description=open(readme_path).read(),
    long_description_content_type='text/markdown; charset=UTF-8',
    license='MPL v2',
    zip_safe=False,
    packages=find_packages('src/'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'hypothesis[fakefactory]',
        'hypothesis-fspaths',
        'djangorestframework',
    ],
    setup_requires=['setuptools_scm'],
    extras_require={
        "tests": tests_require,
    },
    classifiers=[
        'Topic :: Software Development :: Testing',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
    ],
)
