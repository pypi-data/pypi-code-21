from setuptools import setup, find_packages


description = """
See `github repo <https://github.com/pior/pyramid_bugsnag>`_ for information.
"""


setup(
    name='pyramid_bugsnag',
    version='0.3',
    description='Pyramid extension to send exceptions to Bugsnag',
    long_description=description,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Framework :: Pyramid",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='wsgi pylons pyramid bugsnag tween exception handler',
    author="Pior Bastida",
    author_email="pior@pbastida.net",
    url="https://github.com/pior/pyramid_bugsnag",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['pyramid>=1.5', 'bugsnag'],
)
