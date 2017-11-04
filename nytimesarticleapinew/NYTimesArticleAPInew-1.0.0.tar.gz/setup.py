import ez_setup
ez_setup.use_setuptools() # in case users don't have setuptools installed

from setuptools import setup

import NYTimesArticleAPInew

setup(
    name="NYTimesArticleAPInew",
    description="Python wrapper for the New York Times Article Search API",
    version=NYTimesArticleAPInew.__version__,
    author=NYTimesArticleAPInew.__author__,
    author_email="champebarton@gmail.com",
    url="https://github.com/champebarton/NYTimesArticleAPI",
    license="MIT",
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
        "Topic :: Office/Business :: News/Diary",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "requests >= 2.7.0",
    ],
    packages=[
        "NYTimesArticleAPInew",
    ],
    keywords="nytimes new york times api article search nyt journalism news",
    test_suite="NYTimesArticleAPInew.tests.NYTimesArticleAPITests",
    zip_safe=True,
)
