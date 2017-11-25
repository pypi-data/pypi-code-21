from setuptools import setup, find_packages

setup(
    name='crosswordpy',
    version="0.0.2",                 
    description="Crossword",
    long_description="No hint crossword",
    package_data = {'crosswordpy': ['crosswordpy_data/*.txt']},
    packages=find_packages(),
    author='Saito Tsutomu',
    license='PSFL',
    classifiers=[
        "Development Status :: 1 - Planning"
    ],
    keywords='crosswordpy',
    install_requires=['pygame', ],
    entry_points={'console_scripts': ['crosswordpy = crosswordpy:main']},
)