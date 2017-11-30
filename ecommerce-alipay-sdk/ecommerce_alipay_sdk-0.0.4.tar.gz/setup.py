from setuptools import setup, find_packages
print find_packages(exclude=['test'])
setup(
    name='ecommerce_alipay_sdk',
    version='0.0.4',
    keywords=('ecommerce', 'alipay', 'ecommerce-alipay'),
    description='An unofficial AliPay unofficial SDK for ecommerce module of edx',
    license='MIT License',
    install_requires=["pycryptodome", "six"],

    author='seaswander',
    author_email='sevenseaswander@gmail.com',
    url='https://github.com/seaswander/ecommerce-alipay-sdk',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(exclude=['test']),
    platforms='any',
)
