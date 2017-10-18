from ext_cloud.BaseCloud.BaseVolumes.BaseVolumes import BaseVolumescls
from ext_cloud.AWS.AWSVolumes.AWSVolume import AWSVolumecls
from ext_cloud.AWS.AWSVolumes.AWSSnapshot import AWSSnapshotcls
from boto import ec2
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSVolumescls(AWSBaseCloudcls, BaseVolumescls):

    def __init__(self, **kwargs):
        self.__ec2 = None
        self._credentials['username'] = kwargs['username']
        self._credentials['password'] = kwargs['password']
        self._credentials['region_name'] = kwargs['region_name']

    @property
    def __EC2(self):
        return self.__ec2

    @__EC2.getter
    def __EC2(self):
        if self.__ec2 is None:
            self.__ec2 = ec2.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials['username'], aws_secret_access_key=self._credentials['password'])
        return self.__ec2

    def list_volumes(self):
        aws_volumes = self.__EC2.get_all_volumes()
        volumes = []
        for aws_volume in aws_volumes:
            volume = AWSVolumecls(aws_volume, credentials=self._credentials)
            volumes.append(volume)

        return volumes

    def get_volume_by_id(self, volume_id):
        aws_volume = self.__EC2.get_all_volumes(volume_ids=[volume_id])
        if aws_volume is None:
            return
        volume = AWSVolumecls(aws_volume[0], credentials=self._credentials)
        return volume

    def get_snapshot_by_id(self, snapshot_id):
        aws_snapshot = self.__EC2.get_all_snapshots(snapshot_ids=[snapshot_id])
        if aws_snapshot is None:
            return

        snapshot = AWSSnapshotcls(
            aws_snapshot[0], credentials=self._credentials)
        return snapshot

    def get_volumes_by_tag(self, tag_name, tag_value):
        volume_filters = {'tag-key': tag_name, 'tag-value': tag_value}
        aws_volumes = self.__EC2.get_all_volumes(filters=volume_filters)
        volumes = []
        for aws_volume in aws_volumes:
            volume = AWSVolumecls(aws_volume, credentials=self._credentials)
            volumes.append(volume)

        return volumes

    def create_volume(self, size=2, name=None, zone=None):
        if zone is None:
            aws_zones = self.__EC2.get_all_zones()
            zone = aws_zones[0]
        aws_volume = self.__EC2.create_volume(size, zone)
        volume = AWSVolumecls(aws_volume, credentials=self._credentials)
        if name is not None:
            volume.name = name
        return volume

    def attach_volume(self, volume_id=None, instance_id=None, device_path=None):
        self.__EC2.attach_volume(volume_id, instance_id, device_path)

    def detach_volume(self, volume_id=None, instance_id=None):
        self.__EC2.detach_volume(volume_id, instance_id)

    def list_snapshots(self):
        aws_snapshots = self.__EC2.get_all_snapshots(owner="self")
        snapshots = []
        for aws_snapshot in aws_snapshots:
            snapshot = AWSSnapshotcls(
                aws_snapshot, credentials=self._credentials)
            snapshots.append(snapshot)

        return snapshots

    def delete_volume_by_id(self, volume_id):
        self.__EC2.delete_volume(volume_id=volume_id)

    def create_snapshot(self, volume_id, name=None, description=None):
        aws_snapshot = self.__EC2.create_snapshot(
            volume_id=volume_id, description=description)
        if name is not None:
            aws_snapshot.add_tag('Name', name)
        snapshot = AWSSnapshotcls(aws_snapshot, credentials=self._credentials)
        return snapshot

    def create_volume_from_snapshot(self, snapshot_id, size=2, name=None):
        aws_zones = self.__EC2.get_all_zones()
        aws_volume = self.__EC2.create_volume(
            size, aws_zones[0], snapshot=snapshot_id)
        volume = AWSVolumecls(aws_volume, credentials=self._credentials)
        if name is not None:
            volume.name = name
        return volume

    def get_snapshots_by_tag(self, tag_name, tag_value):
        snapshot_filters = {'tag-key': tag_name, 'tag-value': tag_value}
        aws_snapshots = self.__EC2.get_all_snapshots(filters=snapshot_filters)
        snapshots = []
        for aws_snapshot in aws_snapshots:
            snapshot = AWSSnapshotcls(
                aws_snapshot, credentials=self._credentials)
            snapshots.append(snapshot)
        return snapshots

    def delete_snapshot_by_id(self, snapshot_id):
        self.__EC2.delete_snapshot(snapshot_id=snapshot_id)
