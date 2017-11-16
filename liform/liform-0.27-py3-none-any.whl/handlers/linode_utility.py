_linode_client = None
_linode_regions_ni = {}
_linode_regions_in = {}
_linode_domains_ni = {}
_linode_domains_in = {}
_linode_distributions_ni = {}
_linode_distributions_in = {}
_linode_types_ni = {}
_linode_types_in = {}


def _linode_client_init(settings):
    from linode import LinodeClient
    from ..utility import warning_print

    global _linode_client
    global _linode_regions_ni
    global _linode_regions_in
    global _linode_domains_ni
    global _linode_domains_in
    global _linode_distributions_ni
    global _linode_distributions_in
    global _linode_types_ni
    global _linode_types_in

    try:
        if _linode_client is None:
            _linode_client = LinodeClient(settings['provider_linode']['access_token'])

            for region in _linode_client.get_regions():
                _linode_regions_in[region.id] = region.id
                _linode_regions_ni[region.id] = region.id

            for domain in _linode_client.get_domains():
                _linode_domains_in[domain.id] = domain.domain
                _linode_domains_ni[domain.domain] = domain.id

            for distribution in _linode_client.linode.get_distributions():
                _linode_distributions_in[distribution.id] = distribution.label
                _linode_distributions_ni[distribution.label] = distribution.id

            for type in _linode_client.linode.get_types():
                _linode_types_in[type.id] = type.label
                _linode_types_ni[type.label] = type.id
    except Exception as e:
        warning_print('\033[31;1m_linode_client_init()\033[0m')
        raise


def _linode_server_ensure_running(server_resource):
    from linode.errors import ApiError
    from time import sleep
    from ..utility import warning_print

    try:
        while True:
            try:
                if server_resource._linode_object.status == 'running':
                    break

                if server_resource._linode_object.status == 'offline':
                    server_resource._linode_object.boot()
                    sleep(5)

                server_resource._linode_object.invalidate()
                sleep(2)
            except ApiError as e:
                if (e.status == 400) and (e.args[0].startswith('400: Linode busy.')):
                    pass
                else:
                    raise
    except Exception as e:
        warning_print('\033[31;1m_linode_server_ensure_running({0})\033[0m', server_resource.slug)
        raise


def _linode_server_ensure_offline(server_resource):
    from linode.errors import ApiError
    from time import sleep
    from ..utility import warning_print

    try:
        if not server_resource:
            return

        if not server_resource._linode_object:
            return

        while True:
            try:
                if server_resource._linode_object.status == 'offline':
                    break

                if server_resource._linode_object.status == 'running':
                    server_resource._linode_object.shutdown()
                    sleep(5)

                server_resource._linode_object.invalidate()
                sleep(2)
            except ApiError as e:
                if (e.status == 400) and (e.args[0].startswith('400: Linode busy.')):
                    pass
                else:
                    raise
    except Exception as e:
        warning_print('\033[31;1m_linode_server_ensure_offline({0})\033[0m', server_resource.slug)
        raise


def _linode_server_ensure_missing(server_resource):
    from linode.errors import ApiError
    from time import sleep
    from ..utility import warning_print

    try:
        if not server_resource:
            return

        if not server_resource._linode_object:
            return

        while True:
            try:
                server_resource._linode_object.invalidate()

                if server_resource._linode_object.delete():
                    sleep(5)
            except ApiError as e:
                if e.status in (404,):
                    break
                else:
                    raise
    except Exception as e:
        warning_print('\033[31;1m_linode_server_ensure_missing({0})\033[0m', server_resource.slug)
        raise


def _linode_server_select(server_resource):
    from linode import Linode
    from linode.errors import ApiError
    from ..utility import warning_print

    global _linode_client

    try:
        server_resource._linode_object = None

        if not server_resource.id:
            return

        try:
            server_object = Linode(_linode_client, server_resource.id)
            server_object._api_get()
            server_resource._linode_object = server_object
        except ApiError as e:
            if e.status in (404,):
                return
            else:
                raise
    except Exception as e:
        warning_print('\033[31;1m_linode_server_select({0})\033[0m', server_resource.slug)
        raise


def _linode_server_create(server_resource):
    from ..utility import warning_print

    global _linode_client

    try:
        region_name = server_resource.properties['region']
        type_name = server_resource.properties['type']
        group_name = server_resource.properties['group']
        region_id = _linode_types_ni.get(region_name, 'us-east-1a')
        type_id = _linode_types_ni.get(type_name, 'g5-standard-1')

        server_resource._linode_object = _linode_client.linode.create_instance(type_id, region_id)
        server_resource._linode_object.label = server_resource.name
        server_resource._linode_object.group = group_name
        server_resource._linode_object.save()
        server_resource._linode_object.allocate_ip(public=False)

        _linode_server_ensure_offline(server_resource)
    except Exception as e:
        warning_print('\033[31;1m_linode_server_create({0})\033[0m', server_resource.slug)
        raise


def _linode_server_delete(server_resource):
    from linode.errors import ApiError
    from ..utility import warning_print

    try:
        _linode_server_ensure_offline(server_resource)

        while True:
            try:
                if server_resource._linode_object.delete():
                    break
            except ApiError as e:
                if e.status in (404,):
                    break
                else:
                    raise

        _linode_server_ensure_missing(server_resource)
    except Exception as e:
        warning_print('\033[31;1m_linode_server_delete({0})\033[0m', server_resource.slug)
        raise


def _linode_server_config(server_resource, devices):
    from ..utility import warning_print

    try:
        _linode_server_ensure_offline(server_resource)
        server_resource._linode_object.invalidate()

        for config in server_resource._linode_object.configs:
            config.delete()

        server_resource._linode_object.create_config(label='default', devices=devices)

        _linode_server_ensure_running(server_resource)
    except Exception as e:
        warning_print('\033[31;1m_linode_server_config({0})\033[0m', server_resource.slug)
        raise


def _linode_server_shutdown(server_resource):
    from ..utility import warning_print

    try:
        _linode_server_ensure_offline(server_resource)
    except Exception as e:
        warning_print('\033[31;1m_linode_server_shutdown({0})\033[0m', server_resource.slug)
        raise


def _linode_server_sync(server_resource):
    from linode import Disk
    from linode import Volume
    from .linode_constants import DNS_RESOLVERS
    from ..utility import warning_print

    try:
        if server_resource._linode_object:
            fqdn = server_resource.properties.get('fqdn', None)
            network = {
                'ipv4': {
                    'private': [],
                    'public': [],
                    'dns': DNS_RESOLVERS[server_resource._linode_object.region.id]['ipv4']
                },
                'ipv6': {
                    'slaac': [],
                    'dns': DNS_RESOLVERS[server_resource._linode_object.region.id]['ipv6']
                }
            }

            ips = server_resource._linode_object.ips

            for ipv4 in ips.ipv4.public:
                if fqdn and ipv4.rdns != fqdn:
                    ipv4.rdns = fqdn
                    #ipv4.save()

                server_resource.ipv4 = ipv4.address

                network['ipv4']['public'].append({
                    'address': ipv4.address,
                    'subnet_prefix': ipv4.prefix,
                    'subnet_mask': ipv4.subnet_mask,
                    'gateway': ipv4.gateway
                })

            for ipv4 in ips.ipv4.private:
                network['ipv4']['private'].append({
                    'address': ipv4.address,
                    'subnet_prefix': ipv4.prefix,
                    'subnet_mask': ipv4.subnet_mask,
                    'gateway': ipv4.gateway
                })

            for ipv6 in [ips.ipv6.slaac]:
                if fqdn and ipv6.range['rdns'] != fqdn:
                    ipv6.range['rdns'] = fqdn
                    #ipv6.save()

                server_resource.ipv6 = ipv6.range['address']

                network['ipv6']['slaac'].append({
                    'address': ipv6.range['address'],
                    'subnet_prefix': ipv6.range['prefix'],
                    'subnet_mask': ipv6.range['subnet_mask'],
                    'gateway': ipv6.range['gateway']
                })

            storage = []

            for config in server_resource._linode_object.configs:
                if config.label == 'default':
                    devices = vars(config.devices)

                    for name in sorted(devices.keys()):
                        device = devices[name]

                        if type(device) is Disk:
                            for child in server_resource.children:
                                if (child.type == '{linode}disk') and (child.id == device.id):
                                    storage.append({
                                        'device_type': 'disk',
                                        'device_path': '/dev/{0}'.format(name),
                                        'mount_path': child.properties['mount-path'],
                                        'filesystem_type': child.properties['filesystem-type']
                                    })
                        elif type(device) is Volume:
                            for child in server_resource.children:
                                if (child.type == '{linode}volume') and (child.id == device.id):
                                    storage.append({
                                        'device_type': 'volume',
                                        'device_path': '/dev/{0}'.format(name),
                                        'mount_path': child.properties['mount-path'],
                                        'filesystem_type': child.properties['filesystem-type']
                                    })

            server_resource.id = server_resource._linode_object.id
            server_resource.code = server_resource._linode_object.label
            server_resource.properties['network'] = network
            server_resource.properties['storage'] = storage
        else:
            server_resource.id = None
            server_resource.code = None
            server_resource.ipv4 = None
            server_resource.ipv6 = None
    except Exception as e:
        warning_print('\033[31;1m_linode_server_sync({0})\033[0m', server_resource.slug)
        raise


def _linode_disk_ensure_ready(server_resource, disk_resource):
    from linode.errors import ApiError
    from time import sleep
    from ..utility import warning_print

    try:
        while True:
            try:
                if disk_resource._linode_object.status == 'ready':
                    break

                disk_resource._linode_object.invalidate()
                sleep(2)
            except ApiError as e:
                if e.status in (404,):
                    pass
                else:
                    raise
    except Exception as e:
        warning_print('\033[31;1m_linode_disk_ensure_ready({0})\033[0m', disk_resource.slug)
        raise


def _linode_disk_ensure_missing(server_resource, disk_resource):
    from linode.errors import ApiError
    from time import sleep
    from ..utility import warning_print

    try:
        while True:
            try:
                if disk_resource._linode_object.delete():
                    sleep(5)

                disk_resource._linode_object.invalidate()
                sleep(2)
            except ApiError as e:
                if e.status in (404,):
                    break
                else:
                    raise
    except Exception as e:
        warning_print('\033[31;1m_linode_disk_ensure_missing({0})\033[0m', disk_resource.slug)
        raise


def _linode_disk_select(server_resource, disk_resource):
    from linode import Disk
    from linode.errors import ApiError
    from ..utility import warning_print

    global _linode_client

    try:
        disk_resource._linode_object = None

        if not disk_resource.id:
            return

        try:
            disk_object = Disk(_linode_client, disk_resource.id, server_resource.id)
            disk_object._api_get()
            disk_resource._linode_object = disk_object
        except ApiError as e:
            if e.status in (404,):
                return
            else:
                raise
    except Exception as e:
        warning_print('\033[31;1m_linode_disk_select({0})\033[0m', disk_resource.slug)
        raise


def _linode_disk_create(server_resource, disk_resource):
    from random import SystemRandom
    from string import ascii_lowercase
    from string import ascii_uppercase
    from string import digits
    from ..utility import warning_print

    global _linode_distributions_ni

    filesystem_type = '?'
    filesystem_size = -1

    try:
        filesystem_type = disk_resource.properties['filesystem-type']
        filesystem_size = int(disk_resource.properties['filesystem-size'])
        distribution_name = disk_resource.properties.get('distribution-name', None)
        authorized_keys = disk_resource.properties.get('authorized-keys', None)
        distribution_id = _linode_distributions_ni.get(distribution_name, None)
        root_pass = None if distribution_id is None else ''.join(
            SystemRandom().choice(ascii_lowercase + ascii_uppercase + digits) for _ in range(12))

        _linode_server_ensure_offline(server_resource)

        if disk_resource._linode_object:
            if (disk_resource.state == 0) or (disk_resource._linode_object.filesystem != filesystem_type):
                _linode_disk_delete(server_resource, disk_resource)
                disk_resource._linode_object = None

        if filesystem_size == 0:
            server_resource._linode_object.invalidate()

            filesystem_size = server_resource._linode_object.specs.disk

            for disk in server_resource._linode_object.disks:
                filesystem_size -= disk.size

        if authorized_keys:
            authorized_keys = authorized_keys.splitlines()

        disk_resource._linode_object = server_resource._linode_object.create_disk(
            filesystem_size,
            label=disk_resource.name,
            filesystem=filesystem_type,
            distribution=distribution_id,
            root_pass=root_pass,
            authorized_keys=authorized_keys)

        _linode_disk_ensure_ready(server_resource, disk_resource)
    except Exception as e:
        warning_print(
            '\033[31;1m_linode_disk_create({0}, {1}, {2})\033[0m',
            disk_resource.slug,
            filesystem_type,
            filesystem_size)
        raise


def _linode_disk_delete(server_resource, disk_resource):
    from linode.errors import ApiError
    from ..utility import warning_print

    try:
        try:
            _linode_server_ensure_offline(server_resource)
        except ApiError as e:
            if e.status in (404,):
                pass
            else:
                raise

        while True:
            try:
                if disk_resource._linode_object.delete():
                    break
            except ApiError as e:
                if e.status in (404,):
                    break
                else:
                    raise

        _linode_disk_ensure_missing(server_resource, disk_resource)
    except Exception as e:
        warning_print('\033[31;1m_linode_disk_delete({0})\033[0m', disk_resource.slug)
        raise


def _linode_disk_sync(disk_resource):
    from ..utility import warning_print

    try:
        if disk_resource._linode_object:
            disk_resource.id = disk_resource._linode_object.id
            disk_resource.code = disk_resource._linode_object.label
        else:
            disk_resource.id = None
            disk_resource.code = None

        disk_resource.ipv4 = None
        disk_resource.ipv6 = None
    except Exception as e:
        warning_print('\033[31;1m_linode_disk_sync({0})\033[0m', disk_resource.slug)
        raise


def _linode_volume_ensure_ready(server_resource, volume_resource):
    from linode.errors import ApiError
    from ..utility import warning_print

    try:
        while True:
            try:
                volume_resource._linode_object.invalidate()

                if volume_resource._linode_object.status == 'active':
                    break
            except ApiError as e:
                if e.status in (404,):
                    pass
                else:
                    raise
    except Exception as e:
        warning_print('\033[31;1m_linode_volume_ensure_ready({0})\033[0m', volume_resource.slug)
        raise


def _linode_volume_ensure_missing(server_resource, volume_resource):
    from linode.errors import ApiError
    from ..utility import warning_print

    try:
        while True:
            try:
                volume_resource._linode_object.invalidate()

                if volume_resource._linode_object.status != None:
                    volume_resource._linode_object.delete()
            except ApiError as e:
                if e.status in (404,):
                    break
                else:
                    raise
    except Exception as e:
        warning_print('\033[31;1m_linode_volume_ensure_missing({0})\033[0m', volume_resource.slug)
        raise


def _linode_volume_select(server_resource, volume_resource):
    from linode import Volume
    from linode.errors import ApiError
    from ..utility import warning_print

    global _linode_client

    try:
        volume_resource._linode_object = None

        if not volume_resource.id:
            return

        try:
            volume_object = Volume(_linode_client, volume_resource.id)
            volume_object._api_get()
            volume_resource._linode_object = volume_object
        except ApiError as e:
            if e.status in (404,):
                return
            else:
                raise
    except Exception as e:
        warning_print('\033[31;1m_linode_volume_select({0})\033[0m', volume_resource.slug)
        raise


def _linode_volume_create(server_resource, volume_resource):
    from ..utility import warning_print

    global _linode_client

    filesystem_size = -1

    try:
        filesystem_size = int(volume_resource.properties['filesystem-size'])

        _linode_server_ensure_offline(server_resource)

        if volume_resource._linode_object:
            if volume_resource.state == 0:
                _linode_volume_delete(server_resource, volume_resource)
                volume_resource._linode_object = None

        volume_resource._linode_object = _linode_client.linode.create_volume(
            region=server_resource._linode_object.region,
            size=(filesystem_size + 1023) // 1024,
            label='{0}__{1}'.format(server_resource.name, volume_resource.name))

        _linode_volume_ensure_ready(server_resource, volume_resource)
    except Exception as e:
        warning_print(
            '\033[31;1m_linode_volume_create({0}, {1})\033[0m',
            volume_resource.slug,
            filesystem_size)
        raise


def _linode_volume_delete(server_resource, volume_resource):
    from linode.errors import ApiError
    from ..utility import warning_print

    try:
        try:
            _linode_server_ensure_offline(server_resource)
        except ApiError as e:
            if e.status in (404,):
                pass
            else:
                raise

        while True:
            try:
                if volume_resource._linode_object.delete():
                    break
            except ApiError as e:
                if e.status in (404,):
                    break
                else:
                    raise

        _linode_volume_ensure_missing(server_resource, volume_resource)
    except Exception as e:
        warning_print('\033[31;1m_linode_volume_delete({0})\033[0m', volume_resource.slug)
        raise


def _linode_volume_sync(volume_resource):
    from ..utility import warning_print

    try:
        if volume_resource._linode_object:
            volume_resource.id = volume_resource._linode_object.id
            volume_resource.code = volume_resource._linode_object.label
        else:
            volume_resource.id = None
            volume_resource.code = None

        volume_resource.ipv4 = None
        volume_resource.ipv6 = None
    except Exception as e:
        warning_print('\033[31;1m_linode_volume_sync({0})\033[0m', volume_resource.slug)
        raise
