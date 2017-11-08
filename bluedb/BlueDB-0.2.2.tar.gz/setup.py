from setuptools import setup

readme = ''
with open('README.rst') as f:
    readme = f.read()

setup(
        name='BlueDB',
        author='EnderDas',
        url='https://github.com/Enderdas/BlueDB',
        packages=['BlueDB'],
        version='0.2.2',
        description='Like shelves but better...',
        long_description=readme
    )
