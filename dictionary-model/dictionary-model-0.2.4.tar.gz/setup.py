from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='dictionary-model',
      version='0.2.4',
      description='Model for tracking context of utterance and predicting future characters.',
      long_description=readme(),
      author='Michał Kosturek',
      author_email='eemkos@gmail.com',
      license='Michał Kosturek',
      packages=['dictionary_model'],
      install_requires=['sklearn', 'keras', 'wget', 'numpy'],
      zip_safe=False)