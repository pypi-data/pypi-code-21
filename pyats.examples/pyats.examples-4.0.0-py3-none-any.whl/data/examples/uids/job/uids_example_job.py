# To run the job:
# easypy <pyats_root>/examples/uids/job/uids_example_ids_job.py
# Description: This example shows looping and variants in pyats

import os

from ats.easypy import run
# Data structure used to mentions that to execute
from ats.datastructures.logic import And, Or, Not

def main():

    # Find the location of the script in relation to the job file
    test_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    testscript = os.path.join(test_path, 'uids_example_script.py')

    #####
    # Skip Example
    #####

    #__task1
    # Skip Container/Section that match tc_two and my_looped_testcase
    run(testscript=testscript,
        uids=Not('tc_two','my_looped_testcase'))

    #__task2
    # Skip Container/Section that match common_setup
    run(testscript=testscript,
        uids=Not('common_setup'))


    # Skip Container/Section that match common_setup, and also skip
    # Container/Section that begins with loop2

    #__task3
    # ^loop2 will match a loop of a testcase section.
    # It also demonstrate that regex can be used
    run(testscript=testscript,
        uids=Not('common_setup','^loop2$'))

    #####
    # Execute Example
    #####

    #__task4
    # Execute Container/Section that match common_setup
    run(testscript=testscript,
        uids=And('common_setup'))

    #__task5
    # Execute Container/Section that match tc_two or my_looped_testcase
    run(testscript=testscript,
        uids=Or('tc_two','my_looped_testcase'))

    #__task6
    # Execute Container/Section that match common_setup or test_two, or begins
    # with loop2
    run(testscript=testscript,
        uids=Or('common_setup','^loop2','test_two'))

    #####
    # Skip and Execute Example
    #####

    #__task7
    # Skip loop1, and execute tc_two, my_looped_testcase
    run(testscript=testscript,
        uids=And(Not('loop1'), Or('tc_two','my_looped_testcase')))

    #####
    # Default behavior
    #####
    
    #__task8
    # By default everything will be executed, as no uids is specified.
    run(testscript=testscript)
