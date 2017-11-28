from setuptools import setup

setup(name='keyholder',
      version='0.1',
      description='Wrapper for multiple key-value stores',
      url='https://github.com/s0urc3c0d3/keyholder',
      author='Grzegorz Dwornicki',
      author_email='gd1100@gmail.com',
      license='MIT',
      packages=['keyholder'],
      install_requires=['kazoo','python-etcd'],
      zip_safe=False)