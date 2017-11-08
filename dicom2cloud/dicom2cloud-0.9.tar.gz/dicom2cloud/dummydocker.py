import time

def startDocker(targetdir):
    print('Running docker dummy:', targetdir)
    timeout = time.time() + 60 * .5
    return ('c1', timeout)

def checkIfDone(timeout):
    timer = time.time()
    print timer
    if timer >= timeout:
        return True
    else:
        return False

def getStatus():
    return 1

def finalizeJob():
    return 1

if __name__ == '__main__':
    (c, timeout) = startDocker('test')
    print c
    while(not checkIfDone(timeout)):
        print "running"
    print "finished"