try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='calcium',
    version='0.1',
    description='Minimal interactive shell framework',
    author='URANO Ryoya',
    author_email='urano.works.mail@gmail.com',
    py_modules=['calcium'],
    license='MIT',
)

