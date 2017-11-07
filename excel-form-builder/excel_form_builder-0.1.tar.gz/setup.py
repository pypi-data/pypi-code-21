from setuptools import setup

setup(name='excel_form_builder',
      version='0.1',
      description='Convert Word/PDF documents to Excel Workbooks',
      url='https://github.com/aseli1/dm_excel_form_builder',
      author='Anthony Seliga',
      author_email='anthony.seliga@gmail.com',
      license='MIT',
      packages=['excel_form_builder'],
      install_requires=[
          'openpyxl',
          'colorama',
      ],
      scripts=['bin/create_form'],
      zip_safe=False)
