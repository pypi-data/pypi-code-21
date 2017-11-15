#!/usr/bin/python

import os
import sys


####################################################

### check the output of os.system ###

def check_sys (out):
    if (out>0):
        sys.exit(0)

### check if valgrind got any errors ###

def check_valgrind ():
    if "ERROR SUMMARY: 0 errors from 0" in open("valgrind_output.dat").read():
        print "\n valgrind: OK! \n"
        os.remove("valgrind_output.dat")
    else:
        print "\n Error from vagrind! \n"
        print "".join(file("valgrind_output.dat"))
        os.remove("valgrind_output.dat")
        sys.exit(0)

        
### run the example code (with or withoud valgrind) ###

flags_Valgrind = "" #"--leak-check=full"

def com (ex, language):
    if not ("valgrind" in sys.argv):
        if (language=="C++"):
            out = os.system("./"+ex)
            check_sys(out)
        elif (language=="python"):
            out = os.system("python "+ex)
            check_sys(out)
        else:
            print "\n Error: language not allowed! \n"
            sys.exit(0)
    else:
        if (language=="C++"):
            out = os.system("valgrind "+flags_Valgrind+" --log-file=\"valgrind_output.dat\" ./"+ex)
            check_sys(out)
            check_valgrind()
        elif (language=="python"):
            out = os.system("python "+ex)
            check_sys(out)
        else:
            print "\n Error: language not allowed! \n"
            sys.exit(0)

        
### check if the example is ok ###

def check (dir, file, language):
    if ("all" in sys.argv or file in sys.argv or ("python" in sys.argv and language=="python") or ("C++" in sys.argv and language=="C++")):
        print "\n\n-----> Testing ", file, "<-----\n"
        os.chdir(cwd+"/Examples/"+dir)
        com(file, language)

        
####################################################


os.system("clear")
cwd = os.getcwd()


### compile the CBL ###

if not ("nocompile" in sys.argv):
    out = os.system("make clean && make FLAGS=\"-O0 -g\" && make CAMB && make allExamples FLAGS=\"-O0 -g\"")
    check_sys(out)
    

####################################################


### check the C++ examples -> check(directory, example_executable, language) ###

check("vectors", "vectors", "C++") 

check("randomNumbers", "randomNumbers", "C++") 

check("wrappers", "integration_gsl", "C++") 
#check("wrappers", "integration_cuba", "C++") # seg fault with valgrind!!!
check("wrappers", "minimisation", "C++") 

check("distances", "distances", "C++") 

check("covsample", "covsample", "C++") 

check("cosmology", "cosmology", "C++") 
check("cosmology", "fsigma8", "C++") 
check("cosmology", "model_cosmology", "C++") 

check("statistics/codes", "prior", "C++") 
check("statistics/codes", "fit", "C++") 
check("statistics/codes", "sampler", "C++")

check("catalogue", "catalogue", "C++") 

check("clustering/codes", "2pt_monopole", "C++") 
check("clustering/codes", "2pt_monopole_errors", "C++") 
check("clustering/codes", "2pt_2D", "C++")
check("clustering/codes", "2pt_projected", "C++")
check("clustering/codes", "2pt_angular", "C++")
check("clustering/codes", "3pt", "C++")

check("clustering/codes", "model_2pt_monopole_BAO", "C++")
check("clustering/codes", "model_2pt_monopole_RSD", "C++")
check("clustering/codes", "model_2pt_projected", "C++") 
check("clustering/codes", "model_2pt_2D", "C++") 
check("clustering/codes", "model_3pt", "C++") 

check("cosmicVoids/codes", "sizeFunction", "C++") 
check("cosmicVoids/codes", "cleanVoidCatalogue", "C++") 

check("readParameterFile", "readParameterFile", "C++") 


####################################################


### compile the CBL in python ###

if not ("nopy" in sys.argv):
    os.chdir(cwd)
    out = os.system("make clean && make purgepy && make FLAGS=\"-O0 -g\" && make CAMB && make python")
    check_sys(out)
    
if not ("nopy2" in sys.argv):
    os.chdir(cwd)
    out = os.system("make clean && make purgepy && make FLAGS=\"-O0 -g\" && make CAMB && make python2")
    check_sys(out)
    
    
####################################################


### check the python examples -> check(directory, example_executable, language) ###

check("wrappers", "fft_fftlog.py", "python")

check("distances", "distances.py", "python") 

check("statistics/codes", "prior.py", "python")

check("catalogue", "catalogue.py", "python")

check("clustering/codes", "2pt_monopole.py", "python") 
check("clustering/codes", "2pt_model.py", "python") 
check("clustering/codes", "3pt_model.py", "python")

check("cosmicVoids/codes", "sizeFunction.py", "python") 
check("cosmicVoids/pipeline", "cleanVoidCatalogue.py", "python") 


####################################################


### create the documentation ###

if not ("nodoc" in sys.argv):
    os.chdir(cwd)
    out = os.system("make doc")
    check_sys(out)
    print "".join(file("Doc/WARNING_LOGFILE"))
