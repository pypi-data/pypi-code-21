import os
import glob
import subprocess
import json
import pprint


class SData(object):
    """
    Parse Tiros Snapshot json data
    """

    def __init__(self, debug):
        self.debug = debug
        self._accounts = dict() #track account id
        self.account_vpc = dict()
        return

    def dprint(self, msg, data):
        if self.debug:
            print("--start--{}".format(msg))
            pprint.pprint(data)
            print("--end--{}".format(msg))

    def update_account(self, acc, vpc):
        try:
            l_vpc = self.account_vpc[acc]
            l_vpc.append(vpc)
        except KeyError:
            self.account_vpc.update({acc:[vpc]})

    def _vpcs_v35(self, data):
        # old Tiros snapshot have reversed key in vpc
        vpc_dict = dict()
        vpcs = data['vpcs']
        vpcs_info = vpcs['tags']
        _tags = vpcs['vpcs']
        for info in vpcs_info:
            _vpc = info['vpc']
            tags = self.get_tags(_vpc, _tags)
            account = info.get('account', 'UnknownAccount')
            vpc_dict.update({info['vpc']: {'state': info['state'],
                                           'cidr': info['cidr'],
                                           'account': account}})
            self._accounts.update({_vpc: account})
            self.update_account(account, _vpc)
        return vpc_dict

    def _vpcs(self, data):
        vpc_dict = dict()
        vpcs = data['vpcs']
        vpcs_infos = vpcs['vpcs']
        _tags = vpcs['tags']
        for info in vpcs_infos:
            _vpc = info['vpc']
            tags = self.get_tags(_vpc, _tags)
            account = info.get('account', 'UnknownAccount')
            vpc_dict.update({_vpc: {'state': info['state'],
                                    'cidr': info['cidr'],
                                    'tags': tags,
                                    'account': account}})
            self._accounts.update({_vpc: account})
            self.update_account(account, _vpc)
        return vpc_dict

    def _subnets(self, data):
        subnets = dict()
        _subnets = data['subnets']
        _tags = _subnets['tags']
        for subnet in _subnets['subnets']:
            _subnet_id = subnet['subnet']
            tags = self.get_tags(_subnet_id, _tags)
            vpc = subnet['vpc']
            account = self._accounts.get(vpc, "UnknownAccount")
            subnets.update({_subnet_id: {'cidr': subnet['cidr'],
                                         'vpc': vpc,
                                         'az': subnet['az'],
                                         'tags': tags,
                                         'account': account}})
            self._accounts.update({_subnet_id: account})
        return subnets

    def _acls(self, data):
        acls = dict()
        _acls = data['acls']
        tags_acl = _acls['tags']
        acl_assoc = {acl["aclassoc"]: {'subnet': acl['subnet'],
                                       'acl': acl['acl']} for acl in _acls['associations']}
        for acl in _acls['acls']:
            tag = next((item for item in tags_acl if item["id"] == acl['acl']), {
                       'key': '', 'value': ''}
                      )
            acls.update(
                    {acl['acl']: self._merge_dicts({"vpc": acl['vpc']}, tag)}
                )
        return {'acl_vpc': acls, 'assoc': acl_assoc}

    def _eni(self, data):
        _enis = data['enis']
        sg_enis = self._mk_item_list(_enis['sgs'], 'sg', 'eni')
        ips = {d['eni']: {'ip': d['ip']} for d in _enis['ips']}
        eni_pp = dict()
        for d in _enis["associations"]:
            p_p_ip = {i: d[i] for i in d if i != 'eni'}
            eni_pp.update({d['eni']: p_p_ip})
        instance_enis = {item['instance']: item['eni']
                         for item in _enis['attachments']}
        eni_detail = self._merge_dicts(ips, eni_pp)
        return sg_enis, instance_enis, eni_detail

    def _elbs(self, data):
        data_elbs = data['elbs']
        sg_elb = {item['sg']: item['elb'] for item in data_elbs['sgs']}
        sg_subnet = {item['elb']: item['subnet']
                     for item in data_elbs['subnets']}
        elb_tags = {item['id']: item['value'] for item in data_elbs['tags']}
        elb_instance = self._mk_item_list(
            data_elbs['instances'], 'instance', 'elb')
        return elb_instance

    def _sg(self, data):
        acls_dict = dict()
        data_sgs = data['sgs']
        sg_tags = data_sgs['tags']
        sg_vpc = {item['sg']: item['vpc'] for item in data_sgs['sgs']}
        sg_egress = self.mk_egress(data_sgs["custom-cidrs"])
        sg_ingress = self.mk_ingress(data_sgs["tcp-udp-cidrs"])
        all_sg = dict()
        for tag in sg_tags:
            name = self.mk_pp_name(tag)
            sg = tag['id']
            vpc = sg_vpc[sg]
            egress = sg_egress.get(sg, {})
            ingress = sg_ingress.get(sg, {})
            sg_detail = {"name": name,
                         "vpc": vpc,
                         "egress": egress,
                         "ingress": ingress}
            all_sg.update({sg: sg_detail})
        return all_sg

    def _igws(self, data):
        _data = data["igws"]
        _attach = _data.get('attachments')
        _tags = _data.get('tags')
        igw_out = dict()
        for item in _attach:
            _vpc = item['vpc']
            account = self._accounts.get(_vpc, "UnknownAccount")
            igw_out.update({item['igw']: {'vpc': _vpc,
                                          'account': account,
                                          'state': item['state']}})
        for item in _tags:
            igw_item = igw_out.get(item['id'])
            name = self.mk_pp_name(item)
            if igw_item:
                igw_item.update({'name': name})
        return igw_out

    def get_tags(self, id, tags):
        tag_out = {tag['key']: tag['value'] for tag in tags if tag["id"] == id}
        return tag_out

    def mk_egress(self, custom_cidrs):
        out = dict()
        for d in custom_cidrs:
            rule = {i: d[i] for i in d if i not in ['sg', 'dir']}
            out.update({d['sg']: rule})
        return out

    def mk_ingress(self, tcp_udp_cidrs):
        out = dict()
        for item in tcp_udp_cidrs:
            port = item["ports"]
            pp = "%s-%s" % (port.get("from", ""), port.get("to", ""))
            rule = {i: item[i]
                    for i in item if i not in ['ports', 'dir', 'sg']}
            rule.update({"ports": pp})
            out.update({item["sg"]: rule})
        return out

    def _old_instances(self, data):
        """
        For old snapshots that don't have instance-subnets key
        """
        instance_dict = dict()
        _states = {ins['instance']: ins['state']
                   for ins in data.get('instances', [])}
        for inst in data["instances"]:
            instance = inst['instance']
            tags = self.get_tags(instance, data['tags'])
            sub = inst['subnet']
            state = _states.get(instance, '')
            account = self._accounts.get(sub, "UnknownAccount")
            instance_dict.update({instance: {'subnet': sub,
                                             'tags': tags,
                                             'state': state,
                                             'account': account}})
        return instance_dict

    def _instances(self, data):
        """
        Deal with Instances data
        return a dictionary of instances
        """
        _instances = data['instances']
        inst_subnet = _instances.get('instance-subnets')
        if not inst_subnet:
            return self._old_instances(_instances)
        _subnets = {sub['instance']: sub['subnet'] for sub in inst_subnet}
        instance_dict = dict()
        _states = {ins['instance']: ins['state']
                   for ins in _instances.get('instances', [])}
        for in_sub in inst_subnet:
            instance = in_sub['instance']
            subnet = in_sub['subnet']
            tags = self.get_tags(instance, _instances['tags'])
            state = _states.get(instance, '')
            account = self._accounts.get(subnet, "UnknownAccount")
            instance_dict.update({instance: {'subnet': subnet,
                                             'account': account,
                                             'tags': tags,
                                             'state': state}})
        return instance_dict

    def _merge_dicts(self, *dict_args):
        result = dict()
        for d in dict_args:
            result.update(d)
        return result

    def _mk_item_list(self, in_list, i_key, i_val):
        out = dict()
        for d in in_list:
            try:
                val = out[d[i_key]]
                val.append(d[i_val])
                out.update({d[i_key]: val})
            except:
                out.update({d[i_key]: [d[i_val]]})
        return out

    def mk_instance_sg(self, sg_enis, instance_enis):
        eni_sg = dict()
        for sg, eni in sg_enis.items():
            for e in eni:
                try:
                    e_sg = eni_sg[e] + [sg]
                    eni_sg.update({e: e_sg})
                except:
                    eni_sg.update({e: [sg]})
        instance_sg_eni = dict()
        for k, v in instance_enis.items():
            instance_sg_eni.update({k: {"sg": eni_sg.get(v, []),
                                        "eni": v}})
        return instance_sg_eni

    def mk_pp_name(self, val_dict):
        if val_dict['key'] == 'Name':
            return val_dict['value']
        else:
            return "{}:{}".format(val_dict['key'], val_dict["value"])

    def process_snapshot(self, filename):
        """
        Read the Tiros Snapshot
        """
        parsed_json = None
        with open(filename) as f:
            parsed_json = json.load(f)
        vpcs = dict()
        try:
            vpcs = self._vpcs(parsed_json)
        except KeyError:
            vpcs = self._vpcs_v35(parsed_json)
        self.dprint("VPCS", vpcs)
        subnets = self._subnets(parsed_json)
        self.dprint("Subnets", subnets)
        instances = self._instances(parsed_json)
        self.dprint("Instances", instances)
        acls = self._acls(parsed_json)
        self.dprint("ACLS", acls)
        sg_enis, instance_enis, eni_detail = self._eni(parsed_json)
        self.dprint("ENIS", instance_enis)
        igws = self._igws(parsed_json)
        self.dprint("IGWS", igws)
        sg_detail = self._sg(parsed_json)
        self.dprint("Accounts", self.account_vpc)
        instance_sg_eni = self.mk_instance_sg(sg_enis, instance_enis)
        eni_sg_detail = {'inst_sg_eni': instance_sg_eni,
                         'sg': sg_detail,
                         'eni': eni_detail}
        return {'vpc': vpcs,
                'subnet': subnets,
                'instances': instances,
                'eni_sg': eni_sg_detail,
                'acl': acls,
                'igws': igws,
                'account': self.account_vpc}
