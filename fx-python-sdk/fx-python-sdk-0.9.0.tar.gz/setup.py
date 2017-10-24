import sys
from distutils.core import setup

VERSION = "0.9.0"

cmdclass = {}
if sys.version_info < (2, 7):
    raise Exception("Python 2.7 is required.")
if sys.version_info > (3, 0):
    raise Exception("Python 3 not supported at this time.")


def run_setup():
    setup(
        name="fx-python-sdk",
        version=VERSION,
        description="Python SDK for Impossible FX",
        author="Impossible Software",
        author_email="gh@impossiblesoftware.com",
        url="https://www.impossiblesoftware.com/",
        packages=["impossible_fx"],
        license="MIT License",
        cmdclass=cmdclass,
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Topic :: Multimedia :: Video"
        ],
        install_requires=[
            "requests",
            "protobuf",
        ]
    )

if __name__ == "__main__":
    run_setup()
