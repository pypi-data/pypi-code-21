from setuptools import setup

setup(
    name="cerca",
    version="0.1",
    description="A library and utility for scanning static websites for links",
    url="https://github.com/dang3r/cerca",
    author="Daniel Cardoza",
    author_email="daniel@redbooth.com",
    license="MIT",
    packages=["cerca"],
    scripts=["scripts/cerca"],
    zip_safe=False
)
