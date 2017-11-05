from setuptools import setup
import codecs
import cm2c

def long_description():
    with codecs.open('README.rst', encoding='utf8') as f:
        return f.read()

setup(
    name='CM2C',
    version=cm2c.__version__,
    scripts=['cm2c.pyz'],
    url='https://gitlab.com/ArnaudM/CM2C',
    license='MIT',
    author='Arnaud Moura',
    author_email='arnaudmoura@gmail.com',
    description='Convert Movie To Cast (CM2C) is a Python application to convert any videos files with subtitle(s) to '
                'video supported by Google Chromecast.',
    long_description=long_description(),
    platforms=['Any'],
    install_requires=['progressbar2>=3.12.0'],
    classifiers=[
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],
    keywords='video movie chromecast ffmpeg executable'
)
