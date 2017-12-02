import setuptools

setuptools.setup(
    name='pyblueprint',
    version='0.0.1',
    description='draw diagrams using python',
    long_description='draw diagrams using python',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    maintainer='Mark Veltzer',
    maintainer_email='mark.veltzer@gmail.com',
    keywords=[
        "svg",
        "diagram",
        "python",
        "inkscape",
    ],
    url='https://github.com/veltzer/pyblueprint',
    download_url='https://github.com/veltzer/pyblueprint',
    license='MIT',
    platforms=[
        "python3",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        "svgwrite",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],
    data_files=[
    ],
    entry_points={'console_scripts': [
    ]},
)
