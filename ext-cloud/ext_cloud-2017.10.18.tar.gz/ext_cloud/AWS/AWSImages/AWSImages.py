from ext_cloud.BaseCloud.BaseImages.BaseImages import BaseImagescls
from ext_cloud.AWS.AWSImages.AWSImage import AWSImagecls
from boto import ec2
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSImagescls(AWSBaseCloudcls, BaseImagescls):

    def __init__(self, **kwargs):
        self._ec2 = None
        self._credentials['username'] = kwargs['username']
        self._credentials['password'] = kwargs['password']
        self._credentials['region_name'] = kwargs['region_name']

    @property
    def _EC2(self):
        return self._ec2

    @_EC2.getter
    def _EC2(self):
        if self._ec2 is None:
            self._ec2 = ec2.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials[
                                              'username'], aws_secret_access_key=self._credentials['password'])
        return self._ec2

    def list_images(self):
        aws_images = self._EC2.get_all_images(owners="self")
        images = self.get_standard_images()
        for aws_image in aws_images:
            image = AWSImagecls(aws_image, credentials=self._credentials)
            images.append(image)
        return images

    def get_standard_images(self):
        from ext_cloud.AWS.AWSImages.AWSImageDict import AWS_IMAGES

        aws_images = self._EC2.get_all_images(image_ids=AWS_IMAGES)
        images = []
        for aws_image in aws_images:
            image = AWSImagecls(aws_image, credentials=self._credentials)
            images.append(image)
        return images

    def get_image_by_id(self, image_id):
        image_list = []
        image_list.append(image_id)
        aws_images = self._EC2.get_all_images(image_ids=image_list)
        for aws_image in aws_images:
            image = AWSImagecls(aws_image, credentials=self._credentials)
            return image
        return None

    def create_image_from_instance(self, instance_id, name=None):
        aws_image = self._EC2.create_image(instance_id=instance_id, name=name)
        return aws_image
