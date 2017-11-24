from setuptools import setup

setup(name='pysett',
      version='0.6',
      description='Simple YAML settings',
      url='https://github.com/mlackman/pysettings',
      author='Mika Lackman',
      author_email='mika.lackman@gmail.com',
      license='MIT',
      packages=['pysett'],
      python_requires='>3.6',
      install_requires=[
          'PyYaml',
      ],
      zip_safe=False)
