import logging
import copy
from pathlib import Path
from collections import OrderedDict

import jinja2

from . import build

log = logging.getLogger('inventory')
log.addHandler(logging.NullHandler())

class DOWrightInventoryError(Exception):
    pass


def find_private_interface(droplet:dict) -> str:
    for interface in droplet.networks['v4']:
        if interface['type'] == 'private':
            return interface['ip_address']
    raise DOWrightInventoryError(
        'The droplet (%s) has no private network interface'.format(
            droplet.name
        )
    )

def get_inventory_groups(builder: build.Builder,
                         inventory_hostnames:dict) -> dict:
    groups = OrderedDict()
    defaults = builder.spec['inventory'].get('defaults',{})

    for name,group_dict in builder.spec['inventory']['groups'].items():
        is_group_of_hosts = 'hosts' in group_dict
        if is_group_of_hosts:
            group_list = group_dict['hosts']
            group = groups[name] = OrderedDict()
        else:
            # Group of groups
            group_list = group_dict['children']
            group = groups[name+':children'] = OrderedDict()

        group['children'] = OrderedDict()
        group['vars'] = group_dict.get('vars',{}).copy()
        for i,group_item in enumerate(group_list):
            new = defaults.copy()

            name = group_item.pop('name')
            new.update(group_item)

            if is_group_of_hosts:
                # If name in inventory_hostnames, then there is a FQDN
                # for this host that should be used
                name = inventory_hostnames.get(builder.droplet_name(name), name)

            group['children'][name] = new

    return groups


def format_group(name, group):
    items = []
    for item_name, item_vars in group.items():
        var_str = ' '.join('{}={}'.format(k,v) for k,v in item_vars.items())
        items.append('{} {}'.format(item_name, var_str))
    group_str = '{name}{items}\n'.format(
        name='[{}]\n'.format(name) if name else '',
        items='\n'.join(items),
    )
    return group_str
    
def format_group_vars(name, group_vars):
    items = ['{}={}'.format(k,v) for k,v in group_vars.items()]
    vars_str = '[{name}:vars]\n{items}\n'.format(
        name=name, items='\n'.join(items),
    )
    return vars_str
    
def create_inventory(builder: build.Builder) -> None:
    inventory_path = Path(builder.spec['inventory']['name'])\
                     .expanduser().resolve()
    log.info('Creating host inventory: %s', inventory_path)
    droplet_configs = builder.droplet_configurations

    if droplet_configs:
        inventory_groups_str = []

        inventory_hosts = OrderedDict()
        inventory_hostnames = {}
        # Individual droplet hosts
        for dconfig in droplet_configs:
            spec, do_droplet, fips, groups, hosts = map(
                dconfig.get, ['spec','dod','fips','groups','hosts']
            )

            # Use the FQDN if a domain has been registered for the
            # droplet, otherwise use the droplet name
            inv_hostname = do_droplet.name
            if hosts:
                inv_hostname = hosts[0]
                # inventory_hostnames will only have keys for droplets
                # with configured FQDNs
                inventory_hostnames[do_droplet.name] = inv_hostname

            ip = fips[0] if fips else do_droplet.ip_address
            user = 'root'
            private_ip = find_private_interface(do_droplet)
            private_hostname = '{}.private'.format(do_droplet.name)

            inventory_hosts[inv_hostname] = OrderedDict([
                ('ansible_host', ip),
                ('ansible_user', user),
                ('private_ipv4_address', private_ip),
                ('private_hostname', private_hostname),
                ('ansible_python_interpreter', '/usr/bin/python3'),
            ])

        inventory_groups_str.append(
            format_group('', inventory_hosts)
        )

        # Droplet groups
        for group_name, droplet_specs in builder.spec['droplets'].items():
            group = OrderedDict()

            for s in droplet_specs:
                c = builder.droplet_kwargs(s)
                name = inventory_hostnames.get(c['name'], c['name'])
                group[name] = {}
                    
            inventory_groups_str.append(
                format_group(group_name, group)
            )

        # Droplet slug groups (i.e. grouping by OS)
        slugs = OrderedDict(sorted(
            [(c['dod'].image['slug'],[]) for c in droplet_configs],
            key=lambda t:t[0],
        ))
        for c in droplet_configs:
            d = c['dod']
            slugs[d.image['slug']].append(
                inventory_hostnames.get(d.name,d.name)
            )
        for slug_name, group_list in slugs.items():
            inventory_groups_str.append(
                format_group(slug_name, {n:{} for n in group_list})
            )

        groups = get_inventory_groups(builder, inventory_hostnames)
        for group_name, group_dict in groups.items():
            inventory_groups_str.append(
                format_group(group_name, group_dict['children'])
            )
            if group_dict['vars']:
                inventory_groups_str.append(
                    format_group_vars(group_name, group_dict['vars'])
                )
                
            
        inventory_path.write_text(
            '\n\n'.join(inventory_groups_str)
        )

        # template = ansible_hosts_conf_template()
        # inventory_path.write_text(
        #     template.render(
        #         all_droplets=all_droplets,
        #         group_configs=group_configs,
        #         groups=get_inventory_groups(builder),
        #         slugs=slugs,
        #         private_ips=private_ips,
        #     )
        # )
    else:
        log.info('.. No droplets to configure.')


ansible_hosts_conf_template = lambda: jinja2.Template('''
{% for droplet in (all_droplets): -%}
{{ droplet.name }} ansible_host={{ droplet.ip_address }} ansible_user=root private_ipv4_address={{ private_ips[droplet.name] }} private_hostname={{ droplet.name }}.private ansible_python_interpreter=/usr/bin/python3
{% endfor %}

{% for dtype in droplet_configs: -%}
{%   if droplet_configs[dtype]|length -%}
[{{ dtype }}]
{%     for droplet in droplet_configs[dtype]: -%}
{{ droplet.name }}
{%     endfor -%}
{%   endif -%}
{% endfor -%}


{% for slug in slugs -%}
[{{ slug }}]
{%   for droplet in slugs[slug] -%}
{{ droplet.name }}
{%   endfor -%}
{% endfor -%}


{% for gname in groups: -%}
{%   if groups[gname]|length -%}
[{{ gname }}]
{%     for group in groups[gname] -%}
{{ group.name }}
{%     endfor %}
{%   endif -%}
{% endfor %}
''')

