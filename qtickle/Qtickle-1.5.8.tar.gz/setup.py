from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        zip_safe=False,
        name='Qtickle',
        version="1.5.8",
        author='Nicholas Finch',
        author_email='tisaconundrum2@github.com',
        packages=find_packages(),
        url='https://github.com/tisaconundrum2/Qtickle',
        description="""
        A script designed to aid in saving values inside Qt objects.
        It works by inspecting for object names and then collecting their
        values.
        """,
        long_description=open('README.rst').read(),

    )
