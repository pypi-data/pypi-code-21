from setuptools import setup

setup(
    name='makeitgreen',    # This is the name of your PyPI-package.
    version='0.6.1',                          # Update the version number for new releases
    scripts=['migg'],                  # The name of your scipt, and also the command you'll be using for calling it
    description='Makes your Git Green every time you run this package'
)
