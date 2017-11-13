from ext_cloud.BaseCloud.BaseCompute.BaseKeypair import BaseKeypaircls
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSKeypaircls(AWSBaseCloudcls, BaseKeypaircls):

    __aws_keypair = None

    def __init__(self, *arg, **kwargs):
        self.__aws_keypair = arg[0]

        super(AWSKeypaircls, self).__init__(id=self.__aws_keypair.fingerprint, name=self.__aws_keypair.name, credentials=kwargs['credentials'])

    @property
    def privatekey(self):
        return self.__aws_keypair.material

    @property
    def publickey(self):
        pass

    @property
    def delete(self):
        self.__aws_keypair.delete()
