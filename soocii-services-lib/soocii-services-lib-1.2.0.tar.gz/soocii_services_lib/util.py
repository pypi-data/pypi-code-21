import urllib.request
from time import sleep


def wait_for_internet_connection(host, port):
    """Wait for target until target is able to be connected"""
    target = host + ':' + str(port)
    print("Wait for {} ready".format(target))
    count = 0
    while True:
        try:
            urllib.request.urlopen('http://' + target, timeout=1)
            return target
        except Exception as e:
            dots = ''
            for i in range(3):
                dots += '.' if i <= count % 3 else ' '
            print("Still waiting for {} {}".format(target, dots), end='\r')
            count += 1
            if type(e) is urllib.request.HTTPError:
                return target
            sleep(1)
            pass
