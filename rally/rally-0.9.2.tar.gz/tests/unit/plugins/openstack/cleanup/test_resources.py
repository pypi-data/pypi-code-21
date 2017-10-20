# Copyright 2014: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy

from boto import exception as boto_exception
import ddt
import mock
from neutronclient.common import exceptions as neutron_exceptions
from novaclient import exceptions as nova_exc
from watcherclient.common.apiclient import exceptions as watcher_exceptions

from rally import consts
from rally.plugins.openstack.cleanup import resources
from tests.unit import test

BASE = "rally.plugins.openstack.cleanup.resources"


class SynchronizedDeletionTestCase(test.TestCase):

    def test_is_deleted(self):
        self.assertTrue(resources.SynchronizedDeletion().is_deleted())


class QuotaMixinTestCase(test.TestCase):

    @mock.patch("%s.identity.Identity" % BASE)
    def test_list(self, mock_identity):
        quota = resources.QuotaMixin()
        quota.tenant_uuid = None
        quota.user = mock.MagicMock()
        self.assertEqual([], quota.list())
        self.assertFalse(mock_identity.called)

        quota.tenant_uuid = mock.MagicMock()
        self.assertEqual([mock_identity.return_value.get_project.return_value],
                         quota.list())
        mock_identity.assert_called_once_with(quota.user)


class MagnumMixinTestCase(test.TestCase):

    def test_id(self):
        magnum = resources.MagnumMixin()
        magnum._service = "magnum"
        magnum.raw_resource = mock.MagicMock()
        self.assertEqual(magnum.raw_resource.uuid, magnum.id())

    def test_list(self):
        magnum = resources.MagnumMixin()
        magnum._service = "magnum"
        some_resources = [mock.MagicMock(), mock.MagicMock(),
                          mock.MagicMock(), mock.MagicMock()]
        magnum._manager = mock.MagicMock()
        magnum._manager.return_value.list.side_effect = (
            some_resources[:2], some_resources[2:4], [])
        self.assertEqual(some_resources, magnum.list())
        self.assertEqual(
            [mock.call(marker=None), mock.call(marker=some_resources[1].uuid),
             mock.call(marker=some_resources[3].uuid)],
            magnum._manager.return_value.list.call_args_list)


class NovaServerTestCase(test.TestCase):

    def test_list(self):
        server = resources.NovaServer()
        server._manager = mock.MagicMock()

        server.list()

        server._manager.return_value.list.assert_called_once_with(limit=-1)

    def test_delete(self):
        server = resources.NovaServer()
        server.raw_resource = mock.Mock()
        server._manager = mock.Mock()
        server.delete()

        server._manager.return_value.delete.assert_called_once_with(
            server.raw_resource.id)

    def test_delete_locked(self):
        server = resources.NovaServer()
        server.raw_resource = mock.Mock()
        setattr(server.raw_resource, "OS-EXT-STS:locked", True)
        server._manager = mock.Mock()
        server.delete()

        server.raw_resource.unlock.assert_called_once_with()
        server._manager.return_value.delete.assert_called_once_with(
            server.raw_resource.id)


class NovaFloatingIPsTestCase(test.TestCase):

    def test_name(self):
        fips = resources.NovaFloatingIPs()
        fips.raw_resource = mock.MagicMock()
        self.assertTrue(fips.name())


class NovaFlavorsTestCase(test.TestCase):

    @mock.patch("%s.base.ResourceManager._manager" % BASE)
    def test_is_deleted(self, mock_resource_manager__manager):
        exc = nova_exc.NotFound(404)
        mock_resource_manager__manager().get.side_effect = exc
        flavor = resources.NovaFlavors()
        flavor.raw_resource = mock.MagicMock()
        self.assertEqual(True, flavor.is_deleted())

    @mock.patch("%s.base.ResourceManager._manager" % BASE)
    def test_is_deleted_fail(self, mock_resource_manager__manager):
        mock_resource_manager__manager().get.side_effect = TypeError()
        flavor = resources.NovaFlavors()
        flavor.raw_resource = mock.MagicMock()
        self.assertRaises(TypeError, flavor.is_deleted)


class NovaServerGroupsTestCase(test.TestCase):

    @mock.patch("%s.base.ResourceManager._manager" % BASE)
    @mock.patch("rally.common.utils.name_matches_object")
    def test_list(self, mock_name_matches_object,
                  mock_resource_manager__manager):
        server_groups = [mock.MagicMock(name="rally_foo1"),
                         mock.MagicMock(name="rally_foo2"),
                         mock.MagicMock(name="foo3")]
        mock_name_matches_object.side_effect = [False, True, True]
        mock_resource_manager__manager().list.return_value = server_groups
        self.assertEqual(server_groups, resources.NovaServerGroups().list())


class NovaSecurityGroupTestCase(test.TestCase):

    @mock.patch("%s.base.ResourceManager._manager" % BASE)
    def test_list(self, mock_resource_manager__manager):
        secgroups = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
        secgroups[0].name = "a"
        secgroups[1].name = "b"
        secgroups[2].name = "default"

        mock_resource_manager__manager().list.return_value = secgroups
        self.assertSequenceEqual(secgroups[:2],
                                 resources.NovaSecurityGroup().list())


class NovaFloatingIpsBulkTestCase(test.TestCase):

    def test_id(self):
        ip_range = resources.NovaFloatingIpsBulk()
        ip_range.raw_resource = mock.MagicMock()
        self.assertEqual(ip_range.raw_resource.address, ip_range.id())

    def test_name(self):
        fips = resources.NovaFloatingIpsBulk()
        fips.raw_resource = mock.MagicMock()
        self.assertIsNone(fips.name())


class NovaNetworksTestCase(test.TestCase):

    def test_name(self):
        network = resources.NovaNetworks()
        network.raw_resource = mock.MagicMock()
        self.assertEqual(network.raw_resource.label, network.name())


class EC2MixinTestCase(test.TestCase):

    def get_ec2_mixin(self):
        ec2 = resources.EC2Mixin()
        ec2._service = "ec2"
        return ec2

    def test__manager(self):
        ec2 = self.get_ec2_mixin()
        ec2.user = mock.MagicMock()
        self.assertEqual(ec2.user.ec2.return_value, ec2._manager())


class EC2ServerTestCase(test.TestCase):

    @mock.patch("%s.EC2Server._manager" % BASE)
    def test_is_deleted(self, mock_ec2_server__manager):
        raw_res1 = mock.MagicMock(state="terminated")
        raw_res2 = mock.MagicMock(state="terminated")
        resource = mock.MagicMock(id="test_id")
        manager = resources.EC2Server(resource=resource)

        mock_ec2_server__manager().get_only_instances.return_value = [raw_res1]
        self.assertTrue(manager.is_deleted())

        raw_res1.state = "running"
        self.assertFalse(manager.is_deleted())

        mock_ec2_server__manager().get_only_instances.return_value = [
            raw_res1, raw_res2]
        self.assertFalse(manager.is_deleted())

        raw_res1.state = "terminated"
        self.assertTrue(manager.is_deleted())

        mock_ec2_server__manager().get_only_instances.return_value = []
        self.assertTrue(manager.is_deleted())

    @mock.patch("%s.EC2Server._manager" % BASE)
    def test_is_deleted_exceptions(self, mock_ec2_server__manager):
        mock_ec2_server__manager.side_effect = [
            boto_exception.EC2ResponseError(
                status="fake", reason="fake",
                body={"Error": {"Code": "fake_code"}}),
            boto_exception.EC2ResponseError(
                status="fake", reason="fake",
                body={"Error": {"Code": "InvalidInstanceID.NotFound"}})
        ]
        manager = resources.EC2Server(resource=mock.MagicMock())
        self.assertFalse(manager.is_deleted())
        self.assertTrue(manager.is_deleted())

    @mock.patch("%s.EC2Server._manager" % BASE)
    def test_delete(self, mock_ec2_server__manager):
        resource = mock.MagicMock(id="test_id")
        manager = resources.EC2Server(resource=resource)
        manager.delete()
        mock_ec2_server__manager().terminate_instances.assert_called_once_with(
            instance_ids=["test_id"])

    @mock.patch("%s.EC2Server._manager" % BASE)
    def test_list(self, mock_ec2_server__manager):
        manager = resources.EC2Server()
        mock_ec2_server__manager().get_only_instances.return_value = [
            "a", "b", "c"]
        self.assertEqual(["a", "b", "c"], manager.list())


class NeutronMixinTestCase(test.TestCase):

    def get_neutron_mixin(self):
        neut = resources.NeutronMixin()
        neut._service = "neutron"
        return neut

    def test_manager(self):
        neut = self.get_neutron_mixin()
        neut.user = mock.MagicMock()
        self.assertEqual(neut.user.neutron.return_value, neut._manager())

    @mock.patch("%s.NeutronMixin._manager" % BASE)
    def test_supports_extension(self, mock__manager):
        mock__manager().list_extensions.return_value = {
            "extensions": [{"alias": "foo"}, {"alias": "bar"}]
        }
        neut = self.get_neutron_mixin()
        self.assertTrue(neut.supports_extension("foo"))
        self.assertTrue(neut.supports_extension("bar"))
        self.assertFalse(neut.supports_extension("foobar"))

    def test_id(self):
        neut = self.get_neutron_mixin()
        neut.raw_resource = {"id": "test"}
        self.assertEqual("test", neut.id())

    def test_name(self):
        neutron = self.get_neutron_mixin()
        neutron.raw_resource = {"id": "test_id", "name": "test_name"}
        self.assertEqual("test_name", neutron.name())

    def test_delete(self):
        neut = self.get_neutron_mixin()
        neut.user = mock.MagicMock()
        neut._resource = "some_resource"
        neut.raw_resource = {"id": "42"}

        neut.delete()
        neut.user.neutron().delete_some_resource.assert_called_once_with("42")

    def test_list(self):
        neut = self.get_neutron_mixin()
        neut.user = mock.MagicMock()
        neut._resource = "some_resource"
        neut.tenant_uuid = "user_tenant"

        some_resources = [{"tenant_id": neut.tenant_uuid}, {"tenant_id": "a"}]
        neut.user.neutron().list_some_resources.return_value = {
            "some_resources": some_resources
        }

        self.assertEqual([some_resources[0]], list(neut.list()))

        neut.user.neutron().list_some_resources.assert_called_once_with(
            tenant_id=neut.tenant_uuid)


class NeutronLbaasV1MixinTestCase(test.TestCase):

    def get_neutron_lbaasv1_mixin(self, extensions=None):
        if extensions is None:
            extensions = []
        neut = resources.NeutronLbaasV1Mixin()
        neut._service = "neutron"
        neut._resource = "some_resource"
        neut._manager = mock.Mock()
        neut._manager().list_extensions.return_value = {
            "extensions": [{"alias": ext} for ext in extensions]
        }
        return neut

    def test_list_lbaas_available(self):
        neut = self.get_neutron_lbaasv1_mixin(extensions=["lbaas"])
        neut.tenant_uuid = "user_tenant"

        some_resources = [{"tenant_id": neut.tenant_uuid}, {"tenant_id": "a"}]
        neut._manager().list_some_resources.return_value = {
            "some_resources": some_resources
        }

        self.assertEqual([some_resources[0]], list(neut.list()))
        neut._manager().list_some_resources.assert_called_once_with(
            tenant_id=neut.tenant_uuid)

    def test_list_lbaas_unavailable(self):
        neut = self.get_neutron_lbaasv1_mixin()

        self.assertEqual([], list(neut.list()))
        self.assertFalse(neut._manager().list_some_resources.called)


class NeutronLbaasV2MixinTestCase(test.TestCase):

    def get_neutron_lbaasv2_mixin(self, extensions=None):
        if extensions is None:
            extensions = []
        neut = resources.NeutronLbaasV2Mixin()
        neut._service = "neutron"
        neut._resource = "some_resource"
        neut._manager = mock.Mock()
        neut._manager().list_extensions.return_value = {
            "extensions": [{"alias": ext} for ext in extensions]
        }
        return neut

    def test_list_lbaasv2_available(self):
        neut = self.get_neutron_lbaasv2_mixin(extensions=["lbaasv2"])
        neut.tenant_uuid = "user_tenant"

        some_resources = [{"tenant_id": neut.tenant_uuid}, {"tenant_id": "a"}]
        neut._manager().list_some_resources.return_value = {
            "some_resources": some_resources
        }

        self.assertEqual([some_resources[0]], list(neut.list()))
        neut._manager().list_some_resources.assert_called_once_with(
            tenant_id=neut.tenant_uuid)

    def test_list_lbaasv2_unavailable(self):
        neut = self.get_neutron_lbaasv2_mixin()

        self.assertEqual([], list(neut.list()))
        self.assertFalse(neut._manager().list_some_resources.called)


class NeutronV2LoadbalancerTestCase(test.TestCase):

    def get_neutron_lbaasv2_lb(self):
        neutron_lb = resources.NeutronV2Loadbalancer()
        neutron_lb.raw_resource = {"id": "1", "name": "s_rally"}
        neutron_lb._manager = mock.Mock()
        return neutron_lb

    def test_is_deleted_true(self):
        from neutronclient.common import exceptions as n_exceptions
        neutron_lb = self.get_neutron_lbaasv2_lb()
        neutron_lb._manager().show_loadbalancer.side_effect = (
            n_exceptions.NotFound)

        self.assertTrue(neutron_lb.is_deleted())

        neutron_lb._manager().show_loadbalancer.assert_called_once_with(
            neutron_lb.id())

    def test_is_deleted_false(self):
        from neutronclient.common import exceptions as n_exceptions
        neutron_lb = self.get_neutron_lbaasv2_lb()
        neutron_lb._manager().show_loadbalancer.return_value = (
            neutron_lb.raw_resource)

        self.assertFalse(neutron_lb.is_deleted())
        neutron_lb._manager().show_loadbalancer.assert_called_once_with(
            neutron_lb.id())

        neutron_lb._manager().show_loadbalancer.reset_mock()

        neutron_lb._manager().show_loadbalancer.side_effect = (
            n_exceptions.Forbidden)

        self.assertFalse(neutron_lb.is_deleted())
        neutron_lb._manager().show_loadbalancer.assert_called_once_with(
            neutron_lb.id())


class NeutronFloatingIPTestCase(test.TestCase):

    def test_name(self):
        fips = resources.NeutronFloatingIP({"name": "foo"})
        self.assertIsInstance(fips.name(), resources.base.NoName)

    def test_list(self):
        fips = {"floatingips": [{"tenant_id": "foo", "id": "foo"}]}

        user = mock.MagicMock()
        user.services.return_value = {}
        user.neutron.return_value.list_floatingips.return_value = fips

        self.assertEqual(
            [], resources.NeutronFloatingIP(user=user,
                                            tenant_uuid="foo").list())
        self.assertFalse(user.neutron.return_value.list_floatingips.called)

        user.services.return_value = {
            consts.ServiceType.NETWORK: consts.Service.NEUTRON}
        self.assertEqual(fips["floatingips"], list(
            resources.NeutronFloatingIP(user=user, tenant_uuid="foo").list()))
        user.neutron.return_value.list_floatingips.assert_called_once_with(
            tenant_id="foo")


class NeutronPortTestCase(test.TestCase):

    def test_delete(self):
        raw_res = {"device_owner": "abbabaab", "id": "some_id"}
        user = mock.MagicMock()

        resources.NeutronPort(resource=raw_res, user=user).delete()

        user.neutron().delete_port.assert_called_once_with(raw_res["id"])

    def test_delete_port_raise_exception(self):
        raw_res = {"device_owner": "abbabaab", "id": "some_id"}
        user = mock.MagicMock()
        user.neutron().delete_port.side_effect = (
            neutron_exceptions.PortNotFoundClient)

        resources.NeutronPort(resource=raw_res, user=user).delete()

        user.neutron().delete_port.assert_called_once_with(raw_res["id"])

    def test_delete_port_device_owner(self):
        raw_res = {
            "device_owner": "network:router_interface",
            "id": "some_id",
            "device_id": "dev_id"
        }
        user = mock.MagicMock()

        resources.NeutronPort(resource=raw_res, user=user).delete()

        user.neutron().remove_interface_router.assert_called_once_with(
            raw_res["device_id"], {"port_id": raw_res["id"]})

    def test_name(self):
        raw_res = {
            "id": "some_id",
            "device_id": "dev_id",
        }

        self.assertIsInstance(
            resources.NeutronPort(resource=raw_res,
                                  user=mock.MagicMock()).name(),
            resources.base.NoName)

        raw_res["name"] = "foo"
        self.assertEqual("foo", resources.NeutronPort(
            resource=raw_res, user=mock.MagicMock()).name())

        raw_res["parent_name"] = "bar"
        self.assertEqual("bar", resources.NeutronPort(
            resource=raw_res, user=mock.MagicMock()).name())

        del raw_res["name"]
        self.assertEqual("bar", resources.NeutronPort(
            resource=raw_res, user=mock.MagicMock()).name())

    def test_list(self):

        tenant_uuid = "uuuu-uuuu-iiii-dddd"

        ports = [
            # the case when 'name' is present, so 'device_owner' field is not
            #   required
            {"tenant_id": tenant_uuid, "id": "id1", "name": "foo"},
            # 3 different cases when router_interface is an owner
            {"tenant_id": tenant_uuid, "id": "id2",
             "device_owner": "network:router_interface",
             "device_id": "router-1"},
            {"tenant_id": tenant_uuid, "id": "id3",
             "device_owner": "network:router_interface_distributed",
             "device_id": "router-1"},
            {"tenant_id": tenant_uuid, "id": "id4",
             "device_owner": "network:ha_router_replicated_interface",
             "device_id": "router-2"},
            # the case when gateway router is an owner
            {"tenant_id": tenant_uuid, "id": "id5",
             "device_owner": "network:router_gateway",
             "device_id": "router-3"},
            # the case when gateway router is an owner, but device_id is
            #   invalid
            {"tenant_id": tenant_uuid, "id": "id6",
             "device_owner": "network:router_gateway",
             "device_id": "aaaa"},
            # the case when port was auto-created with floating-ip
            {"tenant_id": tenant_uuid, "id": "id7",
             "device_owner": "network:dhcp",
             "device_id": "asdasdasd"},
            # the case when port is from another tenant
            {"tenant_id": "wrong tenant", "id": "id8", "name": "foo"},
            # WTF port without any parent and name
            {"tenant_id": tenant_uuid, "id": "id9", "device_owner": ""},
        ]

        routers = [
            {"id": "router-1", "name": "Router-1", "tenant_id": tenant_uuid},
            {"id": "router-2", "name": "Router-2", "tenant_id": tenant_uuid},
            {"id": "router-3", "name": "Router-3", "tenant_id": tenant_uuid},
            {"id": "router-4", "name": "Router-4", "tenant_id": tenant_uuid},
            {"id": "router-5", "name": "Router-5", "tenant_id": tenant_uuid},
        ]

        expected_ports = []
        for port in ports:
            if port["tenant_id"] == tenant_uuid:
                expected_ports.append(copy.deepcopy(port))
                if ("device_id" in port and
                        port["device_id"].startswith("router")):
                    expected_ports[-1]["parent_name"] = [
                        r for r in routers
                        if r["id"] == port["device_id"]][0]["name"]

        class FakeNeutronClient(object):

            list_ports = mock.Mock()
            list_routers = mock.Mock()

        neutron = FakeNeutronClient
        neutron.list_ports.return_value = {"ports": ports}
        neutron.list_routers.return_value = {"routers": routers}

        user = mock.Mock(neutron=neutron)
        self.assertEqual(expected_ports, resources.NeutronPort(
            user=user, tenant_uuid=tenant_uuid).list())
        neutron.list_ports.assert_called_once_with()
        neutron.list_routers.assert_called_once_with()


@ddt.ddt
class NeutronSecurityGroupTestCase(test.TestCase):

    @ddt.data(
        {"admin": mock.Mock(), "admin_required": True},
        {"admin": None, "admin_required": False})
    @ddt.unpack
    def test_list(self, admin, admin_required):
        sg_list = [{"tenant_id": "user_tenant", "name": "default"},
                   {"tenant_id": "user_tenant", "name": "foo_sg"}]

        neut = resources.NeutronSecurityGroup()
        neut.user = mock.MagicMock()
        neut._resource = "security_group"
        neut.tenant_uuid = "user_tenant"

        neut.user.neutron().list_security_groups.return_value = {
            "security_groups": sg_list
        }

        expected_result = [sg_list[1]]
        self.assertEqual(expected_result, list(neut.list()))

        neut.user.neutron().list_security_groups.assert_called_once_with(
            tenant_id=neut.tenant_uuid)


class NeutronQuotaTestCase(test.TestCase):

    def test_delete(self):
        admin = mock.MagicMock()
        resources.NeutronQuota(admin=admin, tenant_uuid="fake").delete()
        admin.neutron.return_value.delete_quota.assert_called_once_with("fake")


@ddt.ddt
class GlanceImageTestCase(test.TestCase):

    @mock.patch("rally.plugins.openstack.wrappers.glance.wrap")
    def test__wrapper_admin(self, mock_glance_wrap):
        admin = mock.Mock()
        glance = resources.GlanceImage(admin=admin)
        wrapper = glance._wrapper()

        mock_glance_wrap.assert_called_once_with(admin.glance, glance)
        self.assertEqual(wrapper, mock_glance_wrap.return_value)

    @mock.patch("rally.plugins.openstack.wrappers.glance.wrap")
    def test__wrapper_user(self, mock_glance_wrap):
        user = mock.Mock()
        glance = resources.GlanceImage(user=user)
        wrapper = glance._wrapper()

        mock_glance_wrap.assert_called_once_with(user.glance, glance)
        self.assertEqual(wrapper, mock_glance_wrap.return_value)

    @mock.patch("rally.plugins.openstack.wrappers.glance.wrap")
    def test__wrapper_admin_preferred(self, mock_glance_wrap):
        admin = mock.Mock()
        user = mock.Mock()
        glance = resources.GlanceImage(admin=admin, user=user)
        wrapper = glance._wrapper()

        mock_glance_wrap.assert_called_once_with(admin.glance, glance)
        self.assertEqual(wrapper, mock_glance_wrap.return_value)

    def test_list(self):
        glance = resources.GlanceImage()
        glance._wrapper = mock.Mock()
        glance.tenant_uuid = mock.Mock()

        self.assertEqual(glance.list(),
                         glance._wrapper.return_value.list_images.return_value)
        glance._wrapper.return_value.list_images.assert_called_once_with(
            owner=glance.tenant_uuid)

    def test_delete(self):
        glance = resources.GlanceImage()
        glance._client = mock.Mock()
        glance._wrapper = mock.Mock()
        glance.raw_resource = mock.Mock()

        client = glance._client.return_value
        wrapper = glance._wrapper.return_value

        deleted_image = mock.Mock(status="DELETED")
        wrapper.get_image.side_effect = [glance.raw_resource, deleted_image]

        glance.delete()
        client().images.delete.assert_called_once_with(glance.raw_resource.id)


class CeilometerTestCase(test.TestCase):

    def test_id(self):
        ceil = resources.CeilometerAlarms()
        ceil.raw_resource = mock.MagicMock()
        self.assertEqual(ceil.raw_resource.alarm_id, ceil.id())

    @mock.patch("%s.CeilometerAlarms._manager" % BASE)
    def test_list(self, mock_ceilometer_alarms__manager):

        ceil = resources.CeilometerAlarms()
        ceil.tenant_uuid = mock.MagicMock()
        mock_ceilometer_alarms__manager().list.return_value = ["a", "b", "c"]
        mock_ceilometer_alarms__manager.reset_mock()

        self.assertEqual(["a", "b", "c"], ceil.list())
        mock_ceilometer_alarms__manager().list.assert_called_once_with(
            q=[{"field": "project_id", "op": "eq", "value": ceil.tenant_uuid}])


class ZaqarQueuesTestCase(test.TestCase):

    def test_list(self):
        user = mock.Mock()
        zaqar = resources.ZaqarQueues(user=user)
        zaqar.list()
        user.zaqar().queues.assert_called_once_with()


class KeystoneMixinTestCase(test.TestCase):

    def test_is_deleted(self):
        self.assertTrue(resources.KeystoneMixin().is_deleted())

    def get_keystone_mixin(self):
        kmixin = resources.KeystoneMixin()
        kmixin._service = "keystone"
        return kmixin

    @mock.patch("%s.identity" % BASE)
    def test_manager(self, mock_identity):
        keystone_mixin = self.get_keystone_mixin()
        keystone_mixin.admin = mock.MagicMock()
        self.assertEqual(mock_identity.Identity.return_value,
                         keystone_mixin._manager())
        mock_identity.Identity.assert_called_once_with(
            keystone_mixin.admin)

    @mock.patch("%s.identity" % BASE)
    def test_delete(self, mock_identity):
        keystone_mixin = self.get_keystone_mixin()
        keystone_mixin._resource = "some_resource"
        keystone_mixin.id = lambda: "id_a"
        keystone_mixin.admin = mock.MagicMock()

        keystone_mixin.delete()
        mock_identity.Identity.assert_called_once_with(keystone_mixin.admin)
        identity_service = mock_identity.Identity.return_value
        identity_service.delete_some_resource.assert_called_once_with("id_a")

    @mock.patch("%s.identity" % BASE)
    def test_list(self, mock_identity):
        keystone_mixin = self.get_keystone_mixin()
        keystone_mixin._resource = "some_resource2"
        keystone_mixin.admin = mock.MagicMock()
        identity = mock_identity.Identity

        self.assertSequenceEqual(
            identity.return_value.list_some_resource2s.return_value,
            keystone_mixin.list())
        identity.assert_called_once_with(keystone_mixin.admin)
        identity.return_value.list_some_resource2s.assert_called_once_with()


class KeystoneEc2TestCase(test.TestCase):
    def test_user_id_property(self):
        user_client = mock.Mock()
        admin_client = mock.Mock()

        manager = resources.KeystoneEc2(user=user_client, admin=admin_client)

        self.assertEqual(user_client.keystone.auth_ref.user_id,
                         manager.user_id)

    def test_list(self):
        user_client = mock.Mock()
        admin_client = mock.Mock()

        with mock.patch("%s.identity.Identity" % BASE, autospec=True) as p:
            identity = p.return_value
            manager = resources.KeystoneEc2(user=user_client,
                                            admin=admin_client)
            self.assertEqual(identity.list_ec2credentials.return_value,
                             manager.list())
            p.assert_called_once_with(user_client)
            identity.list_ec2credentials.assert_called_once_with(
                manager.user_id)

    def test_delete(self):
        user_client = mock.Mock()
        admin_client = mock.Mock()
        raw_resource = mock.Mock()

        with mock.patch("%s.identity.Identity" % BASE, autospec=True) as p:
            manager = resources.KeystoneEc2(user=user_client,
                                            admin=admin_client,
                                            resource=raw_resource)
            manager.delete()

            p.assert_called_once_with(user_client)
            p.return_value.delete_ec2credential.assert_called_once_with(
                manager.user_id, access=raw_resource.access)


class SwiftMixinTestCase(test.TestCase):

    def get_swift_mixin(self):
        swift_mixin = resources.SwiftMixin()
        swift_mixin._service = "swift"
        return swift_mixin

    def test_manager(self):
        swift_mixin = self.get_swift_mixin()
        swift_mixin.user = mock.MagicMock()
        self.assertEqual(swift_mixin.user.swift.return_value,
                         swift_mixin._manager())

    def test_id(self):
        swift_mixin = self.get_swift_mixin()
        swift_mixin.raw_resource = mock.MagicMock()
        self.assertEqual(swift_mixin.raw_resource, swift_mixin.id())

    def test_name(self):
        swift = self.get_swift_mixin()
        swift.raw_resource = ["name1", "name2"]
        self.assertEqual("name2", swift.name())

    def test_delete(self):
        swift_mixin = self.get_swift_mixin()
        swift_mixin.user = mock.MagicMock()
        swift_mixin._resource = "some_resource"
        swift_mixin.raw_resource = mock.MagicMock()
        swift_mixin.delete()
        swift_mixin.user.swift().delete_some_resource.assert_called_once_with(
            *swift_mixin.raw_resource)


class SwiftObjectTestCase(test.TestCase):

    @mock.patch("%s.SwiftMixin._manager" % BASE)
    def test_list(self, mock_swift_mixin__manager):
        containers = [mock.MagicMock(), mock.MagicMock()]
        objects = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
        mock_swift_mixin__manager().get_account.return_value = (
            "header", containers)
        mock_swift_mixin__manager().get_container.return_value = (
            "header", objects)
        self.assertEqual(len(containers),
                         len(resources.SwiftContainer().list()))
        self.assertEqual(len(containers) * len(objects),
                         len(resources.SwiftObject().list()))


class SwiftContainerTestCase(test.TestCase):

    @mock.patch("%s.SwiftMixin._manager" % BASE)
    def test_list(self, mock_swift_mixin__manager):
        containers = [mock.MagicMock(), mock.MagicMock(), mock.MagicMock()]
        mock_swift_mixin__manager().get_account.return_value = (
            "header", containers)
        self.assertEqual(len(containers),
                         len(resources.SwiftContainer().list()))


class ManilaShareTestCase(test.TestCase):

    def test_list(self):
        share_resource = resources.ManilaShare()
        share_resource._manager = mock.MagicMock()

        share_resource.list()

        self.assertEqual("shares", share_resource._resource)
        share_resource._manager.return_value.list.assert_called_once_with()

    def test_delete(self):
        share_resource = resources.ManilaShare()
        share_resource._manager = mock.MagicMock()
        share_resource.id = lambda: "fake_id"

        share_resource.delete()

        self.assertEqual("shares", share_resource._resource)
        share_resource._manager.return_value.delete.assert_called_once_with(
            "fake_id")


class ManilaShareNetworkTestCase(test.TestCase):

    def test_list(self):
        sn_resource = resources.ManilaShareNetwork()
        sn_resource._manager = mock.MagicMock()

        sn_resource.list()

        self.assertEqual("share_networks", sn_resource._resource)
        sn_resource._manager.return_value.list.assert_called_once_with()

    def test_delete(self):
        sn_resource = resources.ManilaShareNetwork()
        sn_resource._manager = mock.MagicMock()
        sn_resource.id = lambda: "fake_id"

        sn_resource.delete()

        self.assertEqual("share_networks", sn_resource._resource)
        sn_resource._manager.return_value.delete.assert_called_once_with(
            "fake_id")


class ManilaSecurityServiceTestCase(test.TestCase):

    def test_list(self):
        ss_resource = resources.ManilaSecurityService()
        ss_resource._manager = mock.MagicMock()

        ss_resource.list()

        self.assertEqual("security_services", ss_resource._resource)
        ss_resource._manager.return_value.list.assert_called_once_with()

    def test_delete(self):
        ss_resource = resources.ManilaSecurityService()
        ss_resource._manager = mock.MagicMock()
        ss_resource.id = lambda: "fake_id"

        ss_resource.delete()

        self.assertEqual("security_services", ss_resource._resource)
        ss_resource._manager.return_value.delete.assert_called_once_with(
            "fake_id")


class MistralMixinTestCase(test.TestCase):

    def test_delete(self):
        mistral = resources.MistralMixin()
        mistral._service = "mistral"
        mistral.user = mock.MagicMock()
        mistral._resource = "some_resources"
        mistral.raw_resource = {"id": "TEST_ID"}
        mistral.user.mistral().some_resources.delete.return_value = None

        mistral.delete()
        mistral.user.mistral().some_resources.delete.assert_called_once_with(
            "TEST_ID")


class MistralWorkbookTestCase(test.TestCase):

    def test_delete(self):
        mistral = resources.MistralWorkbooks()
        mistral._service = "mistral"
        mistral.user = mock.MagicMock()
        mistral._resource = "some_resources"
        mistral.raw_resource = {"name": "TEST_NAME"}
        mistral.user.mistral().some_resources.delete.return_value = None

        mistral.delete()
        mistral.user.mistral().some_resources.delete.assert_called_once_with(
            "TEST_NAME")


class FuelEnvironmentTestCase(test.TestCase):

    def test_id(self):
        fres = resources.FuelEnvironment()
        fres.raw_resource = {"id": 42, "name": "chavez"}
        self.assertEqual(42, fres.id())

    def test_name(self):
        fuel = resources.FuelEnvironment()
        fuel.raw_resource = {"id": "test_id", "name": "test_name"}
        self.assertEqual("test_name", fuel.name())

    @mock.patch("%s.FuelEnvironment._manager" % BASE)
    def test_is_deleted(self, mock__manager):
        mock__manager.return_value.get.return_value = None
        fres = resources.FuelEnvironment()
        fres.id = mock.Mock()
        self.assertTrue(fres.is_deleted())
        mock__manager.return_value.get.return_value = "env"
        self.assertFalse(fres.is_deleted())
        mock__manager.return_value.get.assert_called_with(fres.id.return_value)


class SenlinMixinTestCase(test.TestCase):

    def test_id(self):
        senlin = resources.SenlinMixin()
        senlin.raw_resource = {"id": "TEST_ID"}
        self.assertEqual("TEST_ID", senlin.id())

    def test__manager(self):
        senlin = resources.SenlinMixin()
        senlin._service = "senlin"
        senlin.user = mock.MagicMock()
        self.assertEqual(senlin.user.senlin.return_value, senlin._manager())

    def test_list(self):
        senlin = resources.SenlinMixin()
        senlin._service = "senlin"
        senlin.user = mock.MagicMock()
        senlin._resource = "some_resources"

        some_resources = [{"name": "resource1"}, {"name": "resource2"}]
        senlin.user.senlin().some_resources.return_value = some_resources

        self.assertEqual(some_resources, senlin.list())
        senlin.user.senlin().some_resources.assert_called_once_with()

    def test_delete(self):
        senlin = resources.SenlinMixin()
        senlin._service = "senlin"
        senlin.user = mock.MagicMock()
        senlin._resource = "some_resources"
        senlin.raw_resource = {"id": "TEST_ID"}
        senlin.user.senlin().delete_some_resource.return_value = None

        senlin.delete()
        senlin.user.senlin().delete_some_resource.assert_called_once_with(
            "TEST_ID")


class WatcherTemplateTestCase(test.TestCase):

    def test_id(self):
        watcher = resources.WatcherTemplate()
        watcher.raw_resource = mock.MagicMock(uuid=100)
        self.assertEqual(100, watcher.id())

    @mock.patch("%s.WatcherTemplate._manager" % BASE)
    def test_is_deleted(self, mock__manager):
        mock__manager.return_value.get.return_value = None
        watcher = resources.WatcherTemplate()
        watcher.id = mock.Mock()
        self.assertFalse(watcher.is_deleted())
        mock__manager.side_effect = [watcher_exceptions.NotFound()]
        self.assertTrue(watcher.is_deleted())

    def test_list(self):
        watcher = resources.WatcherTemplate()
        watcher._manager = mock.MagicMock()

        watcher.list()

        self.assertEqual("audit_template", watcher._resource)
        watcher._manager().list.assert_called_once_with(limit=0)


class WatcherAuditTestCase(test.TestCase):

    def test_id(self):
        watcher = resources.WatcherAudit()
        watcher.raw_resource = mock.MagicMock(uuid=100)
        self.assertEqual(100, watcher.id())

    def test_name(self):
        watcher = resources.WatcherAudit()
        watcher.raw_resource = mock.MagicMock(uuid="name")
        self.assertEqual("name", watcher.name())

    @mock.patch("%s.WatcherAudit._manager" % BASE)
    def test_is_deleted(self, mock__manager):
        mock__manager.return_value.get.return_value = None
        watcher = resources.WatcherAudit()
        watcher.id = mock.Mock()
        self.assertFalse(watcher.is_deleted())
        mock__manager.side_effect = [watcher_exceptions.NotFound()]
        self.assertTrue(watcher.is_deleted())

    def test_list(self):
        watcher = resources.WatcherAudit()
        watcher._manager = mock.MagicMock()

        watcher.list()

        self.assertEqual("audit", watcher._resource)
        watcher._manager().list.assert_called_once_with(limit=0)


class WatcherActionPlanTestCase(test.TestCase):

    def test_id(self):
        watcher = resources.WatcherActionPlan()
        watcher.raw_resource = mock.MagicMock(uuid=100)
        self.assertEqual(100, watcher.id())

    def test_name(self):
        watcher = resources.WatcherActionPlan()
        watcher.raw_resource = mock.MagicMock(uuid="name")
        self.assertEqual("name", watcher.name())

    @mock.patch("%s.WatcherActionPlan._manager" % BASE)
    def test_is_deleted(self, mock__manager):
        mock__manager.return_value.get.return_value = None
        watcher = resources.WatcherActionPlan()
        watcher.id = mock.Mock()
        self.assertFalse(watcher.is_deleted())
        mock__manager.side_effect = [watcher_exceptions.NotFound()]
        self.assertTrue(watcher.is_deleted())

    def test_list(self):
        watcher = resources.WatcherActionPlan()
        watcher._manager = mock.MagicMock()

        watcher.list()

        self.assertEqual("action_plan", watcher._resource)
        watcher._manager().list.assert_called_once_with(limit=0)
