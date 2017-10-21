from setuptools import setup


#setup(name='language-model-char-predictor-test',    # This is the name of your PyPI-package.
#      version='0.1',                                # Update the version number for new releases
#      scripts=['CharPredictor']                     # The name of your scipt, and also the command you'll be using for calling it
#)


setup(name='dictionary-model',
      version='0.2',
      description='Model for tracking context of utterance and predicting future characters.',
      #url='http://github.com/storborg/funniest',
      author='Michał Kosturek',
      author_email='eemkos@gmail.com',
      license='Michał Kosturek',
      packages=['dictionary_model'],
      install_requires=['sklearn', 'keras', 'wget', 'numpy'],
      zip_safe=False)