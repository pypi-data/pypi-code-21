import os
import json
import pprint


class QData(object):
    """
    Prepare query data
    """

    def __init__(self, ):
        # first class nodes
        self.fc_nodes = ['vpc', 'subnet', 'i']
        return

    def _eni(self, data):
        _enis = data['enis']
        sg_enis = self._mk_item_list(_enis['sgs'], 'sg', 'eni')
        ips = {d['eni']: d['ip'] for d in _enis['ips']}
        eni_ips = dict()
        for d in _enis["associations"]:
            p_p_ip = {i: d[i] for i in d if i != 'eni'}
            if p_p_ip is {}:
                p_p_ip = {"ip": ips.get(d['eni'], '')}
            eni_ips.update({d['eni']: p_p_ip})
        instance_enis = {item['eni']: item['instance']
                         for item in _enis['attachments']}
        return sg_enis, instance_enis, eni_ips

    def _acls_rtbs(self, data):
        _acls = data['acls']
        _rtbs = data['rtbs']
        acl = self._mk_item_list(_acls['associations'], 'acl', 'subnet')
        rtb = self._mk_item_list(_rtbs['associations'], 'rtb', 'subnet')
        return acl, rtb

    def _igws_elbs(self, data):
        _igws = data['igws']
        _elbs = data['elbs']
        igws = self._mk_item_list(_igws['attachments'], 'igw', 'vpc')
        elbs = self._mk_item_list(_elbs['elbs'], 'rtb', 'vpc')
        return igws, elbs

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

    def _get_instance(self, item, snap_data):
        sg_enis, instance_enis, eni_ips = self._eni(snap_data)
        enis = sg_enis.get(item)
        out = list()
        if not enis:
            instance = instance_enis.get(item)
            if instance:
                out.append(instance)
        else:
            out = enis
        return out

    def _get_subnet(self, item, snap_data):
        acl, rtb = self._acls_rtbs(snap_data)
        s_acl = acl.get(item)
        s_rtb = rtb.get(item)
        out = s_acl if s_acl else s_rtb
        return out if out else []

    def _get_vpc(self, item, snap_data):
        igw, elb = self._igws_elbs(snap_data)
        v_igw = igw.get(item)
        v_elb = elb.get(item)
        out = v_igw if v_igw else v_elb
        return out if out else []

    def get_fc(self, item, snap_data):
        """
        Get a list of first class nodes
        """
        key = item.split('-')[0]
        if key in ["sg", "eni"]:
            blink = self._get_instance(item, snap_data)
        elif key in ["acl", "rtb"]:
            blink = self._get_subnet(item, snap_data)
        elif key in ["igw", 'elb']:
            blink = self._get_vpc(item, snap_data)
        elif key in self.fc_nodes:
            blink = [item]
        else:
            blink = []
        return blink

    def proc_query_data(self,  query_data, snap_filename):
        """
        Post process query data to find relationship
        """
        query_data_out = query_data
        with open(snap_filename) as f:
            parsed_json = json.load(f)
        for item in query_data_out:
            color = list()
            for tag, value in item.items():
                new_fc = self.get_fc(value, parsed_json)
                if new_fc:
                    color.append(new_fc)
            out = set([item1 for sub in color for item1 in sub])
            item.update({"h_color": list(out)})
        return query_data_out
