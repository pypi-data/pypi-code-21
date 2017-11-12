import os
import glob

def delete():
    os.chdir('temporary')

    files = glob.glob("*.java")
    for f in files:
        os.remove(f)

    files = glob.glob("*.class")
    for f in files:
        os.remove(f)