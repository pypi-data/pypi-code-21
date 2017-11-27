from setuptools import setup

setup(
    name="flask-simple-pagination",
    description="A simple flask pagination library",
    url="https://github.com/MakerLabsDevelopment/flask-simple-pagination",
    author="Alex Good",
    email="alex@makerlabs.co.uk",
    license="MIT",
    modules="flask_simple_pagination",
    install_requires=[
        "flask"
    ],
    extras_require={
        "dev": [
            "PyHamcrest",
            "marshmallow",
            "ipython",
        ]
    }
)

