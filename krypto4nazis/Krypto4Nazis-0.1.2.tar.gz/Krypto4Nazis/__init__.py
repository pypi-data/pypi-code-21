from MorseStation import MorseStation
from pycube import Cube, CubeRandom, CubeKDF, CubeHMAC

class NaziKrypt:
    def __init__(self, key):
        self.key = key

    def encrypt(self, data, nonce=""):
        return Cube(self.key, nonce).encrypt(data)

    def decrypt(self, data, nonce=""):
        return Cube(self.key, nonce).decrypt(data)

class NaziKryptHMAC:

    def encrypt(self, data, key):
        return CubeHMAC().encrypt(data, key)

    def decrypt(self, data, key):
        return CubeHMAC().decrypt(data, key)

class NaziMorse:
    def __init__(self, key, noncelength=8, kdf=True, frequency=1000, wpm=18, timeunit=1.2, volume=1):
        self.frequency = frequency
        self.wpm = wpm
        self.timeunit = timeunit
        self.volume = volume
        if kdf == True:
            self.key = CubeKDF().genkey(key)
        else:
            self.key = key
        self.noncelength = noncelength

    def transmit(self, data, filename, nonce=""):
        if nonce == "":
            nonce = CubeRandom().random(8)
        cipher_text = NaziKrypt(self.key, nonce).encrypt(data)
        MorseStation(self.frequency, self.wpm, self.timeunit, self.volume).transmit(nonce+cipher_text, filename)

class NaziMorseHMAC:
    def __init__(self, key, frequency=1000, wpm=18, timeunit=1.2, volume=1):
        self.key = key
        self.frequency = frequency
        self.wpm = wpm
        self.timeunit = timeunit
        self.volume = volume

    def transmit(self, data, filename, nonce=""):
        cipher_text = NaziKryptHMAC().encrypt(data, self.key)
        MorseStation(self.frequency, self.wpm, self.timeunit, self.volume).transmit(cipher_text, filename)
