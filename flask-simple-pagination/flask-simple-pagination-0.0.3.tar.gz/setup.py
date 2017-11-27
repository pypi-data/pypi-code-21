from setuptools import setup

setup(
    version="0.0.3",
    name="flask-simple-pagination",
    description="A simple flask pagination library",
    url="https://github.com/MakerLabsDevelopment/flask-simple-pagination",
    author="Alex Good",
    email="alex@makerlabs.co.uk",
    license="MIT",
    py_modules="flask_simple_pagination",
    install_requires=[
        "flask"
    ],
    extras_require={
        "dev": [
            "PyHamcrest",
            "marshmallow",
            "ipython",
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3",
)

