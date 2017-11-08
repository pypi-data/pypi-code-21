import subprocess


'''
This script is used to call the data_validation_testcases.py
Here we can pass different folders on which we want to perfrom the validations
'''
my_input = ['Programme']
for each in my_input:
    print(each)
    subprocess.call(['python3.4', 'data_validation_testcases.py', '-v', each])
