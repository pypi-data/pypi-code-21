from setuptools import setup


requires = ["requests==2.18.4"]


setup(
    name='flounder',
    version='0.0.6',
    description='flounder is a library that create Entity of Dialogflow. This library uses RestAPI of dialogflow. It is not an official library.',
    url='https://github.com/flatfisher/flounder',
    author='flatfisher',
    author_email='shimano.entou@gmail.com',
    license='MIT',
    keywords=['dialogflow', 'dialogflow entity'],
    packages=[
        "flounder"
    ],
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 2.7',
    ]
)