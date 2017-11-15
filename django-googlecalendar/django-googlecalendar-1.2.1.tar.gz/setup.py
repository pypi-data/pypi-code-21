from setuptools import setup, find_packages

from googlecalendar import get_version
setup(
    name = "django-googlecalendar",
    packages = find_packages(),
    install_requires=[
        "gdata",
        "FeinCMS",
    ],
    version = get_version(),
    description = "This project implements Google Calendar API as django objects.",
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
    include_package_data=True,
)
