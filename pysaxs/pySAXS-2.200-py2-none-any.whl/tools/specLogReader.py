filename="e:/saxs_20170202.log"

class scan:
    def __init__(self,No=0,description=""):
        self.No=No
        self.description=description
        self.x=[]
        self.y=[]
    def addData(self,x,y):
        self.x.append(x)
        self.y.append(y)

def readScanLog(filename):
    '''
    decode SPEC scan log file
    '''
    #open log file
    file=open(filename,'r')
    l=file.readlines()
    file.close()
    #decode
    scanList={}
    newscan=None
    for currentLine in l:
        #print currentLine[:2]
        if currentLine[:2]=="#S":
            
            #scan found
            No=int(currentLine.split()[1])
            titlepos=currentLine.find(currentLine.split()[2])
            #print currentLine[titlepos:-1]
            newscan=scan(No,currentLine[titlepos:-1])
            scanList[No]=newscan
        if currentLine[0]<>"#":
            #add data to current scan
            #decode current data
            spl=currentLine.split()
            if len(spl)>0:
                x=float(spl[0])
                y=float(spl[-1])
                if newscan is not None:
                    newscan.addData(x, y)
                    
    return scanList
            
        