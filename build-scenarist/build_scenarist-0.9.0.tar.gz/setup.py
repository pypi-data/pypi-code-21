from setuptools import setup

from scenarist import version

setup(name='build_scenarist',
      version=version,
      description='',
      url='http://github.com/sogimu/scenarist',
      author='Aleksandr Lizin',
      author_email='sogimu@nxt.ru',
      license='MIT',
      packages=['build_scenarist'],
      scripts=['scenarist.py'],
      package_data={'build_scenarist': ['src/*']},
      zip_safe=False)
