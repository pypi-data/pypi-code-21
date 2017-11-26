from setuptools import setup

setup(
    name="brainfudge",
    version='0.0.1',
    author="Zwork101",
    author_email="zwork101@gmail.com",
    packages=["brainfudge"],
    entry_points={'console_scripts': ['brainfudge = brainfudge.fudge:main']}
)