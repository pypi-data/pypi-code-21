from setuptools import setup

setup(name='p_stone_labs',
      version='0.32',
      description='P-Stone Labs',
      url='http://github.com/gravitt8460',
      author='P-Stone',
      author_email='max.gravitt@gmail.com',
      license='MIT',
      packages=['p_stone_labs'],
      scripts=['bin/numberguess'],
      py_modules=['numberguess', 'leaderboard', 'gameplay'],
      data_files=['leaderboard.csv'],
      zip_safe=False)
