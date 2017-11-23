import json

from .des_encryption_algorithm import des, PAD_PKCS5
from base64 import urlsafe_b64decode, urlsafe_b64encode


def encode_data(parameters, key):
    """
        Encodes given parameters using the DES algorithm.
        Requires an key with length 8 which it uses as a salt.
        
        Args:
            parameters (dict): The parameters to encode.
            key (string): The key used to encode the URL.
        
        Returns:
            string: The encoded data
    """
    json_parameters = json.dumps(parameters)
    des_encryption  = des(key)
    encrypted_data  = des_encryption.encrypt(json_parameters, padmode=PAD_PKCS5)
    base64_data     = urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    return base64_data


def decode_data(encoded_parameters, key):
    """
        Decodes encoded_parameters using the DES algorithm.
        Requires the `key` used to encode it.
        
        Args:
            encoded_parameters (string): The encoded_parameters to decode.
            key (string): The key used to decode the encoded_parameters.
        
        Returns:
            dict: Returns a dictionary of the decoded data.
    """
    des_encryption = des(key)
    encrypted_data = urlsafe_b64decode(encoded_parameters)
    decrypted_data = des_encryption.decrypt(encrypted_data, padmode=PAD_PKCS5).decode('utf-8')
    parsed_data    = json.loads(decrypted_data)
    
    return parsed_data
