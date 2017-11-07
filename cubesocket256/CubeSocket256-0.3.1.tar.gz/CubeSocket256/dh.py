import random, os
from Crypto.Util import number
import socket

class DiffieHellman:
    def __init__(self, socket=None, psize=1024):
        if socket != None:
            self.sock = socket
        self.prime_size = psize

    def gen_prime(self):
        return number.getPrime(self.prime_size, os.urandom)

    def gen_server(self):
        g = self.gen_prime()
        p = self.gen_prime()
        secret = self.gen_prime()
        return g, p, secret

    def srv_exchange(self, client):
        g, p, secret = self.gen_server()
        client.send(str(g)+":"+str(p))
        step = pow(g, secret, p)
        client.send(str(step))
        step2 = int(client.recv(2048))
        key = number.long_to_bytes(pow(step2, secret, p))
        return key

    def cli_exchange(self):
        secret = self.gen_prime()
        gp = self.sock.recv(2048)
        g = int(gp.split(":")[0])
        p = int(gp.split(":")[1])
        step = pow(g, secret, p)
        step2 = int(self.sock.recv(2048))
        self.sock.send(str(step))
        key = number.long_to_bytes(pow(step2, secret, p))
        return key

    def client(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.key = self.cli_exchange()

    def server(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(5)
        while True:
            client, addr = self.sock.accept()
            self.key = self.srv_exchange(client)

    def wrapsocket(self, socket):
        self.sock = socket
