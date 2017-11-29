from setuptools import setup

setup(
    name='philter_internal',    # This is the name of your PyPI-package.
    version='0.1.1',  # Update the version number for new releases
    packages=['philter_internal'],
    #include_package_data=True,
    package_data={'philter_internal': ['whitelist.pkl'],
    },
    entry_points={
        'console_scripts': [
            'philter = philter_internal.philter:main',
            'philter-annotation = philter_internal.philter_annotator:main',
            'philter-eval = philter_internal.philter_eval:main']
            },
        # The name of your scipt, and also the command you'll be using for calling it
    zip_safe = False,
    install_requires=[
          'nltk',
          'spacy'
      ],
    author='UCSF-ICHS',
    author_email='beaunorgeot@gmail.com'
)
