from pycube256 import CubeHMAC, Cube, CubeRandom, CubeBlock
from dh import DiffieHellman
import socket
from hashlib import sha256

# v0.3

class CubeSocket:
    def __init__(self, key=None, protocol="TCP", dc=0, algorithm="Cube", dhsize=1024):
        algorithms = ['Cube','CubeHMAC', 'CubeBlock']
        if algorithm not in algorithms:
            raise ValueError('Error: Algorithm not supported.')
        self.key = key
        self.session_key = key
        self.key_length = 16
        self.nonce_length = 8
        self.direct_connect = dc
        self.algorithm = algorithm
        self.dhsize = dhsize
        if protocol == "TCP":
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif protocol == "UDP":
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def wrap(self, sock):
        self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def close(self):
        self.sock.close()

    def listen(self, num_listeners):
        self.sock.listen(num_listeners)

    def bind(self, host, port):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))

    def cli_keyexchange(self, sock):
        session_key = DiffieHellman(sock, self.dhsize).cli_exchange()
        hashed_key = sha256(session_key).digest()
        session_key = hashed_key[:self.key_length]
        return session_key

    def srv_keyexchange(self, client_sock):
        session_key = DiffieHellman(psize=self.dhsize).srv_exchange(client_sock)
        hashed_key = sha256(session_key).digest()
        session_key = hashed_key[:self.key_length]
        return session_key

    def accept(self):
        client, addr = self.sock.accept()
        if self.direct_connect == 0:
            self.session_key = self.srv_keyexchange(client)
        return client, addr

    def gen_key(self, length):
        key = CubeRandom().random(length)
        return key

    def cubeconnect(self, host, port):
        self.connect(host, port)
        self.session_key = self.cli_keyexchange(self.sock)

    def send(self, buf):
        if self.algorithm == "Cube":
            nonce = CubeRandom().random(self.nonce_length)
            buf = Cube(self.session_key, nonce).encrypt(buf)
            self.sock.send(nonce+buf)
        elif self.algorithm == "CubeBlock":
            nonce = CubeRandom().random(self.nonce_length)
            buf = CubeBlock(self.session_key, nonce).encrypt(buf)
            self.sock.send(nonce+buf)
        elif self.algorithm == "CubeHMAC":
            buf = CubeHMAC().encrypt(buf, self.session_key)
            self.sock.send(buf)

    def recv(self, buf_size):
        buf = self.sock.recv(self.nonce_length+buf_size)
        if self.algorithm == "Cube":
            nonce = buf[:self.nonce_length]
            payload = buf[self.nonce_length:]
            content = Cube(self.session_key, nonce).decrypt(payload)
        elif self.algorithm == "CubeBlock":
            nonce = buf[:self.nonce_length]
            payload = buf[self.nonce_length:]
            content = CubeBlock(self.session_key, nonce).decrypt(payload)
        elif self.algorithm == "CubeHMAC":
            content = CubeHMAC().decrypt(buf, self.session_key)
        return content

    def sendto(self, buf, ip, port):
        if self.algorithm == "Cube":
            nonce = self.gen_key(self.nonce_length)
            buf = Cube(self.session_key, nonce).encrypt(buf)
            self.sock.sendto(nonce+buf, (ip, port))
        elif self.algorithm == "CubeBlock":
            nonce = self.gen_key(self.nonce_length)
            buf = CubeBlock(self.session_key, nonce).encrypt(buf)
            self.sock.sendto(nonce+buf, (ip, port))
        elif self.algorithm == "CubeHMAC":
            buf = CubeHMAC().encrypt(buf, self.session_key)
            self.sock.sendto(buf, (ip, port))

    def recvfrom(self, buf_size):
        buf, addr = self.sock.recvfrom(buf_size)
        if self.algorithm == "Cube":
            nonce = buf[0:self.nonce_length]
            data = buf[self.nonce_length:]
            data = Cube(self.session_key, nonce).decrypt(data)
        elif self.algorithm == "CubeBlock":
            nonce = buf[0:self.nonce_length]
            data = buf[self.nonce_length:]
            data = CubeBlock(self.session_key, nonce).decrypt(data)
        elif self.algorithm == "CubeHMAC":
            data = CubeHMAC().decrypt(buf, self.session_key)
        return data

class CubeWrap:
    def __init__(self, sock, key, protocol="TCP", dc=0):
        self.cubesock = CubeSocket(key, protocol, dc)
        self.cubesock.wrap(sock)
        self.raw_sock = sock
