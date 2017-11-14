from setuptools import setup, find_packages

setup(
    name='flamespeed',
    version='0.1.0',
    author='YTB',
    author_email = 'student@g.harvard.edu',
    packages=find_packages(),
    package_data={'flamespeed': ['../data/*.*', '../data/rxns_test/*.*']},
    url='https://github.com/flamespeed/cs207-FinalProject/',
    license='MIT',
    description='Chemical kinetics library for Python',
    long_description=open('README.md').read(),
    python_requires='>=3',
    install_requires=[
        "NumPy >= 1.8",
        "Scipy >= 0.13"
    ],

)
