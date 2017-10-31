
import os
import boto3
import base64

class KMSController():

    def __init__(self, region=None, key_id=None):
        if region is None:
            region = os.environ.get('AWS_DEFAULT_REGION')
        self.region = region
        self.key_id = key_id
        self.kms = boto3.client('kms', region_name=self.region)

    def encrypt(self, str):
        response = self.kms.encrypt(
            KeyId=self.key_id,
            Plaintext=str
        )
        encrypted = response['CiphertextBlob']
        encrypted_str = base64.b64encode(encrypted)
        return encrypted_str

    def decrypt(self, str):
        response = self.kms.decrypt(
            CiphertextBlob=base64.b64decode(str)
        )
        decrypted_str = response['Plaintext']
        return decrypted_str

    def find(self):
        if self.key_id is None: return None
        response = self.kms.list_keys()
        for key in response['Keys']:
            if key['KeyId'] == self.key_id:
                return key['KeyArn']
        return None
