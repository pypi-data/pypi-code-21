from setuptools import setup, find_packages

setup(name='dxl-pygate',
      version='0.8.4',
      description='A simplified python interface for Gate.',
      url='https://github.com/Hong-Xiang/pygate',
      author='Hong Xiang',
      author_email='hx.hongxiang@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['fs', 'click', 'pyyaml',
                        'rx', 'jinja2', 'dxl-dxpy>=0.5'],
      scripts=['bin/pygate'],
      data_files=[('scripts', ['scripts/map_bash_sample.sh',
                               'scripts/map_bash.sh', 'scripts/map_zsh.sh', 'scripts/merge_zsh.sh', 'scripts/pygate.yml'])],
      zip_safe=False)
