from setuptools import setup, find_packages

setup(name='dxl-pygate',
      version='0.5.1',
      description='A simplified python interface for Gate.',
      url='https://github.com/Hong-Xiang/pygate',
      author='Hong Xiang',
      author_email='hx.hongxiang@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['fs', 'click', 'pyyaml',
                        'rx', 'jinja2', 'dxl-dxpy>=0.4'],
      scripts=['bin/pygate'],
      zip_safe=False)
