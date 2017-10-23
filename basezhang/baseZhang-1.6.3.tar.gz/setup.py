import os
from distutils.core import setup

NAME = 'baseZhang'
_MAJOR = 1
_MINOR = 6
_MICRO = 3
VERSION = '%d.%d.%d' % (_MAJOR, _MINOR, _MICRO)
DESCRIPTION = "mir-feature-tools @ZHANG Xu-long"

SEP = os.sep


def long_description():
    readme = open('README.md', 'r').read()
    changelog = open('CHANGELOG.md', 'r').read()
    return changelog + '\n\n' + readme


setup(
    packages=['baseZhang', 'pymir'],
    data_files=[('.' + SEP, ['CHANGELOG.md', 'README.md']),
                ('.docs' + SEP,
                 ['docs' + SEP + 'install.md', 'docs' + SEP + 'pymir.md', 'docs' + SEP + 'pythonTutorial.md']),
                ('.' + SEP + 'docs' + SEP + 'img' + SEP,
                 ['docs' + SEP + 'img' + SEP + 'pycharm_command_line_arguments.png',
                  'docs' + SEP + 'img' + SEP + 'pycharm_create_new_project.png',
                  'docs' + SEP + 'img' + SEP + 'pycharm_create_new_project_pure_python.png',
                  'docs' + SEP + 'img' + SEP + 'pycharm_hello_open.png',
                  'docs' + SEP + 'img' + SEP + 'pycharm_new_file_input.png',
                  'docs' + SEP + 'img' + SEP + 'pycharm_new_python_file.png',
                  'docs' + SEP + 'img' + SEP + 'pycharm_open.png', 'docs' + SEP + 'img' + SEP + 'pycharm_output.png',
                  'docs' + SEP + 'img' + SEP + 'pycharm_run.png',
                  'docs' + SEP + 'img' + SEP + 'terminal_screenshot.png']),
                ]
    ,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description(),
    author="ZHANG Xu-long",
    author_email="fudan0027zxl@gmail.com",
    license="BSD",
    url="http://zhangxulong.site",
    keywords='audio music sound',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",

    ],
    install_requires=['stft', 'numpy', 'pandas', 'matplotlib', 'h5py',
                      'tqdm','hmmlearn',
                      'PyAudio', 'pydub', 'pyPdf', 'PyYAML', 'six',
                      'SoundFile', 'Theano', 'scikit-learn==0.18.1', 'Keras',
                      'librosa'],
)
