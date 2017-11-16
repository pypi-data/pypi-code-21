from __future__ import absolute_import, division, print_function, unicode_literals

import time
from botocore.parsers import EC2QueryParser, ResponseParserFactory


class PassthroughParser(EC2QueryParser):
    """
    What follows is a patch to also include the raw xml on the wire
    before it hits all of botocore's xml -> json parsing. The reason we
    want the raw xml out is the fact that we can pass it directly to the
    pre-existing nice type-safe java xml unmarshalers on the scala side
    of the world. We also return the parsed json data so that we can do
    pagination and extract certain other bits of it when we need to.
    """

    # noinspection PyMissingConstructor
    def __init__(self, _parser):
        super(PassthroughParser, self).__init__(_parser)
        self.old_parser = _parser

    # noinspection PyProtectedMember
    def _do_parse(self, response, shape):
        parsed = self.old_parser._do_parse(response, shape)
        return {'xml': response['body'], 'parsed': parsed}


class PassthroughParserFactory(ResponseParserFactory):
    # noinspection PyMissingConstructor
    def __init__(self, factory):
        super(PassthroughParserFactory, self).__init__()
        self.old_factory = factory

    def create_parser(self, protocol_name):
        _parser = self.old_factory.create_parser(protocol_name)
        return PassthroughParser(_parser)


def get_results(client, method, **kwargs):
    # This will intentionally fail for api calls that *can* be
    # paginated, because you should be calling get_pages. Returns one
    # xml string of all the results.
    time.sleep(0.1)
    result = getattr(client, method)(**kwargs)
    assert not (client.can_paginate(method))
    return result['xml']


# This will intentionally fail (because the get_paginator call
# will fail) for api calls that *can't* be paginated, because you
# should be calling get_results. Returns a list of xml strings of
# all the results.
# noinspection PyProtectedMember
def get_pages(client, method, **kwargs):
    # XXX: CLI dies with an inscrutable error message on this line if the
    # caller doesn't have permission.  The error message should be better.
    time.sleep(0.1)
    result = getattr(client, method)(**kwargs)
    pagination = client.get_paginator(method)._pagination_cfg
    input_token = pagination['input_token']
    output_token = pagination['output_token']
    result_key = pagination['result_key']

    parsed = result['parsed']
    rv = {'xml': [result['xml']], 'parsed': result['parsed'][result_key]}
    if output_token in parsed:
        kwargs.update({input_token: parsed[output_token]})
        rest = get_pages(client, method, **kwargs)
        rv['xml'] += rest['xml']
        rv['parsed'] += rest['parsed']
    return rv


def get_pages_xml(client, method, **kwargs):
    return get_pages(client, method, **kwargs)['xml']


# noinspection PyProtectedMember
def xml_client(client):
    old_factory = client._endpoint._response_parser_factory
    client._endpoint._response_parser_factory = PassthroughParserFactory(
        old_factory)
    return client


def fetch(session):
    """
    :param session: A boto3 Session with credentials sufficient to
     run the necessary Describe* calls.
    :return: JSON data representing a network from the given account and
    region.  This data can be passed to the snapshot or query commands.
    """
    ec2 = xml_client(session.client('ec2'))
    elb = xml_client(session.client('elb'))
    elbv2 = xml_client(session.client('elbv2'))

    elbv2_elbs = get_pages(elbv2, 'describe_load_balancers', PageSize=1)
    elbv2_elb_arns = [e['LoadBalancerArn'] for e in elbv2_elbs['parsed']]
    elbv2_listeners = [(arn, get_pages(elbv2, 'describe_listeners', LoadBalancerArn=arn)) for arn in elbv2_elb_arns]
    elbv2_listener_arns = [e['ListenerArn'] for (arn, listener) in elbv2_listeners for e in listener['parsed']]
    elbv2_rules = {arn : get_results(elbv2, 'describe_rules', ListenerArn=arn) for arn in elbv2_listener_arns}
    elbv2_targetgroups = get_pages(elbv2, 'describe_target_groups', PageSize=20)
    elbv2_targetgroup_arns = [tg['TargetGroupArn'] for tg in elbv2_targetgroups['parsed']]
    elbv2_targets = {arn: get_results(elbv2, 'describe_target_health', TargetGroupArn=arn) for arn in elbv2_targetgroup_arns}
    elbv2_lbtags = {arn: get_results(elbv2, 'describe_tags', ResourceArns=[arn]) for arn in elbv2_elb_arns}
    elbv2_tgtags = {arn: get_results(elbv2, 'describe_tags', ResourceArns=[arn]) for arn in elbv2_targetgroup_arns}

    elb_results = get_pages(elb, 'describe_load_balancers', PageSize=1)
    elb_names = [e['LoadBalancerName'] for e in elb_results['parsed']]

    # XXX in the aws documentation (e.g.
    # http://docs.aws.amazon.com/cli/latest/reference/ec2/describe-nat-gateways.html)
    # it appears that the output of describe_nat_gateways,
    # describe_vpc_endpoints, and describe_vpc_peering_connections may
    # sometimes be paginated, but boto3 does not appear to support
    # pagination for them. Which is very strange, since the official
    # aws cli uses boto.
    return {
        "describe_availability_zones":
            get_results(ec2, 'describe_availability_zones'),
        "describe_instances":
            get_pages_xml(ec2, 'describe_instances'),
        "describe_internet_gateways":
            get_results(ec2, 'describe_internet_gateways'),
        "describe_nat_gateways":
            get_pages_xml(ec2, 'describe_nat_gateways'),
        "describe_network_acls":
            get_results(ec2, 'describe_network_acls'),
        "describe_network_interfaces":
            get_results(ec2, 'describe_network_interfaces'),
        "describe_prefix_lists":
            get_results(ec2, 'describe_prefix_lists'),
        "describe_regions":
            get_results(ec2, 'describe_regions'),
        "describe_route_tables":
            get_results(ec2, 'describe_route_tables'),
        "describe_security_groups":
            get_results(ec2, 'describe_security_groups'),
        "describe_subnets":
            get_results(ec2, 'describe_subnets'),
        "describe_vpc_endpoints":
            get_results(ec2, 'describe_vpc_endpoints'),
        "describe_vpc_peering_connections":
            get_results(ec2, 'describe_vpc_peering_connections'),
        "describe_vpcs":
            get_results(ec2, 'describe_vpcs'),
        "describe_load_balancers2": {
            "listeners_per_load_balancer":
                { arn: value['xml'] for (arn, value) in elbv2_listeners },
            "load_balancer_tags":
                elbv2_lbtags,
            "load_balancers":
                elbv2_elbs['xml'],
            "rules_per_listener":
                elbv2_rules,
            "target_group_tags":
                elbv2_tgtags,
            "target_groups":
                elbv2_targetgroups['xml'],
            "targets_per_target_group":
                elbv2_targets,
        },
        "describe_load_balancers": {
            "describe_load_balancers":
                elb_results['xml'],
            "describe_load_balancer_tags":
                [get_results(elb, 'describe_tags',
                             LoadBalancerNames=[elb_name])
                 for elb_name in elb_names],
            "describe_load_balancer_attributes":
                [{'name': elb_name,
                  'body': get_results(elb, 'describe_load_balancer_attributes',
                                      LoadBalancerName=elb_name)}
                 for elb_name in elb_names]
        },
    }
