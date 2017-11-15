from setuptools import setup

exec (open('dash_annotated_syntax_highlighter/version.py').read())

setup(
    name='dash_annotated_syntax_highlighter',
    version=__version__,
    author='chriddyp',
    packages=['dash_annotated_syntax_highlighter'],
    include_package_data=True,
    license='MIT',
    description='A specialized syntax highlighter that places code comments into the margins',
    install_requires=[]
)
