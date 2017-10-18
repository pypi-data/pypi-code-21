from ext_cloud.BaseCloud.BaseImages.BaseImages import BaseImagescls
from ext_cloud.OpenStack.OpenStackImages.OpenStackImage import OpenStackImagecls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackImagescls(OpenStackBaseCloudcls, BaseImagescls):

    def __init__(self, **kwargs):
        super(OpenStackImagescls, self).__init__(credentials=kwargs)

    def list_metrics(self):
        metrics = []
        from ext_cloud.BaseCloud.BaseResources.BaseMetrics import BaseMetricscls
        images = self.list_images()
        arch_dict = {}
        for image in images:
            if image.arch is not None:
                if image.arch in arch_dict:
                    arch_dict[image.arch] += 1
                else:
                    arch_dict[image.arch] = 1

        metrics.append(BaseMetricscls('openstack.images.count', len(self.list_images())))
        for key in arch_dict:
            metrics.append(BaseMetricscls('openstack.images.' + key, arch_dict[key]))

        return metrics

    def list_images_cache(self):
        from dogpile.cache.api import NO_VALUE
        from ext_cloud.utils.dogpile_utils import get_region

        region = get_region()

        images = region.get('images')
        if images is not NO_VALUE:
            return images
        dic = {}
        images = self.list_images()
        for image in images:
            dic[image.id] = image.obj_to_dict()

        region.set('images', dic)
        return dic

    def list_images(self):
        openstack_images = self._Clients.glance.images.list(all_tenants=True)
        images = []
        for openstack_image in openstack_images:
            image = OpenStackImagecls(openstack_image, credentials=self._credentials)
            images.append(image)
        return images

    def create_image_from_instance(self):
        pass
