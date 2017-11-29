from setuptools import setup


with open('README.md') as f:
    readme = f.read()


setup(name='businessoptics',
      version='0.2.0',
      description='Client for the BusinessOptics API',
      long_description=readme,
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
      ],
      url='https://github.com/BusinessOptics/businessoptics_client',
      author='BusinessOptics',
      author_email='alex.mojaki@gmail.com',
      license='MIT',
      packages=['businessoptics'],
      install_requires=[
          'requests>=2,<3',
          'future<1',
      ],
      include_package_data=True,
      zip_safe=False)
