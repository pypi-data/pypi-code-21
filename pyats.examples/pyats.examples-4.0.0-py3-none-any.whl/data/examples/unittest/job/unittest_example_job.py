# To run the job:
# easypy <pyats_root>/examples/unittest/job/unittest_example_job.py
# Description: This example shows how to execute an unittest script
import os
from ats.easypy import run

def main():
    # Find the location of the script in relation to the job file
    test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    testscript = os.path.join(test_path, 'unittest_example_script.py')
    
    run(testscript=testscript,
        unittest = True)

