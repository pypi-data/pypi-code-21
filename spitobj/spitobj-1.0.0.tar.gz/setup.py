try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


long_description = """
Fake data object initialization
"""


setup(
    name="spitobj",
    description="Spitobj - fake data object initialization",
    long_description=long_description,
    license="MIT",
    version="1.0.0",
    author="xliiv",
    author_email="tymoteusz.jankowski@gmail.com",
    maintainer="xliiv",
    maintainer_email="tymoteusz.jankowski@gmail.com",
    url="https://github.com/xliiv/spitobj",
    packages=['spitobj'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ]
)
