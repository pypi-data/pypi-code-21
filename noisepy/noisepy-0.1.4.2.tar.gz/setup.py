from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='noisepy',
      version='0.1.4.2',
      description='generates random noisey b/w images',
      long_description=readme(),
      classifiers=[
          'Environment :: Console',
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Multimedia :: Graphics',
          'Topic :: Artistic Software',
      ],
      keywords='noisepy noise image generator snow random',
      url='https://lymbycfyk.github.io/noisepy/',
      author='lymbycfyk',
      author_email='lymbycfyk@posteo.de',
      license='MIT',
      packages=['noisepy'],
      python_requires='>=3',
      install_requires=[
          'numpy',
          'scipy',
      ],
      entry_points={
            'console_scripts': ['noisepy=noisepy.__main__:main'],
      },
      include_package_data=True,
      zip_safe=True)
