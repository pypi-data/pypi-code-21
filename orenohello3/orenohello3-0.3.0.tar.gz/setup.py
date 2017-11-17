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

    name='orenohello3',

    version='0.3.0',

    description='A sample Python project',

    long_description='This is a sample to say Hello!',

    url='https://github.com/yuris001/orenohello',

    author='oreore',

    author_email='hoge.fuga@test.test',

    license='MIT',

    classifiers=[

    'Development Status :: 3 - Alpha',

    'Intended Audience :: Education',

    'Topic :: Education',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 3.5',

    ],

    keywords='sample setuptools development',

    packages=['orenohello'],

    entry_points={

        'console_scripts': [

            'orenohello3=orenohello.orenohello:hello',

        ],

    },

)
