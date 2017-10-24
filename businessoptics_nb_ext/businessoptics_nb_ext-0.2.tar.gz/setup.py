from setuptools import setup

setup(name='businessoptics_nb_ext',
      version='0.2',
      description='BusinessOptics IPython notebook extensions',
      url='http://github.com/BusinessOptics/businessoptics_nb_ext',
      author='James Saunders',
      author_email='james@businessoptics.biz',
      license='MIT',
      packages=['businessoptics_nb_ext'],
      zip_safe=False,
      install_requires=['nbformat', 'notebook'])
