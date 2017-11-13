from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls
from ext_cloud.BaseCloud.BaseRegions.BaseRegion import BaseRegioncls


class AWSRegioncls(AWSBaseCloudcls, BaseRegioncls):

    def __init__(self, *args, **kwargs):
        self._credentials = kwargs['credentials']
        aws_region = args[0]
        super(AWSRegioncls, self).__init__(id=aws_region.name,
                                           name=aws_region.name, credentials=kwargs['credentials'])

    def list_zones(self):
        from boto.ec2 import connect_to_region

        conn = connect_to_region(self.name, aws_access_key_id=self._credentials[
                                 'username'], aws_secret_access_key=self._credentials['password'])
        aws_zones = conn.get_all_zones()
        zones = []
        for aws_zone in aws_zones:
            from ext_cloud.AWS.AWSRegions.AWSZone import AWSZonecls

            zone = AWSZonecls(aws_zone, credentials=self._credentials)
            zones.append(zone)
        return zones
