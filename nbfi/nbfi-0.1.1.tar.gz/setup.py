from setuptools import setup, find_packages

setup(
    name = 'nbfi',
    version = '0.1.1',
    description = 'A tiny new brainfuck interpreter in pure python 3',
    url = 'https://github.com/Bestoa/py-brainfuck',
    author = 'Besto',
    author_email = 'bestoapache@gmail.com',
    license = 'MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],
    keywords='brainfuck',
    packages = find_packages(),
    install_requires = [],
)
