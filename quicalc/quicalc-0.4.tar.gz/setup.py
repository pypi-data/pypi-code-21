from setuptools import setup

def readme():
    with open('README.md') as readme:
        return readme.read()

setup(
        name = 'quicalc',
        version = '0.4',
        description = 'Simple Terminal Calculator',
        long_description = readme(),
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python :: 3.5',
            'Topic :: Scientific/Engineering :: Mathematics'
            ],
        keywords = 'tools math terminal python calculator',
        url = 'http://pythonhosted.org/QuiCalc',
        author = 'Abhishta Gatya',
        author_email = 'abhishtagatya@yahoo.com',
        packages = ['bin'],
        entry_points = {
            'console_scripts' : ['calc=bin.calc:main']
            },
        python_requires = '>=3',
        include_package_data = True,
        zip_safe = False
        )
