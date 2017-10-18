from ext_cloud.Azure.AzureBaseCloud import AzureBaseCloudcls
from ext_cloud.BaseCloud.BaseRegions.BaseRegion import BaseRegioncls


class AzureRegioncls(AzureBaseCloudcls, BaseRegioncls):

    def __init__(self, *args, **kwargs):
        self._credentials = kwargs['credentials']
        azure_location = args[0]
        super(AzureRegioncls, self).__init__(id=azure_location.name,
                                             name=azure_location.name, credentials=kwargs['credentials'])
