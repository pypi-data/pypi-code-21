from setuptools import setup

setup(name='neatmartinet',
      version ='0.2.4',
      description='Ad-hoc pandas dataframe and string cleaning functions implemented in unreadable Python.',
      author='Amber Ocelot',
      author_email='AmberOcelot@gmail.com',
      license='na',
      packages=['neatmartinet'],
      zip_safe=False,
      url='https://github.com/ogierpaul/neatmartinet',
      download_url='https://github.com/ogierpaul/neatmartinet.git',
      keywords=['pandas', 'data cleaning'],
      install_requires=['neatmartinet','fuzzywuzzy','pandas','numpy'],
      classifiers=[
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Intended Audience :: Developers',
          'Topic :: Utilities'
      ]
      )
