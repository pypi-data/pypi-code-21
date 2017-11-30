from setuptools import setup

exec (open('dash_grid_layout/version.py').read())

setup(
    name='dash_grid_layout',
    version=__version__,
    author='FlightDataServices',
    packages=['dash_grid_layout'],
    include_package_data=True,
    license='MIT',
    description='Dash UI Component for using the React Grid Layout library',
    install_requires=[]
)
