from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='noisepy',
      version='0.1.4',
      description='generates random noisey b/w images',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Topic :: Multimedia :: Graphics',
      ],
      keywords='noisepy noise image generator snow random',
      url='https://lymbycfyk.github.io/noisepy/',
      author='lymbycfyk',
      author_email='lymbycfyk@posteo.de',
      license='MIT',
      packages=['noisepy'],
      install_requires=[
          'numpy',
          'scipy',
      ],
      entry_points={
            'console_scripts': ['noisepy=noisepy.__main__:main'],
      },
      include_package_data=True,
      zip_safe=True)
