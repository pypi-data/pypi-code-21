import boto3
class KMSEncrypter(object):
    def __init__(self,aws_kms_id):
        self.aws_kms_id = aws_kms_id
        boto3.set_stream_logger(name='botocore')
        self.kms = boto3.client('kms')

    def encrypt(self,text):
        return self.kms.encrypt(
            KeyId=self.aws_kms_id,
            Plaintext=text
        )['CiphertextBlob']

    def decrypt(self,encrypted_text):
        return self.kms.decrypt(
            CiphertextBlob=encrypted_text
        )['Plaintext'].decode('utf-8')
