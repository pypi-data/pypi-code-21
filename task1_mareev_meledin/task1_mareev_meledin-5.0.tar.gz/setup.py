from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='task1_mareev_meledin',

      version='5.0',
      
      description='Workshop 3 course. Autumn 17-18. Exercise 1.',
      
      author='Mareev Gleb and Meledin Stanislav',
   
      author_email='wowmagic.gm@gmail.com',
     
      license='MIT',
     
      install_requires=[
          'numpy',
          'scipy'
      ],
      
      long_description=readme(),
     
      include_package_data=True,
      
      keywords='task1 mareev maledin cs msu',
      
      url='https://github.com/GlebOlegovich/prac-2017-2018/tree/task1-mareev-meledin/submissions/task1/mareev-meledin/task1_mareev_meledin',
    
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Mathematics',
      ],
     
      packages = ['task1_mareev_meledin'],
     
      zip_safe=False)
