from setuptools import setup, find_packages
import doorstopqt

setup(
    name="doorstopqt",
    author="Johnny Oskarsson",
    author_email="johnny@joskar.se",
    version=doorstopqt.VERSION,
    packages=find_packages(),
    install_requires=[
        "doorstop >= 1.4, < 2",
        "pyqt5 >= 5.9, < 6",
        "markdown >= 2.6.9, < 3"
    ],
    entry_points={
        'console_scripts': [
            'doorstop-qt = doorstopqt.mainview:main'
        ]
    }
)
