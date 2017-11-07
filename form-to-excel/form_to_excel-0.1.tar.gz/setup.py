from setuptools import setup

setup(name='form_to_excel',
      version='0.1',
      description='Convert Word/PDF documents to Excel Workbooks',
      url='https://github.com/aseli1/dm_form_to_excel',
      author='Anthony Seliga',
      author_email='anthony.seliga@gmail.com',
      license='MIT',
      packages=['form_to_excel'],
      install_requires=[
          'openpyxl',
          'python_docx',
          'docx',
          'pdfminer.six',
      ],
      scripts=['bin/convert_paper_form'],
      zip_safe=False)
