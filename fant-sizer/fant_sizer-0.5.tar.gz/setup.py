from setuptools import setup, find_packages
from os.path import join, dirname

setup(
        name="fant_sizer",
        version="0.5",
        author="Rypiuk Oleksandr",
        author_email="ripiuk96@gmail.com",
        description="fant_sizer command-line file-information",
        url="https://github.com/ripiuk/fant_sizer",
        keywords="file command-line information size tool recursively",
        license="MIT",
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Utilities',
            'Environment :: Console',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6'
        ],
        packages=find_packages(),
        long_description=open(join(dirname(__file__), "README.rst")).read(),
        entry_points={
                "console_scripts":
                ['fant_sizer = fant_sizer.fant_sizer:main'],
            },
    )
