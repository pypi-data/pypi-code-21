import logging
import os.path

logger = logging.getLogger(__name__)

class Broker(object):
    """Generic broker interface"""
    def __init__(self, brokerConfig):
        self.brokerName = brokerConfig['name']
        self.brokerType = brokerConfig['type']
        self.protocol = brokerConfig['protocol']
        self.host = brokerConfig['address']
        self.port = brokerConfig['port']
        self.caCertsFile = brokerConfig['ca_certs']
        self.keyFile = brokerConfig['key_file']
        self.certFile = brokerConfig['cert_file']
        self.brokerConfig = brokerConfig
        
        for path in [self.caCertsFile, self.keyFile, self.certFile]:
            if os.path.isfile(path):
                logger.debug("File exists {}".format(path))
            else:
                logger.error("File path {} does not exist".format(path))
                raise IOError("File {} does not exist".format(path))
        
    def subscribe(self):
        raise NotImplementedError("Abstract base class: does not implement subscribe")
    
    def unsubscribe(self):
        raise NotImplementedError("Abstract base class: does not implement unsubscribe")
    
    def publish(self):
        raise NotImplementedError("Abstract base class: does not implement publish")
    
    def publishOneShot(self):
        raise NotImplementedError("Abstract base class: does not implement publishOneShot")