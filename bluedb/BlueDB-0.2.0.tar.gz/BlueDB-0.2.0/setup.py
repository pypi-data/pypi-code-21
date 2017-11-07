from setuptools import setup

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
        name='BlueDB',
        author='EnderDas',
        url='https://github.com/Enderdas/BlueDB',
        version='0.2.0',
        description='Like shelves but better...',
        long_description=readme
    )
