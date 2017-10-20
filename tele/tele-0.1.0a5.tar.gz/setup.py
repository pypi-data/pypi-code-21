from setuptools import setup, find_packages

setup(
    name='tele',
    version='0.1.0a5',
    packages=find_packages(),
    author='Aiden Nibali',
    description='Telemetry for PyTorch',
    test_suite='tests',
    install_requires=[
        'graphviz',
        'h5py',
        'numpy',
        'Pillow',
        'requests',
        'torch',
        'torchnet',
        'torchvision',
    ],
)
