from setuptools import setup
setup(
    name = 'strpy',
    version = '0.6.2',
    packages = ['strpy'], 
    description = 'STR python tools for computer vision and machine learning',
    author = 'Jeffrey Byrne',
    author_email = 'jeffrey.byrne@stresearch.com',
    url = 'https://github.com/stresearch/strpy',
    download_url = 'https://github.com/stresearch/strpy/archive/0.6.2.tar.gz', 
    install_requires=[
        "opencv-python",
        "numpy",  
        "scipy",
        "scikit-learn",
        "matplotlib",    
        "dlib",
        "h5py", 
    ],
    keywords = ['STR', 'vision', 'learning', 'janus'], 
    classifiers = [],
)

# Creating a pypi package
# 
# git commit -am "message"
# git push
# git tag 0.6.2 -m "strpy-0.6.2"
# git push --tags origin master
#
# to delete a tag
#   git tag -d x.y
#   git push origin :refs/tags/x.y
#
# create ~/.pypirc following https://packaging.python.org/guides/migrating-to-pypi-org/#uploading
# python setup.py register -r testpypi
# python setup.py sdist upload -r testpypi
#
# python setup.py register -r pypi
# python setup.py sdist upload -r pypi

