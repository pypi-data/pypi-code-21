#/usr/bin/env python
import time
import sys
import subprocess
import shlex
verbose=True

def print_error(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()
    exit()

def print_msg(message,print_out=True):
    if print_out:
        sys.stdout.write(message)
        sys.stdout.flush()

def test_methylpy_import(function_name,verbose):
    print_msg("- importing %s: " %(function_name),
              verbose)
    try:
        exec("from methylpy import "+function_name)
        print_msg("pass\n",verbose)
    except:
        print_msg("failed\nExit\n",verbose)
        exit()

def get_executable_version(exec_name):
    try:
        sys.stdout.write("- find %s: " %(exec_name))
        if exec_name != "java":
            out = subprocess.check_output(shlex.split(exec_name+" --version"))
            out = out.decode("utf-8")
        else:
            out = subprocess.check_output(shlex.split(exec_name+" -version"),
                                          stderr=subprocess.STDOUT)
            out = out.decode("utf-8")
            out = out.replace("\"","")
        first_line = out.split("\n")[0]
        fields = first_line.split(" ")
        print("found version %s" %(fields[-1]))
        return(True)
    except:
        sys.stdout.write("failed\n")
        return(False)

print("Tests start")
print(time.asctime(time.localtime(time.time())))
print("")
start_time = time.time()

f_stdout = open("test_output_msg.txt",'w')
f_stderr = open("test_error_msg.txt",'w')

# 9 - merge allc
sys.stdout.write("\nTest merge-allc: ")
try:
    subprocess.check_call(
        shlex.split("methylpy merge-allc "
                    +"--allc-files data/allc_P0_FB_1.tsv.gz data/allc_P0_FB_2.tsv.gz "
                    +"data/allc_P0_HT_1.tsv.gz data/allc_P0_HT_2.tsv.gz "
                    +"--output-file results/allc_merged.tsv.gz "),
        stdout=f_stdout,
        stderr=f_stderr)
    sys.stdout.write("pass\n")
except:
    sys.stdout.write("failed\n")

# successful
print("\nAll tests are done!")
print(time.asctime(time.localtime(time.time())))
print("The tests took %.2f seconds!" %(time.time() - start_time))
