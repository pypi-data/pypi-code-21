from testcube_client import business
import os

os.chdir('c:\\temp')

business.run(team_name='UnitTest',
             product_name='TestProduct',
             result_xml_pattern='*.xml'
             )
