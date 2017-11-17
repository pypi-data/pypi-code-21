# To run the job:
# easypy <pyats_root>/examples/datafile/job/datafile_job.py
# Description: This example demonstrates how datafiles work in AEtest

import os
from ats.easypy import run

def main():
    # Find the location of the script in relation to the job file
    test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    testscript = os.path.join(test_path, 'testscript.py')

    # Execute the testscript with no datafile
    run(testscript=testscript)

    # run with simple datafile
    run(testscript=testscript,
        datafile = os.path.join(test_path, 'data', 'simple_data.yaml'))

    # run with extended datafile
    run(testscript=testscript,
        datafile = os.path.join(test_path, 'data', 'extended_data.yaml'))
