from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls
from ext_cloud.BaseCloud.BaseRegions.BaseZone import BaseZonecls


class AWSZonecls(AWSBaseCloudcls, BaseZonecls):

    def __init__(self, *args, **kwargs):
        self._credentials = kwargs['credentials']
        aws_zone = args[0]
        super(AWSZonecls, self).__init__(id=aws_zone.name,
                                         name=aws_zone.name, credentials=kwargs['credentials'])
