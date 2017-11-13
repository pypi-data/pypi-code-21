import collections
SUPPORTED_CLOUD_TYPES = {"amazon", "openstack", "azure"}


def get_ext_cloud(cloud_type, **kwargs):

    kwargs = collections.defaultdict(lambda: None, kwargs)
    if cloud_type.lower() not in SUPPORTED_CLOUD_TYPES:
        msg = "cloud type:" + cloud_type + " not supported"
        raise Exception(msg)

    if cloud_type.lower() == "openstack":

        from ext_cloud.OpenStack.OpenStack import OpenStackcls
        cloud_obj = OpenStackcls(**kwargs)

        return cloud_obj

    if cloud_type.lower() == "amazon":

        from ext_cloud.AWS.AWS import AWScls
        cloud_obj = AWScls(**kwargs)
        return cloud_obj

    if cloud_type.lower() == "azure":
        from ext_cloud.Azure.Azure import Azurecls
        cloud_obj = Azurecls(**kwargs)

        return cloud_obj
