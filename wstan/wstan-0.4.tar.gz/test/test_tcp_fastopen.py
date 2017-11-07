import socket
from ctypes import *

BUFFER_SIZE = 1024
MSG_FASTOPEN = 0x20000000
TCP_FASTOPEN = 23
tfo = True


# ConnectEx function doc:
# https://msdn.microsoft.com/en-us/library/windows/desktop/ms737606(v=vs.85).aspx

host = 'krrr.work'
port = 80
message = b"GET / HTTP/1.0\n\n"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if tfo:
    s.sendto(message, MSG_FASTOPEN, (host, port))
else:
    s.connect((host, port))
    s.send(message)

sock_file = s.makefile('r', 0)
for i in sock_file.readlines():
    print(i)

s.close()