from ext_cloud.BaseCloud.BaseCompute.BaseSecurityGroup import BaseSecurityGroupcls
from boto import ec2
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls
from ext_cloud.AWS.AWSCompute.AWSSecurityGroupRule import AWSSecurityGroupRulecls


class AWSSecurityGroupcls(AWSBaseCloudcls, BaseSecurityGroupcls):

    __aws_security_group = None

    def __init__(self, *arg, **kwargs):
        self.__aws_security_group = arg[0]

        super(AWSSecurityGroupcls, self).__init__(id=self.__aws_security_group.id,
                                                  name=self.__aws_security_group.name, credentials=kwargs['credentials'])

    @property
    def __EC2(self):
        return self.__ec2

    @__EC2.getter
    def __EC2(self):
        if self.__ec2 is None:
            self.__ec2 = ec2.connect_to_region(self._credentials['region_name'], aws_access_key_id=self._credentials[
                                               'username'], aws_secret_access_key=self._credentials['password'])
        return self.__ec2

    @property
    def description(self):
        return self.__aws_security_group.description

    @property
    def rules(self):
        rules = []
        for rule in self.__aws_security_group.rules:
            cidr_block = None
            for grant in rule.grants:
                cidr_block = grant.cidr_ip
                break
            rule = AWSSecurityGroupRulecls(ip_protocol=rule.ip_protocol,
                                           from_port=rule.from_port,
                                           to_port=rule.to_port,
                                           cidr_block=cidr_block)
            rules.append(rule)

        return rules

    def delete(self):
        self.__aws_security_group.delete()

    def add_rule(self, ip_protocol='tcp', from_port=None, to_port=None, cidr_block='0.0.0.0/0'):
        self.__aws_security_group.authorize(
            ip_protocol=ip_protocol, from_port=from_port, to_port=to_port, cidr_ip=cidr_block)

    def delete_rule(self, ip_protocol='tcp', from_port=None, to_port=None, cidr_block=None):
        self.__aws_security_group.revoke(
            ip_protocol=ip_protocol, from_port=from_port, to_port=to_port, cidr_ip=cidr_block)
