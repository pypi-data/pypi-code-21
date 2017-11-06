import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from sepa_netherlands import protocol
from config import merchant_id, return_url, url, fingerprint, password

dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, 'priv.key'), 'rb') as f:
    key = f.read()
with open(os.path.join(dirname, 'cert.pem'), 'rb') as f:
    cert = f.read()
with open(os.path.join(dirname, 'ing.pem'), 'rb') as f:
    verification_cert = f.read()

client = protocol.Client(merchant_id, return_url, url, url, url, key, cert, password, fingerprint, verification_cert)
print(client.request_directory())

class TestSuite(unittest.TestSuite):
    def test(self):
        return

if __name__ == '__main__':
    unittest.main()
