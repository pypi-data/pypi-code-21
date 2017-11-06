import logging
from typing import Union, List
import ipaddress
import copy
import time
from collections import OrderedDict

import jinja2
from digitalocean import Manager, Droplet
from memoized_property import memoized_property
from gems import composite
import paramiko
from paramiko import SSHClient
from tokenmanager import get_tokens

from . import yaml

log = logging.getLogger('build')
log.addHandler(logging.NullHandler())


class DOWrightBuildError(Exception):
    pass


def get_token(dotoken_type:str) -> Union[composite, str]:
    tokens = get_tokens()
    return tokens.digitalocean[dotoken_type]


def find_record(r, domain):
    test = (r['type'], r['name'], r['data'])
    for record in domain.get_records():
        if test == (record.type, record.name, record.data):
            return record


def is_ip_address(address):
    try:
        ipaddress.ip_address(address)
    except ValueError:
        return False
    return True


def droplet_ssh(droplet: Droplet) -> SSHClient:
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(droplet.ip_address, username='root')
    return ssh


def droplet_file_exists(droplet:Droplet, path:str):
    with droplet_ssh(droplet) as ssh:
        _,stdout,_ = ssh.exec_command(
            'cat {} &> /dev/null && echo OK'.format(path)
        )
        exists = bool(stdout.read())
    return exists


cc_udata_template = lambda: jinja2.Template('''\
#cloud-config
runcmd:
{{ commands }}
''')
def get_cloud_config_user_data(commands:list=None) -> str:
    template = cc_udata_template()
    commands = commands or []

    commands.append('touch /.cloud-config-done')

    return template.render(
        commands=yaml.dump(commands),
    )


class Builder:
    def __init__(self, spec:dict, dry_run:bool=False):
        self.spec = spec
        self.dry_run = dry_run

    @memoized_property
    def token(self) -> str:
        return get_token(self.spec['token'])

    @memoized_property
    def manager(self) -> Manager:
        return Manager(token=self.token)

    @property
    def droplets(self) -> list:
        prefix = self.spec['prefix']
        return [d for d in self.manager.get_all_droplets()
                if d.name.startswith(prefix)]

    @property
    def floating_ips(self) -> list:
        ips = self.manager.get_all_floating_ips()
        return ips if ips else []

    @property
    def domains(self) -> list:
        return self.manager.get_all_domains()

    @property
    def droplet_configurations(self) -> list:
        configs = OrderedDict()
        do_dlut = {d.name: d for d in self.droplets}
        domains = self.domains
        floating_ips = self.floating_ips
        for dgroup, droplets in self.spec['droplets'].items():
            for d in droplets:
                kwargs = self.droplet_kwargs(d, [dgroup])
                do_droplet = do_dlut[kwargs['name']]
                fips = [ip.ip for ip in floating_ips
                        if (ip.droplet and ip.droplet['name']==kwargs['name'])]
                allips = set([do_droplet.ip_address] + fips)
                hostnames = []
                for domain in domains:
                    for r in domain.get_records():
                        if r.data in allips:
                            hostnames.append('.'.join([r.name,domain.name]))
                config = {
                    'spec': kwargs,
                    'dod': do_droplet,
                    'fips': fips,
                    'groups': [dgroup],
                    'hosts': hostnames,
                }
                configs[kwargs['name']] = config
        return configs.values()

    def droplet_name(self, name:str) -> str:
        prefix = self.spec['prefix']
        return '{}-{}'.format(prefix, name)

    def prep_domain_records(self, records:list, droplets:list)->list:
        records = records[:]
        for i,rec in enumerate(records):
            rec = rec.copy()
            if not is_ip_address(rec['data']):
                dname = self.droplet_name(rec['data'])
                droplet = [d for d in droplets if d.name == dname][0]
                rec['data'] = droplet.ip_address
            records[i] = rec
        return records

    def prep_droplet(self, droplet:dict) -> dict:
        new = copy.deepcopy(droplet)
        new['name'] = self.droplet_name(droplet['name'])

        config_commands = new.pop('cloud_config_commands',[])
        if config_commands:
            new['user_data'] = get_cloud_config_user_data(config_commands)

        return new

    def droplet_kwargs(self, droplet:dict, tags:List[str]=None) -> dict:
        kwargs = copy.deepcopy(self.spec.get('defaults',{}))
        droplet = self.prep_droplet(droplet)
        log.debug(droplet)
        kwargs.update(droplet)
        kwargs['token'] = self.token
        if tags:
            if 'tags' in kwargs:
                kwargs['tags'].extend(tags)
            else:
                kwargs['tags'] = tags
        return kwargs

    def build_droplets(self) -> None:
        log.info('Building droplets:')
        existing = set(d.name for d in self.droplets)
        prefix = self.spec['prefix']

        for droplet_tag, droplets in self.spec['droplets'].items():
            tags = [droplet_tag, prefix, ]
            kwargs_list = filter(
                lambda kw:kw['name'] not in existing,
                [self.droplet_kwargs(d, tags) for d in droplets]
            )
            # for kwargs in sorted(kwargs_list, key=lambda d:d['name']):
            for kwargs in kwargs_list:
                log.info('  .. building droplet: %s', kwargs['name'])
                droplet = Droplet(**kwargs)
                if not self.dry_run:
                    droplet.create()
                else:
                    log.info('  .. DRY RUN .. did not build.')

        if not self.dry_run:
            droplets = self.droplets
            dlut = {d.name:d for d in droplets}
            new_droplets = [
                dlut[n] for n in set(d.name for d in droplets) - existing
            ]
            log.info('New droplets created:')
            for d in new_droplets:
                log.info('  .. name: %s ip: %s',d.name, d.ip_address)
        else:
            log.info('DRY RUN .. no droplets created.')

    def destroy_droplets(self)->None:
        droplets = self.droplets
        floating_ips = self.floating_ips
        domains = self.domains

        if droplets:
            log.info('Destroying all (%s) droplets...', len(droplets))

            for ip in floating_ips:
                if (ip.droplet and ip.droplet['name'] in {d.name
                                                          for d in droplets}):
                    log.info('  .. unassigning IP (%s) for droplet (%s)',
                             ip.ip, ip.droplet['name'])
                    if not self.dry_run:
                        ip.unassign()
                    else:
                        log.info('  .. DRY RUN .. did not unassign.')

            for domain_name, records in self.spec['domains'].items():
                domain = [d for d in domains if d.name == domain_name][0]
                records = self.prep_domain_records(records, droplets)
                for r in records:
                    record = find_record(r, domain)
                    if record:
                        log.info('  .. removing domain record: %s %s %s',
                                 record.type, record.name, record.data)
                        if not self.dry_run:
                            record.destroy()
                        else:
                            log.info('  .. DRY RUN .. did not remove.')

            log.info('  .. destroying droplets')
            for d in droplets:
                log.info('    .. {}'.format(d.name))
                if not self.dry_run:
                    d.destroy()
                else:
                    log.info('    .. DRY RUN .. did not destroy.')
        else:
            log.info('No droplets to destroy.')

    def configure_floating_ips(self) -> None:
        droplets = self.droplets
        floating_ips = self.floating_ips

        if 'floating_ips' in self.spec:
            log.info('Configuring floating IPs:')
            for ip,name in self.spec['floating_ips'].items():
                fip = [i for i in floating_ips if i.ip == ip]
                if not fip:
                    raise DOWrightBuildError(
                        'No floating IP with ip: {}'.format(ip)
                    )
                fip = fip[0]
                droplet_name = self.droplet_name(name)
                droplets = [d for d in droplets if d.name==droplet_name]
                if not droplets:
                    raise DOWrightBuildError(
                        'No droplet for this spec with'
                        ' name: {} ({})'.format(name, droplet_name)
                    )
                droplet = droplets[0]
                if ((not fip.droplet) or (fip.droplet and
                                          fip.droplet['id'] != droplet.id)):
                    log.info('  assigning %s to %s', fip.ip, droplet.name)
                    if not self.dry_run:
                        fip.assign(droplet.id)
                    else:
                        log.info('  .. DRY RUN .. no assignment.')
        else:
            log.info('No floating IPs to configure.')

    def configure_domains(self) -> None:
        if 'domains' in self.spec:
            log.info('Configuring domains:')

            droplets = self.droplets
            domains = self.domains
            found = False
            for domain_name, records in self.spec['domains'].items():
                domain = [d for d in domains if d.name == domain_name][0]
                records = self.prep_domain_records(records, droplets)
                for r in records:
                    if not find_record(r, domain):
                        found = True
                        kw = {'type':r['type'], 'name':r['name'],
                              'data':r['data']}
                        log.info('  configuring |type: %s|  |name: %s|'
                                 '  |data: %s|',
                                 kw['type'], kw['name'], kw['data'])
                        if not self.dry_run:
                            domain.create_new_domain_record(**kw)
                        else:
                            log.info('  .. DRY RUN .. not configured.')
            if not found:
                log.info('No new domains to be configured.')
        else:
            log.info('No domains to configure.')

    def droplets_still_building(self):
        return [d for d in self.droplets if d.locked]

    def droplets_still_configuring(self):
        ssh_errors = 0
        done = False
        still_configuring = None
        ssh_error = None
        while ssh_errors < 5 and not done:
            try:
                still_configuring = []
                for d in self.droplets:
                    if not droplet_file_exists(d,'/.cloud-config-done'):
                        still_configuring.append(d)
                done = True
            except paramiko.ssh_exception.NoValidConnectionsError as error:
                ssh_errors += 1
                log.error('SSH failed... retrying %s/5',ssh_errors)
                time.sleep(2)
                ssh_error = error
                still_configuring = None
        if still_configuring is None:
            raise ssh_error
        return still_configuring

    def wait_for_build(self) -> None:
        log.info('Waiting for all droplets to finish building:')

        not_done = self.droplets_still_building()
        while not_done:
            log.info(' .. waiting on %s droplets', len(not_done))
            time.sleep(5)
            not_done = self.droplets_still_building()

        not_configured = self.droplets_still_configuring()
        while not_configured:
            log.info(' .. waiting for %s droplets to cloud-config',
                     len(not_configured))
            time.sleep(5)
            not_configured = self.droplets_still_configuring()

        log.info('Done.')
