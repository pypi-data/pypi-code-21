from pathlib import Path
from setuptools import setup, find_packages

root = Path(__file__).parent

# avoid import dependencies during setup when retrieving version
_version = {}
with root.joinpath("cvbuilder/__version__.py").open("rt") as fp:
    exec(fp.read(), _version)

with root.joinpath('./README.rst').open("rt", encoding="utf-8") as f:
    long_description = f.read()

# data_files does not supporting wildcards in subdirectories -> glob relative path for each config file
config_files = [str(f.relative_to(root)) for f in root.joinpath("cvbuilder/config").glob("**/*.json")]

setup(
    name="cvbuilder",
    version=_version.get("__version__"),

    # url="https://git.macaque.de/developer/cv",
    license="MIT",

    keywords=["opencv", "computer vision"],
    description="""Package for building OpenCV {} including Python 3 bindings from the official sources."""
        .format(_version.get("__cv2version__")),
    long_description=long_description,

    author="Hannes Römer",
    author_email="none@example.org",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: C++",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        # "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development",
    ],

    # packages=["cvbuilder",
    #           "cvbuilder.__syspatch__",
    #           "cvbuilder.__syspatch__.patched",
    #           "cvbuilder.__syspatch__.vendor",
    #           "config"],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    data_files=[("config", config_files)],

    install_requires=[
        "pip>=9.0.1",
        "requests",
        "numpy",
    ],

    platforms="LINUX",
    python_requires=">=3.4",

    # setup_requires=["pytest-runner"],
    tests_require=["green"],

    entry_points="""
        [console_scripts]
        cvbuilder=cvbuilder.cli:cli
        """,

)
