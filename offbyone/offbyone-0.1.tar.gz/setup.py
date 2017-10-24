from setuptools import setup

long_description = """
                    `offbyone` produces off by one "errors" in prints and in the interactive shell.
                    Simply import and enjoy. The print function is automatically wrapped to show
                    values off by one.
                    The underlying data is never touched, so no bugs should be introduced by this.
                   """

setup(name='offbyone',
      version='0.1',
      description='Produces off by one "errors" in prints and interactive shell',
      url='https://github.com/chinatsu/offbyone',
      author='chinatsu',
      author_email='lolexplode@gmail.com',
      long_description=long_description,
      license='MIT',
      packages=['offbyone'],
      keywords='off-by-one print',
      zip_safe=False)
