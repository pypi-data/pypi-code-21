from __future__ import unicode_literals

from keyczar.keyczar import Crypter


def decrypt_message_with_file(message, key_file_location):
    """
    Given message and key_file_location,
    decrypt the message with Keyczar and return it
    """
    crypter = Crypter.Read(key_file_location)

    return crypter.Decrypt(message)


def encrypt_message_with_file(message, key_file_location):
    """
    Given message and key_file_location,
    encrypt the message with Keyczar and return it
    """
    crypter = Crypter.Read(key_file_location)

    return crypter.Encrypt(message)