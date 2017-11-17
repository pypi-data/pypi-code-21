from setuptools import setup





#setup(
#
#    name='hello',
#
#    version='0.0.1',
#
#    packages=['hello'],
#
#    entry_points={
#
#        'console_scripts': [
#
#            'hello=hello.hello:hello',
#
#        ],
#
#    },
#
#)

setup(

    name='orenohello',

    version='0.2.0',

    description='A sample Python project',

    long_description='This is a sample to say Hello!',

#    url='https://github.com/sirouma/hello',

    author='ore',

#    author_email='sirouma.09@gmail.com',

    license='MIT',

    classifiers=[

    'Development Status :: 3 - Alpha',

    'Intended Audience :: Education',

    'Topic :: Education',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3.5',

    ],

    keywords='sample setuptools development',

    packages=['hello'],

    entry_points={

        'console_scripts': [

            'hello=hello.hello:hello',

        ],

    },

)
