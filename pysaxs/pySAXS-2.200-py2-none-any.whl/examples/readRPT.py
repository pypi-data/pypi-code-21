'''
example for reading report file
[section1]
option1:1.2
option2:3

'''
import ConfigParser
rpt=ConfigParser.ConfigParser()
testfile="C://winpython//python-2.7.9.amd64//Lib//site-packages//pySAXS//saxsdata//testrpt.txt"
test=rpt.read(testfile)
if len(test)==0:
    print 'error when reading file :', testfile

print rpt.sections()  #print the list of all the sections
expName=rpt.get('experiment','name') #get the option in the specified section
print "Experiment name is : ",expName
print rpt.options('experiment')
print "Average is ",rpt.get('acquisition','average')
print rpt.get('acquisition','exposure time')


    
