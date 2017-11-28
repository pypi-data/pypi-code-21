import re
import json
import click
import datetime
from tabulate import tabulate
from pyvss.manager import DATETIME_FMT
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

columns_two = "{0:<40} {1:<20}"
columns_two_kv = "{0:<20}: {1:<20}"
columns_two_os = "{0:<40} {1:<20}"
columns_two_comms = "{0:<40} {1:<20}"
columns_three = "{0:<20} {1:<40} {2:<20}"
columns_four = "{0:<20} {1:<30} {2:<30} {3:<20}"
columns_five = "{0:<40} {1:<30} {2:<30} {3:<10} {4:<10} {5:<10} {6:<20}"


def pretty_print(dictionary):
    _lines = json.dumps(dictionary, indent=4, sort_keys=True)
    lines = highlight(_lines, JsonLexer(), TerminalFormatter())
    return lines


def validate_json_type(ctx, param, value):
    try:
        if value is not None:
            return json.loads(value)
    except ValueError:
        raise click.BadParameter(
            '{} should be a JSON Parameter Input.'.format(param))


def validate_phone_number(ctx, param, phone):
    phone_regex = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|' \
                  r'\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})+'
    if not re.match(phone_regex, phone):
        raise click.BadParameter(
            'Value must be in the following format 416-166-6666')
    return phone


def validate_admin(ctx, param, value):
    if value:
        _value = value.split(':')
        if not value or len(_value) < 2:
            raise click.BadParameter('Admin should be in the '
                                     'following format: '
                                     'FullName:Phone:email')
        validate_email(ctx, param, _value[2])
        validate_phone_number(ctx, param, _value[1])
        return value


def validate_inform(ctx, param, value):
    if value:
        _value = value.split(',')
        if not value:
            raise click.BadParameter('Informational contacts format:'
                                     ' email@utoronto.ca,email2@utoronto.ca')
        for email in _value:
            validate_email(ctx, param, email)
        return value


def validate_schedule(ctx, param, schedule):
    try:
        if schedule is not None:
            datetime.datetime.strptime(schedule, DATETIME_FMT)
            return schedule
    except ValueError:
        raise click.BadParameter(
            'Schedule timestamp must be in {} format.'.format(DATETIME_FMT))


def validate_email(ctx, param, email):
    email_regex = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    if not re.match(email_regex, email):
        raise click.BadParameter('Value must be in the '
                                 'following format user@utoronto.ca')
    return email


def yes_no(val):
    return 'Yes' if val else 'No'


def capitalize(value):
    return re.sub(r"(\w)([A-Z])", r"\1 \2", value).title()


def print_object(dict_obj, key, attribute_list=None):
    lines = []
    _append = lines.append
    if not attribute_list:
        dump(dict_obj, _key=key, _list=lines)
    else:
        for attr in attribute_list:
            value = yes_no(dict_obj[attr]) \
                if isinstance(dict_obj[attr], bool) \
                else dict_obj[attr]
            _append(columns_two_kv.format(
                capitalize(attr), value))
    return lines


def print_objects(objects, no_header, quiet, id, attribute_list):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for o in objects:
            _append([o[id]])
    else:
        header = attribute_list
        for o in objects:
            _append([o[a] for a in attribute_list])
    lines = tabulate(lines, headers=header, tablefmt=tbfmt, missingval='-')
    return lines


def print_morefs(objects, no_header, quiet, table_header=None, **kwargs):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for o in objects:
            _append([o['moref']])
    else:
        header = ['moref', 'name', 'description'] if not table_header \
            else table_header
        for o in objects:
            row = list()
            for i in table_header:
                row.append(o[i])
            _append(row)
    lines = tabulate(lines, headers=header, tablefmt=tbfmt)
    return lines


def print_vm_events(events, **kwargs):
    lines = []
    _append = lines.append
    events = events['events']
    header = ['username', 'created time', 'message']
    for event in events:
        _append([event['userName'], event['createdTime'], event['message']])
    return tabulate(lines, headers=header)


def print_request(request):
    lines = []
    _append = lines.append
    for k, v in request.items():
        if isinstance(v, dict):
            v = ', '.join(['{}: {}'.format(_k, _v) for _k, _v in v.items()])
        elif isinstance(v, list):
            v = ', '.join([str(_v) for _v in v])
        elif isinstance(v, bool):
            v = yes_no(v)
        if k not in ['_links']:
            _append(columns_two_kv.format(k, v))
    return lines


def print_tokens(objects, no_header, quiet, **kwargs):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for o in objects:
            _append([o['id']])
    else:
        header = ['id', 'value', 'valid', 'last_access']
        for o in objects:
            _append([o[header[0]],
                     '{}...'.format(o[header[1]][:60]),
                     o['status']['valid'],
                     o['status'][header[3]]])
    lines = tabulate(lines, headers=header, tablefmt=tbfmt)
    return lines


def print_os(objects, no_header, quiet, table_header=None):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for o in objects:
            _append([o['id']])
    else:
        header = ['id', 'guestId', 'guestFullName']
        for o in objects:
            _append([o[header[0]], o[header[1]], o[header[2]]])
    lines = tabulate(lines, headers=header, tablefmt=tbfmt)
    return lines


def print_requests(requests, no_header, quiet, table_header=None):
    lines = []
    _append = lines.append
    header = []
    tbfmt = 'plain' if no_header or quiet else 'simple'
    if quiet:
        for r in requests:
            _append([r['id']])
    else:
        header = table_header or ['id', 'created_on', 'updated_on',
                                  'status', 'vm_name', 'vm_uuid']
        for r in requests:
            row = list()
            for h in header:
                row.append(r[h])
            _append(row)
    lines = tabulate(lines, headers=header, tablefmt=tbfmt)
    return lines


def print_vm_attr(uuid, obj, attrs=None, **kwargs):
    lines = []
    _append = lines.append
    _extend = lines.extend
    _append(columns_two_kv.format('Uuid', uuid))
    if not attrs:
        for i in obj:
            _extend([columns_two_kv.format(k, v) for k, v in i.items()])
        return lines
    for a in attrs:
        if isinstance(a, tuple):
            value = obj[a[0]][a[1]]
            key = ' '.join(a)
        else:
            value = obj[a]
            key = a

        if isinstance(value, bool):
            value = yes_no(value)
        elif isinstance(value, list):
            value = ', '.join([str(v) for v in value])
        _append(columns_two_kv.format(capitalize(key), value))
    return lines


def print_vm_objects_attr(uuid, objects, attrs, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', uuid))
    for obj in objects:
        for a in attrs:
            if isinstance(a, tuple):
                value = obj[a[0]][a[1]]
                key = ' '.join(a)
            else:
                value = obj[a]
                key = a

            if isinstance(value, bool):
                value = yes_no(value)
            elif isinstance(value, list):
                value = ', '.join([str(v) for v in value])
            _append(columns_two_kv.format(capitalize(key), value))
    return lines


def print_vm_disks_summary(uuid, disks, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', uuid))
    for disk in disks:
        _append(columns_two_kv.format(
            disk['data']['label'],
            '{} GB'.format(disk['data']['capacityGB'])))
    return lines


def print_vm_cds_summary(uuid, cds, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', uuid))
    for cd in cds:
        _append(columns_two_kv.format(
            cd['data']['label'],
            cd['data']['backing']))
    return lines


def print_vm_snaps_summary(uuid, snaps, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', uuid))
    for snap in snaps:
        _append(columns_two_kv.format(
            'Snapshot {}'.format(snap['id']), snap['name']))
    return lines


def print_vm_nics_summary(uuid, nics, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', uuid))
    for nic in nics:
        _append(columns_two_kv.format(
            nic['data']['label'], nic['data']['macAddress']))
    return lines


def print_vm_info(vm, **kwargs):
    lines = []
    _append = lines.append
    _append(columns_two_kv.format('Uuid', vm['uuid']))
    _append(columns_two_kv.format('Name', vm['name']['full_name']))
    _append(columns_two_kv.format('Folder', vm['folder']['path']))
    _append(columns_two_kv.format('Guest OS', vm['config']['os']['guestId']))
    _append(columns_two_kv.format('Version', vm['hardware']['version']))
    _append(columns_two_kv.format('Status', vm['state']['overallStatus']))
    _append(columns_two_kv.format('State',
                                  vm['state']['powerState']))
    _append(columns_two_kv.format('Alarms', yes_no(vm['state']['alarms'])))
    _append(columns_two_kv.format('CPU/Memory (GB)', '{}/{}'.format(
        vm['hardware']['cpu']['cpuCount'],
        vm['hardware']['memory']['memoryGB'])))
    _append(columns_two_kv.format('Provisioned (GB)',
                                  vm['storage']['provisionedGB']))
    _append(columns_two_kv.format('Snapshot', yes_no(vm['snapshot']['exist'])))
    _append(columns_two_kv.format('Admin', vm['vss']['admin']))
    disks = vm['hardware']['devices']['disks']
    _append(columns_two_kv.format('Disks', len(disks)))
    nics = vm['hardware']['devices']['nics']
    _append(columns_two_kv.format('NICs', len(nics)))
    return lines


def dump(obj, _key=None, _list=None):
    for key, value in obj.items():
        if isinstance(value, list):
            for i in value:
                if isinstance(i, dict):
                    dump(i, key, _list)
                else:
                    _list.append(columns_two_kv.format(key, i))
        elif not isinstance(value, dict) and not isinstance(value, list):
            _k = _key + '.' + key
            if isinstance(value, bool):
                value = yes_no(value)
            _list.append(columns_two_kv.format(_k, value))
        elif key not in ['_links']:
            dump(value, key, _list)


def get_all_inv_attrs():
    return {'status': 'Status', 'domain': 'Fault Domain',
            'diskCount': 'Disk Count', 'uuid': 'Uuid', 'nics': 'NICs',
            'state': 'State', 'dnsName': 'DNS Name',
            'vmtRunning': 'VMware Tools Running Status',
            'memory': 'Memory',
            'provisionedSpace': 'Provisioned Space', 'osId': 'OS Id',
            'folder': 'Folder', 'snapshot': 'Snapshot',
            'requested': 'Requested', 'networkIds': 'Network IDs',
            'hardwareVersion': 'Hardware Version',
            'changeLog': 'Change Log', 'ha_group': 'HA Group',
            'usedSpace': 'Used Space', 'nicCount': 'NIC Count',
            'uncommittedSpace': 'Uncommitted Space',
            'name': 'Name', 'admin': 'Admin', 'disks': 'Hard Disks',
            'vmtVersion': 'VMware Tools Version Status',
            'inform': 'Inform', 'client': 'Client', 'guestOsId': 'Guest OS Id',
            'clientNotes': 'Client Notes',
            'ipAddress': 'IP Address', 'cpu': 'CPU'}
