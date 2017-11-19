import subprocess
import shutil
import os

def handler(tmpMutantName, mutant, sourceFile, uniqueMutants):
    if len(uniqueMutants) == 0:
        shutil.copy(tmpMutantName,tmpMutantName+".backup")
        shutil.copy(sourceFile,tmpMutantName)
        with open(".um.mutant_output",'w') as file:    
            r = subprocess.call(["javac",tmpMutantName],stdout=file,stderr=file)
        with open(tmpMutantName.replace(".swift",""),'rb') as file:
            uniqueMutants[file.read()] = 1
    try:
        shutil.copy(sourceFile,".um.backup."+sourceFile)
        classFile = sourceFile.replace(".java",".class")
        if os.path.exists(classFile):
            shutil.copy(classFile,".um.backup."+classFile)        
        shutil.copy(tmpMutantName,sourceFile)                
        with open(".um.mutant_output",'w') as file:    
            r = subprocess.call(["javac",sourceFile],stdout=file,stderr=file)
    finally:
        shutil.copy(".um.backup."+sourceFile,sourceFile)
        if os.path.exists(".um.backup."+classFile):
            shutil.copy(".um.backup."+classFile,classFile)                
    if r == 0:
        with open(classFile,'rb') as file:
            code = file.read()
        if code in uniqueMutants:
            uniqueMutants[code] += 1
            return "REDUNDANT"
        else:
            uniqueMutants[code] = 1
            return "VALID"
    else:
        return "INVALID"
