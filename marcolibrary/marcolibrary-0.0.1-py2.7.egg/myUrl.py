import json
import urllib2
#f = urllib2.urlopen('http://www.marcodomenichetti.com')
#print f.read()

def myIpPublic():
    
    try:
        print ('sto caricando Jsonip......')
        f2 = urllib2.urlopen('http://jsonip.com')
        data = json.load(f2)   
        myip = data['ip']
##        print myip
        return myip
    except urllib2.URLError:
        print ('errore...')
    


##myIpPublic()


##print('____myIpPublic___fine')
