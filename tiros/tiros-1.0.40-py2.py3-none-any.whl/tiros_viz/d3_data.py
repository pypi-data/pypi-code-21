import json
import pprint


class D3Data(object):
    """
    Manipulate D3 Data
    """

    def __init__(self, debug):
        self.debug = debug
        return

    def _mk_vpc(self, data):
        nodes = list()
        for vpc, vpc_value in data.items():
            tags = vpc_value.get('tags', {})
            name = tags.get('Name', vpc)
            vpc_prop = {'cidr': vpc_value['cidr'],
                        'color': 'vpc',
                        'state': vpc_value['state'],
                        'tags': tags}
            vpc_node = {'id': vpc,
                        'name': name,
                        'account': vpc_value['account'],
                        'properties': vpc_prop}
            nodes.append(vpc_node)
        return nodes

    def _mk_subnets(self, data):
        nodes, links = list(), list()
        for s, s_value in data.items():
            vpc = s_value['vpc']
            tags = s_value.get('tags', {})
            name = tags.get('Name', s)
            s_prop = {'cidr': s_value['cidr'],
                      'color': 'subnet',
                      'vpc': vpc,
                      'az': s_value['az'],
                      'tags': tags}
            sub_node = {'id': s,
                        'name': name,
                        'account': s_value['account'],
                        'properties': s_prop}
            v_link = {'source': vpc,
                      'target': s,
                      'properties': {'vpc': vpc,
                                     'type': 'vpc_link'}}
            nodes.append(sub_node)
            links.append(v_link)
        return nodes, links

    def _mk_sg(self, ids, details):
        out = dict()
        for sg in ids:
            sg_detail = details.get(sg, {})
            sg_detail.update({'id': sg})
            out.update({sg:sg_detail})
        return out

    def _mk_instances(self, instances, details):
        eni_details = details.get('eni')
        sg_details = details.get('sg')
        inst_sg_eni = details.get('inst_sg_eni')
        nodes, links = list(), list()
        for i, i_value in instances.items():
            subnet = i_value['subnet']
            s_link = {'source': subnet,
                      'target': i,
                      'properties': {'subnet': subnet,
                                     'type': 'subnet_link'}}
            tags = i_value.get('tags', {})
            name = tags.get('Name', i)
            sg_id = inst_sg_eni.get(i).get('sg')
            sg = self._mk_sg(sg_id, sg_details)
            eni_id = inst_sg_eni.get(i).get('eni')
            eni = eni_details.get(eni_id, {})
            eni.update({'id': eni_id})
            tags.update({'id': 'tags'})
            i_prop = {'subnet': subnet,
                      'color': 'instance',
                      'tags': tags,
                      'state': i_value['state'],
                      'sg': sg,
                      'eni': eni}
            i_node = {'id': i,
                      'name': name,
                      'account': i_value['account'],
                      'properties': i_prop}
            nodes.append(i_node)
            links.append(s_link)
        return nodes, links

    def mk_vsi(self, data):
        """
        Gather all data in one dictionary for VSI view
        """
        nodes, links = list(), list()
        n_vpc = self._mk_vpc(data['vpc'])
        n_subnet, l_subnet =self._mk_subnets(data['subnet'])
        n_inst, l_inst = self._mk_instances(data['instances'], data['eni_sg'])
        n_igw, l_igw = self._mk_igw(data['igws'])
        n_account, l_account = self._mk_account(data['account'])
        nodes = n_vpc +  n_subnet + n_inst + n_igw + n_account
        links = l_subnet + l_inst +  l_igw + l_account
        d3json = {"label": "Tiros Snapshot Visualization",
                  "Snapshot View": "VPC-Subnet-Instance",
                  "links": links,
                  "nodes": nodes}
        return d3json

    def _mk_igw(self, igws):
        nodes, links = list(), list()
        for igw, val in igws.items():
            prop = {'name': val.get('name', 'NoName'),
                    'state': val.get('state', 'Unknown'),
                    'color': 'igw'}
            nodes.append({'id': igw,
                          'name': igw,
                          'account': val['account'],
                          'properties': prop})
            igw_link = {"source": igw,
                        "target": val['vpc'],
                        "properties": {"type": "igw_link"}}
            links.append(igw_link)
        return nodes, links

    def _mk_account(self, acc):
        nodes, links = list(), list()
        for k, vpc in acc.items():
            nodes.append({'id': k,
                          'name': k,
                          'account': k,
                          'properties': {'color': 'aws_account'}})
            account_link = [{"source": k,
                             "target": v,
                             "properties": {"type": "account_link"}} for v in vpc]
            links += account_link
        return nodes, links

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
