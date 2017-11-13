from setuptools import setup

setup(name='youtube_cue',
      version='0.1.0.dev3',
      packages=['youtube_cue'],
      entry_points={'console_scripts': ['youtube-cue=youtube_cue:main']},

      install_requires=['musicbrainzngs', 'lxml', 'requests', 'youtube-dl', 'cssselect'],

      description='Generate a cue sheet for a youtube url',
      url='https://github.com/bugdone/youtube-cue',
      keywords='youtube cue',
      author='bugdone',
      author_email='bugdone@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
      ],
      )
