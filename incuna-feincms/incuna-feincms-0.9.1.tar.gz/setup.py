from setuptools import setup, find_packages

from incunafein import get_version
setup(
    name = "incuna-feincms",
    packages = find_packages(),
    include_package_data=True,
    version = get_version(),
    description = "Provides enhancements to FeinCMS.",
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
)
