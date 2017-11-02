try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='marvinhelp',
    version='0.1.4',
    description = 'Unhelpful advice from a very smart robot.',
    url='https://github.com/rolfantlers',
    author='Anders Amundson',
    author_email='amundson@gmail.com',
    license='MIT',
    packages=['marvinhelp'],
    install_requires=['nose'],
    python_requires='>=3',
    keywords =['nonsense','robots','advice'],
    scripts=['bin/marvin-advice']
)
