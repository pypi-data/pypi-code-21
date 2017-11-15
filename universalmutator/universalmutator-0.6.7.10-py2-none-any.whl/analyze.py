import subprocess
import sys
import glob
import shutil
import os

def main():

    src = sys.argv[1]
    tstCmd = sys.argv[2]

    srcEnd = src.split(".")[-1]


    with open("killed.txt",'w') as killed:
        with open ("notkilled.txt",'w') as notkilled:
        for f in glob.glob(src.replace(srcEnd,"mutant.*." + srcEnd)):
            try:
                shutil.copy(src,".backup."+src)
                shutil.copy(f,src)
                with open(os.devnull,'w') as dnull:
                    r = subprocess(tstCmd,shell=True,stderr=dnull,stdout=dnull)
                if r == 0:
                    notkilled.write(f+"\n")
                else:
                    killed.write(f+"\n")
            finally:
                shutil.copy(".backup."+src,src)

if __name__ == '__main__':
    main()        
                       
