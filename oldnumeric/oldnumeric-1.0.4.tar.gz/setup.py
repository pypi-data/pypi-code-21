from setuptools import setup, find_packages

setup(name='oldnumeric',
      description='The oldnumeric numpy package',
      author='xoviat',
      author_email='xoviat@noreply.users.github.com',
      packages=find_packages(),
      install_requires=[
            'numpy',
      ],
      setup_requires=[
            'setuptools_scm',
      ],
      use_scm_version=True,
     )
