from setuptools import setup
setup(name='pysemigroup',
      version='0.2c19',
      description='A tool to manipulate transitions semigroups and display them',
      url='http://github.com/charles-paperman/pysemigroup',
      author='Charles Paperman',
      author_email='charles.paperman@gmail.com',
      license='GPLv2+',
      packages=['pysemigroup'],
      keywords='sagemath automata semigroups monoid regular language',
      install_requires=["networkx","numpy"]
)
