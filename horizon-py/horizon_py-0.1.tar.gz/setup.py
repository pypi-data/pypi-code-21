from setuptools import setup

setup(name='horizon_py',
      version='0.1',
      description='DeepHorizon API Client',
      url='https://github.com/deep-horizon/horizon_py',
      author='Ben Whittle',
      author_email='benwhittle31@gmail.com',
      license='MIT',
      packages=['horizon_py'],
      install_requires=['requests'],
      zip_safe=False)