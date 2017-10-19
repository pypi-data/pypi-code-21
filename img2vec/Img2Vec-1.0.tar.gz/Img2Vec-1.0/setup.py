from setuptools import setup, find_packages

setup(
    name="Img2Vec",
    version=1.0,
    description={
        "An implementation for Img2Vec."
    },
    author='fpsandnoob',
    author_email='hzlxcc@gmail.com',
    license="BSD License",
    packages=find_packages(),
    platforms=["all"],
    url="https://github.com/fpsandnoob/img2vec",
    classifiers=[
            'Development Status :: 4 - Beta',
            'Operating System :: OS Independent',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries'
        ],
    install_requires=[
        "tensorflow-gpu>=1.00",
        "keras>=2.0.8",
        "scikit-learn>=0.18.1",
        "Pillow>=4.1.1"
    ]
)
