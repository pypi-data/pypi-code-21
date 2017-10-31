from setuptools import setup

setup(
    name='RNAscrutiny',
    version='0.7',
    description='Generative models from scRNA-seq data.',
    keywords='generative single cell RNA sequencing transcriptomics genomics',
    url='http://lbm.niddk.nih.gov/mckennajp/RNAscrutiny',
    author='Steffen K Cromwell, Joseph P McKena, Vipul Periwal',
    author_email='joepatmckenna@gmail.com',
    license='MIT',
    packages=['RNAscrutiny'],
    install_requires=['numpy', 'matplotlib', 'sklearn'],
    zip_safe=False)
