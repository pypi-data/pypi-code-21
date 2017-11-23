from setuptools import setup, find_packages

install_requires = [
    "psutil>=5.4.*",
]

setup(
    name='apdaemon',
    version='0.2.3',
    packages=find_packages(),
    url='https://github.com/gamelife1314/apdaemon',
    license='MIT',
    author='fudenglong',
    author_email='fudenglong1417@gmail.com',
    description='python daemon tool.',
    install_requires=install_requires,
    long_description=open('README.rst').read(),
    platforms=["linux", "Macos"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
