from setuptools import setup

setup(
      name='iupick',
      version='0.1.0',
      description='A python client for iuPick',
      long_description='A python client for iuPick services.',
      url='https://github.com/iupickmx/iupick-python',
      author='iuPick',
      author_email='devops@iupick.com',
      license='BSD-3-Clause',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.4',
      ],
      keywords='iuPick client',
      install_requires=['requests'],
      python_requires='>=3.4',
)
