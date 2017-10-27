from setuptools import setup, find_packages
from codecs import open
from os import path


# here = path.abspath(path.dirname(__file__))
#
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name="ChessComAPILibrary",
    version='0.1.0.dev1',
    description="Python client/helper library for chess.com's PubAPI.",
    setup_requires=['setuptools-markdown'],
    long_description_markdown_filename='README.md',
    url='https://github.com/walidmujahid/ChessComAPILibrary',
    author='Walid Mujahid وليد مجاهد',
    author_email='walid.mujahid.dev@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='chess.com rest readonly api pubapi client helper library',
    find_packages=['library'],
    install_requires=['tortilla', 'pytest', 'requests', 'vcrpy'],
    python_requires='>=3',
)
