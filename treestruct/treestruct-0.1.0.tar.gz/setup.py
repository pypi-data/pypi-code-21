from setuptools import setup, find_packages


setup(
    name='treestruct',
    version='0.1.0',
    description='Simplify the task of creating, traversing, manipulating and visualizing tree structure',
    author='Shady Rafehi',
    url='https://github.com/srafehi/treestruct',
    author_email='shadyrafehi@gmail.com',
    packages=find_packages(),
    install_requires=['graphviz'],
    keywords=['tree', 'traversal', 'graph', 'graphviz']
)
