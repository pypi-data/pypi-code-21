from setuptools import setup, find_packages

setup(
    name='flask-wtf-storage',
    version='0.0.2',
    keywords=["flask", "wtf", "storage", "google storage"],
    description='extend flask-wtf to use google storage',
    license='MIT License',
    install_requires=[
        'Flask',
        'Jinja2',
        'WTForms',
        'Flask_WTF',
        'google-cloud',
    ],

    author='liupeng',
    author_email='liupeng.dalian@gmail.com',

    packages=find_packages(),
    platforms='any'
)
