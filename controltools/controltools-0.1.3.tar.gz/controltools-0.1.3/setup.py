from setuptools import setup

setup(name='controltools',
      version='0.1.3',
      description='Control System Wrapper',
      url='https://github.com/Faggioni/controltools',
      author='Miguel Faggioni',
      author_email='miguelfaggioni@gmail.com',
      license='MIT',
      install_requires = [
            'numpy',
            'control'
      ],
      zip_safe=False)
