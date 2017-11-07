import socks
import time

s = socks.socksocket()

s.set_proxy(socks.SOCKS5, "localhost", 1080)
s.connect(("example.com", 80))
time.sleep(0.04)
s.send(b'GET / HTTP/1.0\r\n\Host: example.com\r\n\r\n')
print(s.recv(2014))
s.close()