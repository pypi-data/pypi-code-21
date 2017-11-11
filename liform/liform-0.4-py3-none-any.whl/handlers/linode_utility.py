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

    global _linode_client
    global _linode_regions_ni
    global _linode_regions_in
    global _linode_domains_ni
    global _linode_domains_in
    global _linode_distributions_ni
    global _linode_distributions_in
    global _linode_types_ni
    global _linode_types_in

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


# offline         The Linode is powered off.
# booting         The Linode is currently booting up.
# running         The Linode is currently running.
# shutting_down   The Linode is currently shutting down.
# rebooting       The Linode is rebooting.
# provisioning    The Linode is being created.
# deleting        The Linode is being deleted.
# migrating       The Linode is being migrated to a new host/region.


def _linode_server_ensure_running(server_resource):
    from time import sleep

    while True:
        if server_resource._linode_object.status == 'running':
            break

        if server_resource._linode_object.status == 'offline':
            server_resource._linode_object.boot()
            sleep(5)

        server_resource._linode_object.invalidate()
        sleep(2)


def _linode_server_ensure_offline(server_resource):
    from time import sleep

    if not server_resource:
        return

    if not server_resource._linode_object:
        return

    while True:
        if server_resource._linode_object.status == 'offline':
            break

        if server_resource._linode_object.status == 'running':
            server_resource._linode_object.shutdown()
            sleep(5)

        server_resource._linode_object.invalidate()
        sleep(2)


def _linode_server_ensure_missing(server_resource):
    from linode.errors import ApiError
    from time import sleep

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


def _linode_server_select(server_resource):
    from linode import Linode
    from linode.errors import ApiError

    global _linode_client

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


def _linode_server_create(server_resource):
    region_name = server_resource.properties.get('region', 'us-east-1a')
    type_name = server_resource.properties.get('type', 'Linode 2048')
    group_name = server_resource.properties.get('group', 'default')
    region_id = _linode_types_ni.get(region_name, 'us-east-1a')
    type_id = _linode_types_ni.get(type_name, 'g5-standard-1')

    server_resource._linode_object = _linode_client.linode.create_instance(type_id, region_id)
    server_resource.id = server_resource._linode_object.id
    server_resource.code = getattr(server_resource._linode_object, 'label', None)
    server_resource.ipv4 = getattr(server_resource._linode_object, 'ipv4', [None])[0]
    server_resource.ipv6 = getattr(server_resource._linode_object, 'ipv6', None)

    server_resource._linode_object.label = server_resource.name
    server_resource._linode_object.group = group_name
    server_resource._linode_object.save()

    _linode_server_ensure_offline(server_resource)


def _linode_server_delete(server_resource):
    from linode.errors import ApiError

    if server_resource._linode_object:
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


def _linode_server_config(server_resource, devices):
    _linode_server_ensure_offline(server_resource)
    server_resource._linode_object.invalidate()

    for config in server_resource._linode_object.configs:
        config.delete()

    server_resource._linode_object.create_config(label='default', devices=devices)

    _linode_server_ensure_running(server_resource)


def _linode_server_shutdown(server_resource):
    _linode_server_ensure_offline(server_resource)


# ready      No disk jobs are running.
# not ready  This disk is temporarily busy.
# deleting   This disk is being deleted


def _linode_disk_ensure_ready(server_resource, disk_resource):
    from linode.errors import ApiError
    from time import sleep

    global _linode_client

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


def _linode_disk_ensure_missing(server_resource, disk_resource):
    from linode.errors import ApiError
    from time import sleep

    global _linode_client

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


def _linode_disk_select(server_resource, disk_resource):
    from linode import Disk
    from linode.errors import ApiError

    global _linode_client

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


def _linode_disk_create(server_resource, disk_resource):
    from random import SystemRandom
    from string import ascii_lowercase
    from string import ascii_uppercase
    from string import digits

    global _linode_client
    global _linode_distributions_ni

    filesystem_type = disk_resource.properties.get('filesystem-type', 'ext4')
    filesystem_size = int(disk_resource.properties.get('filesystem-size', 4096))
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
            disk_resource.id = None
            disk_resource.code = None
            disk_resource.ipv4 = None
            disk_resource.ipv6 = None

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


def _linode_disk_delete(server_resource, disk_resource):
    from linode.errors import ApiError

    if disk_resource._linode_object:
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


# creating
# active
# resizing
# offline


def _linode_volume_ensure_ready(server_resource, volume_resource):
    from linode.errors import ApiError

    global _linode_client

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


def _linode_volume_ensure_missing(server_resource, volume_resource):
    from linode.errors import ApiError

    global _linode_client

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


def _linode_volume_select(server_resource, volume_resource):
    from linode import Volume
    from linode.errors import ApiError

    global _linode_client

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


def _linode_volume_create(server_resource, volume_resource):
    global _linode_client
    global _linode_distributions_ni

    size = int(volume_resource.properties.get('size', 4096))

    _linode_server_ensure_offline(server_resource)

    if volume_resource._linode_object:
        if volume_resource.state == 0:
            _linode_volume_delete(server_resource, volume_resource)
            volume_resource._linode_object = None
            volume_resource.id = None
            volume_resource.code = None
            volume_resource.ipv4 = None
            volume_resource.ipv6 = None

    volume_resource._linode_object = _linode_client.linode.create_volume(
        region=server_resource._linode_object.region,
        size=(size + 1023) // 1024,
        label='{0}__{1}'.format(server_resource.name, volume_resource.name))

    _linode_volume_ensure_ready(server_resource, volume_resource)


def _linode_volume_delete(server_resource, volume_resource):
    from linode.errors import ApiError

    if volume_resource._linode_object:
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
