from setuptools import setup

setup(name='DateJS',
      description='Python Library that converts Javascript Date objects to Python Datetime objects',
      version='0.1.12',
      url='https://github.com/rithik/DateJS',
      author='Rithik Yelisetty',
      author_email='rithik@gmail.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
      ],
      packages=['DateJS'],
      install_requires=[
          'PyExecJS>=1.4.1',
          'pytz>=2016.10'
      ],
      entry_points={
          'console_scripts': [
              'DateJS=DateJS.main:run'
          ]
      }
)