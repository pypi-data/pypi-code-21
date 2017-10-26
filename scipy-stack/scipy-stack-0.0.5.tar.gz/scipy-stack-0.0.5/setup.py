from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

setup(
    name="scipy-stack",
    version="0.0.5",
    packages=find_packages(),

    install_requires=[
        'numpy>=1.13.1',
        'scipy>=1.0.0',
        'matplotlib>=2.0.2',
        'jupyter>=1.0.0',
        'pandas>=0.20.3',
        'sympy>=1.1.1',
        'nose>=1.3.7',
    ],

    author="David O'Connor",
    author_email="david.alan.oconnor@gmail.com",
    url='https://github.com/David-OConnor/scipy-stack',
    description="Helper to install the SciPy stack",
    long_description=readme,
    license="",
    keywords="scipy-stack, scipy, numpy, pandas, jupyter",
)
