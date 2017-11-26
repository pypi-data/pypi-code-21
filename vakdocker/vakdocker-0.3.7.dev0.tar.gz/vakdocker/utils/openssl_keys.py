"""
Create certificates and private keys for ssl auth
"""

import os.path
from OpenSSL import crypto

TYPE_RSA = crypto.TYPE_RSA
TYPE_DSA = crypto.TYPE_DSA
FIVE_YEARS = (0, 60*60*24*365*5)

class openssl_keys(object):
    def __init__(self, keysdir):
        '''
            Loads or Generate CA public and private key
        '''
        pvtkey_path = os.path.join(keysdir, 'auth.pem')
        self.certificate_path = os.path.join(keysdir, 'auth.cert')

        if os.path.isfile(pvtkey_path) and \
           os.path.isfile(self.certificate_path):
            self.cakey = crypto.load_privatekey(crypto.FILETYPE_PEM,
                                                file(pvtkey_path).read())
            self.cacert = crypto.load_certificate(crypto.FILETYPE_PEM,
                                             file(self.certificate_path).read())
            self.cacert_dump = crypto.dump_certificate(crypto.FILETYPE_PEM,
                                                       self.cacert)
        else:
            self.cakey = self.__create_key_pair(TYPE_RSA, 1024)
            careq = self.__create_cert_request(self.cakey,
                                               CN='Certificate Authority')
            self.cacert = self.__create_certificate(careq,
                                                    (careq, self.cakey),
                                                    0, FIVE_YEARS)
            self.cacert_dump = crypto.dump_certificate(crypto.FILETYPE_PEM,
                                                       self.cacert)

            open(pvtkey_path, 'w'). \
                    write(crypto.dump_privatekey(crypto.FILETYPE_PEM, self.cakey))
            open(self.certificate_path, 'w').write(self.cacert_dump)

    @staticmethod
    def __create_key_pair(type, bits):
        """
        Create a public/private key pair.
    
        Arguments: type - Key type, must be one of TYPE_RSA and TYPE_DSA
                   bits - Number of bits to use in the key
        Returns:   The public/private key pair in a PKey object
        """
        pkey = crypto.PKey()
        pkey.generate_key(type, bits)
        return pkey
    
    @staticmethod
    def __create_cert_request(pkey, digest="sha256", **name):
        """
        Create a certificate request.
    
        Arguments: pkey   - The key to associate with the request
                   digest - Digestion method to use for signing, default is sha256
                   **name - The name of the subject of the request, possible
                            arguments are:
                              C     - Country name
                              ST    - State or province name
                              L     - Locality name
                              O     - Organization name
                              OU    - Organizational unit name
                              CN    - Common name
                              emailAddress - E-mail address
        Returns:   The certificate request in an X509Req object
        """
        req = crypto.X509Req()
        subj = req.get_subject()
    
        for (key,value) in name.items():
            setattr(subj, key, value)
    
        req.set_pubkey(pkey)
        req.sign(pkey, digest)
        return req
    
    @staticmethod
    def __create_certificate(req, (issuerCert, issuerKey), serial, (notBefore, notAfter), digest="sha256"):
        """
        Generate a certificate given a certificate request.
    
        Arguments: req        - Certificate reqeust to use
                   issuerCert - The certificate of the issuer
                   issuerKey  - The private key of the issuer
                   serial     - Serial number for the certificate
                   notBefore  - Timestamp (relative to now) when the certificate
                                starts being valid
                   notAfter   - Timestamp (relative to now) when the certificate
                                stops being valid
                   digest     - Digest method to use for signing, default is
                                sha256
        Returns:   The signed certificate in an X509 object
        """
        cert = crypto.X509()
        cert.set_serial_number(serial)
        cert.gmtime_adj_notBefore(notBefore)
        cert.gmtime_adj_notAfter(notAfter)
        cert.set_issuer(issuerCert.get_subject())
        cert.set_subject(req.get_subject())
        cert.set_pubkey(req.get_pubkey())
        cert.sign(issuerKey, digest)
        return cert

    def get_authcertificate(self):
        return self.certificate_path
    
    def generate_pair(self, cname, fname):
        pkey = self.__create_key_pair(TYPE_RSA, 1024)
        req = self.__create_cert_request(pkey, CN=cname)
        cert = self.__create_certificate(req, (self.cacert, self.cakey), 1, FIVE_YEARS)

        pkey_dump = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey)
        cert_dump = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

        return (pkey_dump, cert_dump)
