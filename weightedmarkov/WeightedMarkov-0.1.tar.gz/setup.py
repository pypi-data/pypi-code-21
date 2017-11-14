from setuptools import setup

setup(name='WeightedMarkov',
      version='0.1',
      description='Implementation of Weighted Markov Chain as in Wai Ki Ching, Eric S. Fung, Michael K. Ng',
      url='https://github.com/sada-narayanappa/WeightedMarkov.git',
      author='Code Red',
      author_email='sada@geospaces.org',
      license='MIT',
      packages = ['WeightedMarkov'],
      package_data={'WeightedMarkov':['*']},
      zip_safe=False,
      install_requires=['Jupytils', 'cvxopt'],
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',
            
          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          #'Topic :: Jupyter Prettification :: Utilities ',
      
          # Pick your license as you wish (should match "license" above)
           'License :: OSI Approved :: MIT License',
      
          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          #'Programming Language :: Python :: 2',
          #'Programming Language :: Python :: 2.6',
          #'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ],
)
