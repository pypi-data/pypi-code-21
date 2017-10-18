from ext_cloud.BaseCloud.BaseRegions.BaseRegions import BaseRegionscls
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSRegionscls(AWSBaseCloudcls, BaseRegionscls):

    def __init__(self, **kwargs):
        self._credentials = kwargs['credentials']

    def list_regions(self):
        from ext_cloud.AWS.AWSRegions.AWSRegion import AWSRegioncls
        from boto.ec2 import regions as Regions

        aws_regions = Regions(aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        regions = []
        for aws_region in aws_regions:
            region = AWSRegioncls(aws_region, credentials=self._credentials)
            regions.append(region)

        return regions

    def get_region_by_id(self, instance_id):
        pass

    def get_region_by_name(self, instance_name):
        pass
