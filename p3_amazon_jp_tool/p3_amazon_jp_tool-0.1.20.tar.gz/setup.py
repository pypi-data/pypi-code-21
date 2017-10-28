from setuptools import setup

setup(
    name="p3_amazon_jp_tool",
    packages=['p3_amazon_jp_tool'],
    modules=['p3_amazon_jp_tool'],
    version="0.1.20",
    description="Amazon JP Sales Reports",
    author="Andy Hsieh",
    author_email="andy.hsieh@hotmail.com",
    license='LICENSE.txt',
    scripts=['bin/p3_amazonjp_sales_report'],
    url='https://bitbucket.com/bealox/p3_amazon_jp_report',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "httplib2 == 0.10.3",
        'setuptools'
    ]

)
