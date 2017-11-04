"""This script's goal is to order a set of disordered files. Specified file types will be moved into directories based on modification/creation date."""
import os
import sys
import argparse
from unipath import Path
from datetime import datetime

def getOrderType():
    user_OT = input("Select the order type:\n\"m\" for modification date - \"c\" for creation date: ")
    user_OT = user_OT.lower()
    inputFinished = False
    while not inputFinished:
        if user_OT in ["c", "m"]:
            if user_OT in ["c"]:
                return "c"
                break
            elif user_OT in ["m"]:
                return "m"
                break
            else:
                print("Unknown error.")
                break
        else:
            print("Invalid order type.")
            os.system("pause")
            quit()
            break


def getExtPath():
    user_path = input("Enter the absolute path to the extensions.txt: ")
    inputFinished = False
    while not inputFinished:
        if os.path.exists(user_path) and user_path[-4:] == ".txt":
            chosenPath = Path(user_path)
            #print(str(chosenPath))
            return chosenPath
            break
        else:
            print("Couldn't find the extensions.txt at: "+str(user_path))
            os.system("pause")
            quit()
            break


def getPath():
    user_path = input("Enter the directory of the disordered files (\"%PATH%\") or choose the parent directory of the script (\"P(arent)\"): ")
    user_path = user_path.lower()
    inputFinished = False
    while not inputFinished:
        if user_path in ["p", "parent"]:
            chosenPath = Path.cwd()
            #print(str(chosenPath))
            return chosenPath
            break
        elif user_path not in ["p", "parent"]:
            if os.path.exists(user_path):
                chosenPath = Path(user_path)
                #print(str(chosenPath))
                return chosenPath
                break
            else:
                print("Couldn't find the specified directory: "+str(user_path))
                os.system("pause")
                quit()
                break
        else:
            print("Unknown error.")
            break

def gatherFromArgClineCall(callMode):
    argPath = Path(args.directory)
    argOrderType = args.orderType
    argExtPath = Path(args.fileExtList)
    extensionList = readExtFromFile(argExtPath)
    order(argPath, argOrderType, extensionList, callMode)


def gatherFromEmptyClineCall(callMode):
    clinePath = getPath()
    clineOrderType = getOrderType()
    clineExtPath = getExtPath()
    extensionList = readExtFromFile(clineExtPath)
    order(clinePath, clineOrderType, extensionList, callMode)


def readExtFromFile(extPath):
    extList = []
    with open(str(extPath), mode='r') as r:
        for line in r:
            if line.startswith("#") or line.startswith(" "):
                pass
            else:
                extList.append(line[:-1])
    return extList


def order(userPath, orderType, fileTypes, callMode = -2):
    #print(callMode, workPath, orderType, fileTypes, sep='\n')
    #os.system("pause")
    """Takes the path from getPath() or call and iterates over all files with specified extensions and stores the timestamps of their last modification."""
    #workPath = "C:\\Users\\Johannes\\Desktop\\Test\\"
    workPath = Path(userPath)
    fileYM_timestamps = []
    fileY_timestamps = []
    #print(str(workPath))
    directory = os.fsencode(str(workPath))
    print("\nLooking for files:")
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if os.path.isfile(str(Path(workPath, filename))):
            for ext in fileTypes:
                if filename.endswith(ext) or filename.endswith(ext.swapcase()): #or filename.endswith(".xyz") - swapcase for alternate upper and lower case
                    if orderType in ["m", "M"]:
                        timestampYM = datetime.fromtimestamp(int(os.path.getmtime(str(Path(workPath, filename))))).strftime("%Y.%m")
                        timestampY = datetime.fromtimestamp(int(os.path.getmtime(str(Path(workPath, filename))))).strftime("%Y")
                        print(filename)
                        fileYM_timestamps.append(timestampYM)
                        fileY_timestamps.append(timestampY)
                    elif orderType in ["c", "C"]:
                        timestampYM = datetime.fromtimestamp(int(os.path.getctime(str(Path(workPath, filename))))).strftime("%Y.%m")
                        timestampY = datetime.fromtimestamp(int(os.path.getctime(str(Path(workPath, filename))))).strftime("%Y")
                        print(filename)
                        fileYM_timestamps.append(timestampYM)
                        fileY_timestamps.append(timestampY)
                    else:
                        break
                        print("Invalid orderType input")
                        os.system("pause")
                    #getmtime (modification time) - getctime (creation time)
                

    if fileYM_timestamps == [] and fileY_timestamps == []:
        print("\nNo data was found!")
        os.system("pause")
    else:
        pathHandle(fileY_timestamps, fileYM_timestamps, workPath, orderType, fileTypes)
        

def pathHandle(fileY_timestamps, fileYM_timestamps, workPath, orderType, fileTypes):
    """Takes the year and year-month timestamps and uniqifies the lists."""
    #initialize empty work lists for timestamps
    workYM_timestamps = []
    workY_timestamps = []

    #uniqifies year timestamps
    workY_timestamps = uniqify(fileY_timestamps)

    #print year timestamps
    print("\nYear directories found:")
    print(workY_timestamps)

    #uniqifies year-month timestamps
    workYM_timestamps = uniqify(fileYM_timestamps)

    #print year-month timestamps
    print("\nYear-Month sub-directories found:")
    print(workYM_timestamps)

    #iterates over year directories that need to be in dir based on found timestamps
    for year in workY_timestamps:
        yearPath = str(Path(workPath, str(year)))
        #print(yearPath)
        if os.path.exists(yearPath):
            pass
        else:
            Path(yearPath).mkdir()
            if os.path.exists(yearPath):
                print("\nCreated missing directory at: "+yearPath)
            else:
                print("\nAn error occured while creating the directory: "+yearPath)

    #iterates over year-month directories that need to be in dir\year\ based on found timestamps
    for yearMonth in workYM_timestamps:
        year = yearMonth[0:4]
        yearMonthPath = str(Path(workPath, str(year), str(yearMonth)))
        #print(yearMonthPath)
        if os.path.exists(yearMonthPath):
            pass
        else:
            Path(yearMonthPath).mkdir()
            if os.path.exists(yearMonthPath):
                print("\nCreated missing sub-directory at: "+yearMonthPath)
            else:
                print("\nAn error occured while creating the sub-directory: "+yearMonthPath)

    move(workPath, orderType, fileTypes)

def move(workPath, orderType, fileTypes):
    """Takes the current work directory from pathHandle() and iterates over the same files from which the timestamps were extracted and moves them to the newly created directories."""
    print("\nMoving files:")
    hasError = []   #for checking whether there has been an error during the operation
    directory = os.fsencode(str(workPath))
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if os.path.isfile(str(Path(workPath, filename))): # skips all directories 
            for ext in fileTypes:
                if filename.endswith(ext) or filename.endswith(ext.swapcase()):
                    if orderType in ["m", "M"]:
                        dirSuffix = datetime.fromtimestamp(int(os.path.getmtime(str(Path(workPath, filename))))).strftime("%Y\%Y.%m")
                    elif orderType in ["c", "C"]:
                        dirSuffix = datetime.fromtimestamp(int(os.path.getctime(str(Path(workPath, filename))))).strftime("%Y\%Y.%m")
                    movePath = Path(workPath, dirSuffix)
                    if not os.path.exists(str(Path(movePath, filename))):
                        os.rename(str(Path(workPath, filename)), str(Path(movePath, filename)))
                        print("\n"+filename+" --> "+movePath)
                        if os.path.exists(str(Path(movePath, filename))):
                            print("\nSuccessfully moved "+filename)
                            hasError.append("0")
                        else:
                            print("\nAn error occured while moving "+filename)
                            hasError.append("1")
                    else:
                        print("\nFile "+filename+" already exists.")
        else:
            pass
                    

    finish(hasError)

   
def uniqify(inputList):
    """Uniqifies an inputList and returns outputList"""
    outputList = []
    for item in inputList:
        if not item in outputList:
            outputList.append(item)
    
    return outputList


def finish(errorLog):
    """Takes the error log from move() and finishes the operation by printing whether there have been errors or not."""
    errorCount = errorLog.count("1")
    if "1" in errorLog:
        print("\nOperation finished with "+str(errorCount)+" errors.")
    else:
        print("\nOperation finished successfully.")
    
    os.system("pause")

    #todo: add option to read extensions from text file (normalize entries), think about github publication



# CALL IDENTIFICATION
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, help="the directory that orderPy will order")
    parser.add_argument("-ot", "--orderType", type=str, help="\"m\"/\"c\"specifies whether orderPy will get dates from last modification or creation date")
    parser.add_argument("-fe","--fileExtList", type=str, help="the path to the file extensions file")
    args = parser.parse_args()
    if args.directory != None or args.orderType != None or args.fileExtList != None: #one or more optional args given
        if args.directory != None and args.orderType != None and args.fileExtList != None: #all optional args given - cline with parsed args
            userCM = 0
            #extList = Path(args.fileExtList)
            gatherFromArgClineCall(userCM)
        else: #invalid number of args given
            userCM = -1
            print("Please specify all optional arguments or none. Check the function syntax by running: \"python orderPy.py -h\"\nor visit github.com/johannesber/orderPy for more information.")
            os.system("pause")
    elif args.directory == None and args.orderType == None and args.fileExtList == None: #no optional arg given - interactive
        userCM = 1
        gatherFromEmptyClineCall(userCM)