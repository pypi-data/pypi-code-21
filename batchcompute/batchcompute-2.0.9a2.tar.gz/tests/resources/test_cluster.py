import unittest

from batchcompute.resources.cluster import *

class ClusterDescriptionTest(unittest.TestCase):

    def setUp(self):
        self.resource_type = "OnDemand"
        self.instance_type = "ecs.t1.small"
        self.description = "cluster created by batchcompute"
        self.cluster_name = "batchcompute cluster"
        self.image_id = "img-xxxx"

    def get_group_description(self):
        group = GroupDescription()

        group.DesiredVMCount = 1
        group.InstanceType = self.instance_type 
        group.ResourceType = self.resource_type 

        self.assertEqual(group.DesiredVMCount, 1)
        self.assertEqual(group.InstanceType, self.instance_type)
        self.assertEqual(group.ResourceType, self.resource_type)

        return group

    def get_cluster_description(self):
        cluster_desc = ClusterDescription()

        cluster_desc.Description = self.description
        cluster_desc.ImageId = self.image_id 
        cluster_desc.Name = self.cluster_name

        self.assertEqual(cluster_desc.Name, self.cluster_name) 
        self.assertEqual(cluster_desc.Description, self.description) 

        group1 = self.get_group_description()
        group2 = self.get_group_description()
        group3 = self.get_group_description()

        cluster_desc.add_group('group1', group1)
        cluster_desc.add_group('group2', group2)
        cluster_desc.add_group('group3', group3)

        self.assertEqual(cluster_desc.get_group('group1').dump(), group1.dump())
        self.assertEqual(cluster_desc.get_group('group2').dump(), group2.dump())
        self.assertEqual(cluster_desc.get_group('group3').dump(), group3.dump())

        cluster_desc.delete_group('group1')
        cluster_desc.delete_group('group2')
        cluster_desc.delete_group('group3')

        self.assertRaises(KeyError, cluster_desc.get_group, 'group1')

        cluster_desc.add_group('group1', group1)
        cluster_desc.add_group('group2', group2)
        cluster_desc.add_group('group3', group3)

        configs = Configs()
        configs.add_system_disk(size=1000, type='cloud')
        configs.add_data_disk(size=1000, type='cloud', mount_point='/path/to/mount')

        self.assertTrue(hasattr(configs.Disks.System, 'Type'))
        self.assertTrue(hasattr(configs.Disks.System, 'Size'))
        self.assertTrue(hasattr(configs.Disks.Data, 'Type'))
        self.assertTrue(hasattr(configs.Disks.Data, 'Size'))
        self.assertTrue(hasattr(configs.Disks.Data, 'MountPoint'))

        cluster_desc.Configs = configs
        self.assertTrue(hasattr(cluster_desc, 'Configs'))

        return cluster_desc

    def testGroup(self):
        self.get_group_description()

    def testClusterDescription(self):
        self.get_cluster_description()


if __name__ == '__main__':
    unittest.main()
