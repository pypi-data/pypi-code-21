from setuptools import setup

setup(name='martian_chatbot',
      version='0.4.0',
      description='Chatbot creation module',
      url='https://jzitkovic@gitlab.martianandmachine.com/service/martian-chatbot.git',
      author='Josip Zitkovic',
      author_email='josip@martian.agency',
      license='MIT',
      packages=['chatbot', 'chatbot.utils', 'chatbot.models'],
      install_requires=[
          'pymongo',
          'requests',
          'simplejson'
      ],
      zip_safe=False)
