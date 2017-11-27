from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='vpgtools',
      version='0.1',
      description='Computer vision tools for the study of politics',
      url='https://github.com/CasAndreu/vpgtools',
      author='Andreu Casas',
      author_email='andreucasas@nyu.edu',
      license='MIT',
      packages=['vpgtools'],
       install_requires=[
          'numpy',
          'matplotlib'
      ],
      zip_safe=False)