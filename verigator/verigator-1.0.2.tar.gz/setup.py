# -*- coding: utf-8 -*-

from setuptools import setup
from messente.verigator import __version__ as version

setup(
    name="verigator",
    version=version,
    packages=["messente", "messente.verigator"],
    setup_requires=["requests==2.18.4"],
    install_requires=["requests==2.18.4"],
    tests_require=["requests-mock==1.3.0", "mock==2.0.0"],
    author="Verigator.com",
    author_email="admin@verigator.com",
    description="Official Verigator.com API library",
    license="Apache License, Version 2",
    keywords="verigator messente sms verification 2FA pin code",
    url="http://messente.com/documentation/",
    test_suite="messente.verigator.test"
)
