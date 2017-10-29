from datetime import datetime
import time
##print  int(datetime.now().strftime("%s%f"))/1000


def getTime13 ():

    aaa = int(datetime.now().strftime("%s%f"))/1000
##    print aaa
    return aaa

def from13ToData(daConvertire):
    import datetime
    
    ccc = datetime.datetime.fromtimestamp(daConvertire/1000).strftime('%H:%M:%S')
    return ccc
    
    
