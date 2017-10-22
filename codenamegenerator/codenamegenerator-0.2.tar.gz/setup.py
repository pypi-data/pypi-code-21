from setuptools import setup

setup(
    name="codenamegenerator",
    version="0.2",
    author="Mario César Señoranis Ayala",
    author_email="mariocesar.c50@gmail.com",
    url="https://github.com/mariocesar/code-name-generator",
    packages=["codenamegenerator"],
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python",
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.5",
      "Programming Language :: Python :: 3.6"
    ],
    entry_points={
      'console_scripts': [
          'codenamegenerator=codenamegenerator:__main__'
        ],
    }
)
