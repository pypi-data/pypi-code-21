'''
The template for the PostgreSQL-based Database as a Service.
'''

import random
import string
import re
from urllib.parse import urlparse

import boto3
import requests
from requests.exceptions import RequestException
import dns.resolver
from clickclick import Action, fatal_error, error
from senza.aws import encrypt, list_kms_keys
from senza.utils import pystache_render

from senza.templates._helper import check_s3_bucket, get_account_alias

AVAILABILITY_ZONES = 'abc'
POSTGRES_PORT = 5432
HEALTHCHECK_PORT = 8008
BG_MON_PORT = 8080
SPILO_POSTGRES_VERSION = "10"
SPILO_IMAGE_ADDRESS = "registry.opensource.zalan.do/acid/spilo-" + SPILO_POSTGRES_VERSION
ODD_SG_GROUP_NAME_REGEX = 'Odd.*'
ZMON_SG_GROUP_NAME_REGEX = 'app-zmon'
PRICE_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"

# This template goes through 2 formatting phases. Once during the init phase and once during
# the create phase of senza. Some placeholders should be evaluated during create.
# This creates some ugly placeholder formatting, therefore some placeholders are placeholders for placeholders
# - version
# - ImageVersion
TEMPLATE = '''
# basic information for generating and executing this definition
SenzaInfo:
  StackName: spilo
  Parameters:
    - Team:
        Default: "{{team_name}}"
  Tags:
    - SpiloCluster: "{{arguments_version}}"
    - Environment: "{{environment}}"
    - TeamName: "{{arguments_team}}"

# a list of senza components to apply to the definition
SenzaComponents:

  # this basic configuration is required for the other components
  - Configuration:
      Type: Senza::StupsAutoConfiguration # auto-detect network setup
      PublicOnly: true
      AvailabilityZones:
      {{#availability_zones}}
      - "{{arguments_region}}{{k}}"
      {{/availability_zones}}

  # will create a launch configuration and auto scaling group with scaling triggers
  - AppServer:
      Type: Senza::TaupageAutoScalingGroup
      Tags:
        - Key: TeamName
          Value: "{{arguments_team}}"
      {{#use_spot_instances}}
      TerminationPolicies:
        - NewestInstance
        - Default
      {{/use_spot_instances}}
      AutoScaling:
        Minimum: {{number_of_instances}}
        Maximum: {{number_of_instances}}
        MetricType: CPU
      InstanceType: {{instance_type}}
      {{#use_spot_instances}}
      SpotPrice: {{spot_price}}
      {{/use_spot_instances}}
      {{#ebs_optimized}}
      EbsOptimized: True
      {{/ebs_optimized}}
      {{#add_replica_loadbalancer}}
      ElasticLoadBalancer:
        - PostgresReplicaLoadBalancer
      {{/add_replica_loadbalancer}}
      HealthCheckType: EC2
      SecurityGroups:
        - Fn::GetAtt:
          - SpiloMemberSG
          - GroupId
      IamRoles:
        - Ref: PostgresAccessRole
      AssociatePublicIpAddress: false # change for standalone deployment in default VPC
      TaupageConfig:
        runtime: Docker
        source: {{docker_image}}
        networking: host
        etcd_discovery_domain: "{{discovery_domain}}"
        environment:
          EIP_ALLOCATION:
            Fn::GetAtt:
            - MasterElasticIP
            - AllocationId
          SCOPE: "{{arguments_version}}"
          ETCD_DISCOVERY_DOMAIN: "{{discovery_domain}}"
          WAL_S3_BUCKET: "{{wal_s3_bucket}}"
          PGPASSWORD_SUPERUSER: "{{pgpassword_superuser}}"
          PGPASSWORD_STANDBY: "{{pgpassword_standby}}"
          BACKUP_SCHEDULE: "00 01 * * *"
          BACKUP_NUM_TO_RETAIN: 5
          {{#ldap_url}}
          LDAP_URL: {{ldap_url}}
          {{/ldap_url}}
          {{#pam_oauth2}}
          PAM_OAUTH2: {{pam_oauth2}}
          {{/pam_oauth2}}
          SPILO_CONFIGURATION: | ## https://github.com/zalando/patroni#yaml-configuration
            tags:
              clonefrom: true
              team: "{{arguments_team}}"
            postgresql:
              bin_dir: /usr/lib/postgresql/{{spilo_postgres_version}}/bin
            bootstrap:
              {{#postgresqlconf}}
              dcs:
                postgresql:
                  parameters:
                    {{{postgresqlconf}}}
              {{/postgresqlconf}}
              initdb:
                - auth-host: md5
                - auth-local: trust
              pg_hba:
                - hostnossl all all all reject
                {{#pam_oauth2}}
                - hostssl   all +zalandos all pam
                {{/pam_oauth2}}
                {{#ldap_suffix}}
                - hostssl   all +zalandos all ldap ldapserver="localhost" ldapprefix="uid=" ldapsuffix=",{{ldap_suffix}}"
                {{/ldap_suffix}}
                - hostssl   all all all md5
        root: True
        sysctl:
          vm.overcommit_memory: {{overcommit_memory}}
          vm.overcommit_ratio: 100
          vm.dirty_ratio: 8
          vm.dirty_background_ratio: 1
          vm.swappiness: 1
        {{#scalyr_account_key}}
        scalyr_account_key: {{scalyr_account_key}}
        scalyr_region: eu
        {{/scalyr_account_key}}
        {{#use_ebs}}
        volumes:
          ebs:
            /dev/sdk: "spilo_{{arguments_version}}_data"
        {{/use_ebs}}
        mounts:
          /home/postgres/pgdata:
            {{#use_ebs}}
            partition: /dev/xvdk
            {{/use_ebs}}
            {{^use_ebs}}
            partition: /dev/nvme0n1
            {{/use_ebs}}
            filesystem: {{fstype}}
            options: {{fsoptions}}
            {{#snapshot_id}}
            erase_on_boot: false
            {{/snapshot_id}}
            {{^snapshot_id}}
            erase_on_boot: true
            {{/snapshot_id}}
Resources:
  {{#use_ebs}}
  {{#availability_zones}}
  SpiloVolume{{v}}:
    Type: AWS::EC2::Volume
    Properties:
      Size: {{volume_size}}
      AvailabilityZone: "{{arguments_region}}{{k}}"
      VolumeType: {{volume_type}}
      {{#snapshot_id}}
      SnapshotId: {{snapshot_id}}
      {{/snapshot_id}}
      {{#volume_iops}}
      Iops: {{volume_iops}}
      {{/volume_iops}}
      Tags:
      - Key: Name
        Value: "spilo_{{arguments_version}}_data"
      - Key: TeamName
        Value: "{{arguments_team}}"
  {{/availability_zones}}
  {{/use_ebs}}
  MasterElasticIP:
    Type: AWS::EC2::EIP
    Properties:
      Domain: vpc
  {{#add_replica_loadbalancer}}
  PostgresReplicaRoute53Record:
    Type: AWS::Route53::RecordSet
    Properties:
      Type: CNAME
      TTL: 20
      HostedZoneName: {{hosted_zone}}
      {{#replica_dns_name}}
      Name: {{replica_dns_name}}
      {{/replica_dns_name}}
      {{^replica_dns_name}}
      Name: "{{arguments_version}}-replica.{{arguments_team}}.{{hosted_zone}}"
      {{/replica_dns_name}}
      ResourceRecords:
        - Fn::GetAtt:
           - PostgresReplicaLoadBalancer
           - DNSName
  PostgresReplicaLoadBalancer:
    Type: AWS::ElasticLoadBalancing::LoadBalancer
    Properties:
      CrossZone: true
      Tags:
        - Key: TeamName
          Value: "{{arguments_team}}"
      HealthCheck:
        HealthyThreshold: 2
        Interval: 5
        Target: HTTP:{{healthcheck_port}}/replica
        Timeout: 3
        UnhealthyThreshold: 2
      Listeners:
        - InstancePort: {{postgres_port}}
          LoadBalancerPort: {{postgres_port}}
          Protocol: TCP
      LoadBalancerName: "spilo-{{arguments_version}}-repl"
      ConnectionSettings:
        IdleTimeout: 3600
      SecurityGroups:
        - Fn::GetAtt:
          - SpiloReplicaSG
          - GroupId
      Scheme: internet-facing
      Subnets:
        Fn::FindInMap:
          - LoadBalancerSubnets
          - Ref: AWS::Region
          - Subnets
  {{/add_replica_loadbalancer}}
  PostgresRoute53Record:
    Type: AWS::Route53::RecordSet
    Properties:
      Type: CNAME
      TTL: 600
      HostedZoneName: {{hosted_zone}}
      {{#master_dns_name}}
      Name: {{master_dns_name}}
      {{/master_dns_name}}
      {{^master_dns_name}}
      Name: "{{arguments_version}}.{{arguments_team}}.{{hosted_zone}}"
      {{/master_dns_name}}
      ResourceRecords:
      - Fn::Sub:
        - "ec2-${Hostname}.${AWS::Region}.compute.amazonaws.com."
        - Hostname:
            Fn::Join:
            - "-"
            - Fn::Split:
              - "."
              - Ref: MasterElasticIP
  PostgresAccessRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
        - Effect: Allow
          Principal:
            Service: ec2.amazonaws.com
          Action: sts:AssumeRole
      Path: /
      Policies:
      - PolicyName: SpiloEC2S3KMSAccess
        PolicyDocument:
          Version: "2012-10-17"
          Statement:
          - Effect: Allow
            Action:
              - s3:ListBucket
            Resource:
              - "arn:aws:s3:::{{wal_s3_bucket}}"
              - "arn:aws:s3:::{{wal_s3_bucket}}/*"
          - Effect: Allow
            Action:
              - s3:*
            Resource:
              - "arn:aws:s3:::{{wal_s3_bucket}}/spilo/{{arguments_version}}/*"
          - Effect: Allow
            Action: ec2:CreateTags
            Resource: "*"
          - Effect: Allow
            Action: ec2:Describe*
            Resource: "*"
          - Effect: Allow
            Action: ec2:AssociateAddress
            Resource: "*"
          - Effect: Allow
            Action: ec2:AttachVolume
            Resource: "*"
          {{#kms_arn}}
          - Effect: Allow
            Action:
              - "kms:Decrypt"
              - "kms:Encrypt"
            Resource:
              - {{kms_arn}}
          {{/kms_arn}}
  {{#add_replica_loadbalancer}}
  SpiloReplicaSG:
    Type: "AWS::EC2::SecurityGroup"
    Properties:
      GroupDescription: "Security Group for the replica ELB of Spilo: {{arguments_version}}"
      SecurityGroupIngress:
        {{spilo_replica_security_group_ingress_rules_block}}
  {{/add_replica_loadbalancer}}
  SpiloMemberSG:
    Type: "AWS::EC2::SecurityGroup"
    Properties:
      GroupDescription: "Security Group for members of Spilo: {{arguments_version}}"
      SecurityGroupIngress:
        {{spilo_master_security_group_ingress_rules_block}}
        {{#kube_worker_sg_id}}
        - IpProtocol: tcp
          FromPort: {{prometheus_port}}
          ToPort: {{prometheus_port}}
          SourceSecurityGroupId: "{{kube_worker_sg_id}}" # kube-worker
        - IpProtocol: tcp
          FromPort: {{postgres_port}}
          ToPort: {{postgres_port}}
          SourceSecurityGroupId: "{{kube_worker_sg_id}}"
        - IpProtocol: tcp
          FromPort: {{healthcheck_port}}
          ToPort: {{healthcheck_port}}
          SourceSecurityGroupId: "{{kube_worker_sg_id}}"
        - IpProtocol: tcp
          FromPort: {{bg_mon_port}}
          ToPort: {{bg_mon_port}}
          SourceSecurityGroupId: "{{kube_worker_sg_id}}"
        {{/kube_worker_sg_id}}
        {{#add_replica_loadbalancer}}
        - IpProtocol: tcp
          FromPort: {{postgres_port}}
          ToPort: {{postgres_port}}
          SourceSecurityGroupId:
            Fn::GetAtt:
              - SpiloReplicaSG
              - GroupId
        - IpProtocol: tcp
          FromPort: {{healthcheck_port}}
          ToPort: {{healthcheck_port}}
          SourceSecurityGroupId:
            Fn::GetAtt:
              - SpiloReplicaSG
              - GroupId
        {{/add_replica_loadbalancer}}
        {{#zmon_sg_id}}
        - IpProtocol: tcp
          FromPort: {{prometheus_port}}
          ToPort: {{prometheus_port}}
          SourceSecurityGroupId: "{{zmon_sg_id}}" # zmon
        - IpProtocol: tcp
          FromPort: {{postgres_port}}
          ToPort: {{postgres_port}}
          SourceSecurityGroupId: "{{zmon_sg_id}}"
        - IpProtocol: tcp
          FromPort: {{healthcheck_port}}
          ToPort: {{healthcheck_port}}
          SourceSecurityGroupId: "{{zmon_sg_id}}"
        {{/zmon_sg_id}}
        {{#odd_sg_id}}
        - IpProtocol: tcp
          FromPort: 0
          ToPort: 65535
          SourceSecurityGroupId: "{{odd_sg_id}}" # odd
        {{/odd_sg_id}}
  SpiloMemberIngressMembers:
    Type: "AWS::EC2::SecurityGroupIngress"
    Properties:
      GroupId:
        Fn::GetAtt:
          - SpiloMemberSG
          - GroupId
      IpProtocol: tcp
      FromPort: 0
      ToPort: 65535
      SourceSecurityGroupId:
        Fn::GetAtt:
          - SpiloMemberSG
          - GroupId
'''


def ebs_optimized_supported(instance_type):
    # per http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSOptimized.html
    """
    >>> ebs_optimized_supported('c3.xlarge')
    True
    >>> ebs_optimized_supported('t2.micro')
    False
    """
    return instance_type in ('c1.large', 'c3.xlarge', 'c3.2xlarge', 'c3.4xlarge',
                             'c4.large', 'c4.xlarge', 'c4.2xlarge', 'c4.4xlarge', 'c4.8xlarge',
                             'd2.xlarge', 'd2.2xlarge', 'd2.4xlarge', 'd2.8xlarge',
                             'g2.2xlarge', 'i2.xlarge', 'i2.2xlarge', 'i2.4xlarge',
                             'm1.large', 'm1.xlarge', 'm2.2xlarge', 'm2.4xlarge',
                             'm3.xlarge', 'm3.2xlarge', 'r3.xlarge', 'r3.2xlarge',
                             'r3.4xlarge')


def set_default_variables(variables):
    variables.setdefault('arguments_version', '{{Arguments.version}}')
    variables.setdefault('arguments_region', '{{Arguments.region}}')
    variables.setdefault('arguments_team', '{{Arguments.Team}}')
    variables.setdefault('team_name', None)
    variables.setdefault('team_region', None)
    variables.setdefault('team_gateway_zone', None)
    # End of required variables #
    variables.setdefault('add_replica_loadbalancer', False)
    variables.setdefault('discovery_domain', None)
    variables.setdefault('master_dns_name', None)
    variables.setdefault('docker_image', get_latest_image(artifact='spilo-{}'.format(SPILO_POSTGRES_VERSION)))
    variables.setdefault('ebs_optimized', None)
    variables.setdefault('fsoptions', 'noatime,nodiratime,nobarrier')
    variables.setdefault('fstype', 'ext4')
    variables.setdefault('healthcheck_port', HEALTHCHECK_PORT)
    variables.setdefault('bg_mon_port', BG_MON_PORT)
    variables.setdefault('hosted_zone', None)
    variables.setdefault('instance_type', 'm4.large')
    variables.setdefault('number_of_instances', 3)
    variables.setdefault('ldap_url', None)
    variables.setdefault('ldap_suffix', None)
    variables.setdefault('pam_oauth2', None)
    variables.setdefault('kms_arn', None)
    variables.setdefault('odd_sg_id', None)
    variables.setdefault('pgpassword_standby', generate_random_password())
    variables.setdefault('pgpassword_superuser', generate_random_password())
    variables.setdefault('postgresqlconf', None)
    variables.setdefault('postgres_port', POSTGRES_PORT)
    variables.setdefault('prometheus_port', '9100')
    variables.setdefault('replica_dns_name', None)
    variables.setdefault('snapshot_id', None)
    variables.setdefault('use_ebs', True)
    variables.setdefault('volume_iops', None)
    variables.setdefault('volume_size', 50)
    variables.setdefault('volume_type', 'gp2')
    variables.setdefault('wal_s3_bucket', None)
    variables.setdefault('zmon_sg_id', None)
    variables.setdefault('use_spot_instances', False)
    variables.setdefault('spot_price', 0)
    variables.setdefault('environment', 'live')
    variables.setdefault('spilo_postgres_version', SPILO_POSTGRES_VERSION)
    variables.setdefault('overcommit_memory', 2)
    variables.setdefault('scalyr_account_key', None)
    variables.setdefault('kube_worker_sg_id', None)

    return variables


def gather_user_variables(variables, account_info, region):

    set_default_variables(variables)

    missing = []
    for required in ('team_name', 'team_region', 'team_gateway_zone', 'hosted_zone'):
        if not variables.get(required):
            missing.append(required)
    if len(missing) > 0:
        fatal_error("Missing values for the following variables: {0}".format(', '.join(missing)))

    # redefine the region per the user input
    if variables['team_region'] != region.Region:
        fatal_error("Current region {0} do not match the requested region {1}\n"
                    "Change the currect region with --region option or set AWS_DEFAULT_REGION variable.".
                    format(region.Region, variables['team_region']))

    variables['wal_s3_bucket'] = '{}-{}-spilo-dbaas'.format(get_account_alias(), region.Region)

    for name in ('team_gateway_zone', 'hosted_zone'):
        if variables[name][-1] != '.':
            variables[name] += '.'

    # split the ldap url into the URL and suffix (path component)
    if variables['ldap_url']:
        url = urlparse(variables['ldap_url'])
        if url.path and url.path[0] == '/':
            variables['ldap_suffix'] = url.path[1:]

    # if master DNS name is specified but not the replica one - derive the replica name from the master
    if variables['master_dns_name'] and not variables['replica_dns_name']:
        replica_dns_components = variables['master_dns_name'].split('.')
        replica_dns_components[0] += '-repl'
        variables['replica_dns_name'] = '.'.join(replica_dns_components)

    variables['add_replica_loadbalancer'] =\
        (variables['add_replica_loadbalancer'] and str(variables['add_replica_loadbalancer']).lower() == "true")

    # make sure all DNS names belong to the hosted zone
    for v in ('master_dns_name', 'replica_dns_name'):
        if variables[v] and not check_dns_name(variables[v], variables['hosted_zone'][:-1]):
            fatal_error("{0} should end with {1}".
                        format(v.replace('_', ' '), variables['hosted_zone'][:-1]))

    if variables['ldap_url'] and not variables['ldap_suffix']:
        fatal_error("LDAP URL is missing the suffix: shoud be in a format: "
                    "ldap[s]://example.com[:port]/ou=people,dc=example,dc=com")

    # pick up the proper etcd address depending on the region
    variables['discovery_domain'] = detect_etcd_discovery_domain_for_region(variables['hosted_zone'],
                                                                            region.Region)

    # get the IP addresses of the NAT gateways to acess a given ELB.
    variables['nat_gateway_addresses'] = detect_eu_team_nat_gateways(variables['team_gateway_zone'])
    variables['odd_instance_addresses'] = detect_eu_team_odd_instances(variables['team_gateway_zone'])
    variables['db_nat_gateway_addresses'] = detect_eu_team_nat_gateways(variables['hosted_zone'],
                                                                        regions=['eu-central-1'])
    generate_spilo_security_group_ingress(variables)

    if variables['postgresqlconf']:
        variables['postgresqlconf'] = generate_postgresql_configuration(variables['postgresqlconf'])

    variables['odd_sg_id'] = detect_security_group(region.Region, ODD_SG_GROUP_NAME_REGEX)
    variables['zmon_sg_id'] = detect_security_group(region.Region, ZMON_SG_GROUP_NAME_REGEX)

    if variables['volume_type'] == 'io1' and not variables['volume_iops']:
        pio_max = variables['volume_size'] * 30
        variables['volume_iops'] = str(pio_max)
    variables['ebs_optimized'] = ebs_optimized_supported(variables['instance_type'])

    if variables['instance_type'].split('.')[0] == 'i3': # no need to define volumes and AZs, mounts are different
        variables['fsoptions'] += ',discard'
        variables['use_ebs'] = False
        variables['availability_zones'] = None
        variables['snapshot_id'] = None
    else:
        if int(variables['number_of_instances']) > len(AVAILABILITY_ZONES):
            fatal_error('We do not support more instances than availability zones with EBS-backed instance types.')
        else:
            variables['availability_zones'] = [{"k": az.lower(), "v": az.upper()}
                                               for az
                                               in sorted(random.sample(AVAILABILITY_ZONES,
                                                                       int(variables['number_of_instances'])))]

    if variables['instance_type'] in ('t2.nano', 't2.micro', 't2.small'):
        variables['overcommit_memory'] = 0

    # pick up the first key with a description containing spilo
    kms_keys = [k for k in list_kms_keys(region.Region)
                if 'alias/aws/ebs' not in k['aliases'] and 'spilo' in ((k['Description']).lower())]

    if len(kms_keys) == 0:
        raise fatal_error('No KMS key is available for encrypting and decrypting. '
                          'Ensure you have at least 1 key available.')

    kms_key = kms_keys[0]
    kms_keyid = kms_key['KeyId']
    variables['kms_arn'] = kms_key['Arn']

    for key in [k for k in variables if k.startswith('pgpassword_')]:
        encrypted = encrypt(region=region.Region, key_id=kms_keyid, plaintext=variables[key], b64encode=True)
        variables[key] = 'aws:kms:{}'.format(encrypted)

    check_s3_bucket(variables['wal_s3_bucket'], region.Region)

    variables['use_spot_instances'] = (str(variables['use_spot_instances']).lower() == "true")
    if variables['use_spot_instances'] and variables['spot_price'] == 0:
        with Action("Calculating the maximum spot price for {0}..".format(variables['instance_type'])) as act:
            on_demand_price = get_on_demand_price(act, variables['team_region'], variables['instance_type'])
            if on_demand_price == 0:
                act.fatal_error("Could not get the correct on-demand price, try running without use_spot_instances")
            else:
                variables['spot_price'] = round(on_demand_price * 2, 3)

    env = variables['environment'].lower()
    if env not in ('live', 'test', 'staging'):
        fatal_error("environment should be either live, test or staging")
    variables['environment'] = env
    if env == 'live' and variables['use_spot_instances']:
        error("Spot instances are not recommended for production environment")

    return variables


def check_dns_name(name, hosted_zone):
    """
    >>> check_dns_name('foo.bar.example.com')
    False
    >>> check_dns_name('foo.bar.' + hosted_zone )
    True
    """
    return name.endswith(hosted_zone)


def generate_random_password(length=64):
    """
    >>> len(generate_random_password(61))
    61
    """
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def generate_definition(variables):
    """
    >>> variables = set_default_variables(dict())
    >>> len(generate_definition(variables)) > 300
    True
    """
    definition_yaml = pystache_render(TEMPLATE, variables)
    return definition_yaml


def generate_rules(addresses_to_allow, port):
    result = ""
    for addr in addresses_to_allow:
        if addr != addresses_to_allow[0]:
            result += '\n'+' ' * 8
        result += "- IpProtocol: tcp{delim}FromPort: {port}{delim}ToPort: {port}{delim}CidrIp: {ip}/32".\
                  format(port=port, ip=addr, delim='\n' + ' ' * 10)
    return result


def generate_spilo_security_group_ingress(variables):
    variables['spilo_master_security_group_ingress_rules_block'] =\
        variables['spilo_replica_security_group_ingress_rules_block'] = \
        generate_rules(variables['nat_gateway_addresses'] + variables['odd_instance_addresses'], POSTGRES_PORT)

    ident = '\n' + ' ' * 8
    variables['spilo_master_security_group_ingress_rules_block'] += ident + '# NAT gateways of DB account:' +\
        ident + generate_rules(variables['db_nat_gateway_addresses'], POSTGRES_PORT)


# we cannot use the JSON form {'name': value}, since pystache manges the quotes.
def generate_postgresql_configuration(postgresqlconf):
    result = ""
    options = [t.strip() for t in postgresqlconf.strip('{}').split(',')]
    for opt in options:
        if opt != options[0]:
            result += '\n' + ' ' * 20
        key, value = opt.split(':', 2)
        result += "{0}: '{1}'".format(key.strip(), value.strip())
    return result


def get_latest_image(registry_domain='registry.opensource.zalan.do', team='acid', artifact='spilo-10'):
    """
    >>> 'registry.opensource.zalan.do' in get_latest_image()
    True
    >>> get_latest_image('dont.exist.url')
    ''
    """
    try:
        r = requests.get('https://{0}/teams/{1}/artifacts/{2}/tags'.format(registry_domain, team, artifact))
        if r.ok:
            # sort the tags by creation date
            latest = None
            for entry in sorted(r.json(), key=lambda t: t['created'], reverse=True):
                tag = entry['name']
                # try to avoid snapshots if possible
                if 'SNAPSHOT' not in tag:
                    latest = tag
                    break
                latest = latest or tag
            return "{0}/{1}/{2}:{3}".format(registry_domain, team, artifact, latest)
    except:
        pass
    return ""


def detect_etcd_discovery_domain_for_region(dbaas_zone, user_region):
    """ Query DNS zone for the etcd record corresponding to a given region. """
    user_region = user_region.split('-')[1]  # leave only 'west' out of 'eu-west-1'

    route53 = boto3.client('route53')
    zones = route53.list_hosted_zones_by_name()

    for z in zones['HostedZones']:
        if z['Name'] == dbaas_zone:
            zone_id = z['Id']
            break
    else:
        fatal_error("Unable to list records for {0}: make sure you are logged into the DBaaS account".
                    format(dbaas_zone))

    paginator = route53.get_paginator('list_resource_record_sets')
    for record_set in paginator.paginate(HostedZoneId=zone_id):
        for r in record_set['ResourceRecordSets']:
            if r['Type'] == 'SRV' and r['Name'] == '_etcd._tcp.{region}.{zone}'.format(region=user_region,
                                                                                       zone=dbaas_zone):
                return "{region}.{zone}".format(region=user_region, zone=dbaas_zone[:-1])
    return None


def detect_eu_team_nat_gateways(team_zone_name, regions=None):
    """
        Detect NAT gateways. Since the complete zone is not hosted by DBaaS and
        not accessible, try to figure out individual NAT endpoints by name.
    """
    if regions is None:
        regions = ['eu-west-1', 'eu-central-1']
    resolver = dns.resolver.Resolver()
    nat_gateways = []
    for region in regions:
        for az in AVAILABILITY_ZONES:
            try:
                answer = resolver.query('nat-{region}{az}.{zone}'.
                                        format(region=region, az=az, zone=team_zone_name), 'A')
                nat_gateways.extend(str(rdata) for rdata in answer)
            except dns.resolver.NXDOMAIN:
                continue
    if not nat_gateways:
        fatal_error("Unable to detect nat gateways: make sure {0} account is set up correctly".format(team_zone_name))
    return nat_gateways


def detect_eu_team_odd_instances(team_zone_name):
    """
      Detect the odd instances by name. Same reliance on a convention as with
      the detect_eu_team_nat_gateways.
    """
    resolver = dns.resolver.Resolver()
    odd_hosts = []
    for region in ('eu-west-1', 'eu-central-1'):
        try:
            answer = resolver.query('odd-{region}.{zone}'.format(region=region, zone=team_zone_name))
            odd_hosts.extend(str(rdata) for rdata in answer)
        except dns.resolver.NXDOMAIN:
            continue

    if not odd_hosts:
        fatal_error("Unable to detect odd hosts: make sure {0} account is set up correctly".format(team_zone_name))
    return odd_hosts


def detect_security_group(region, sg_regex):
    ec2 = boto3.client('ec2', region)

    sgs = [sg for sg in ec2.describe_security_groups()['SecurityGroups'] if re.match(sg_regex, sg['GroupName'])]

    if len(sgs) == 0:
        fatal_error('Could not find security group which matches regex {}'.format(sg_regex))
    if len(sgs) > 1:
        fatal_error('More than one security group found for regex {}'.format(sg_regex))

    return sgs[0]['GroupId']


def get_on_demand_price(act, region, instance_type):
    """
        Calculate prices on demand for a given region and instance type
        Fetch the SKU of the desired on-demand instance from AWS API,
        then use the SKU to fetch the acutal price.
        XXX: the API returns a json of 45MB, takes long to parse
    """
    if region == 'eu-central-1':
        region = 'EU (Ireland)'
    elif region == 'eu-west-1':
        region = 'EU (Frankfurt)'
    else:
        act.fatal_error("Region {0} is not supported for EC2 by this template".format(region))
    try:
        prices_request = requests.get(PRICE_URL)
    except RequestException as e:
        act.fatal_error("Could not get AWS EC2 pricing API {0}: {1}".format(PRICE_URL, e))

    if prices_request.ok:
        prices = prices_request.json()
        for p in prices['products'].values():
            if (p['productFamily'] == 'Compute Instance' and
                    p['attributes'].get('location') == region and
                    p['attributes']['instanceType'] == instance_type and
                    p['attributes']['operatingSystem'] == 'Linux' and
                    p['attributes']['tenancy'] == 'Shared'):
                sku = p['sku']
                break
        else:
            act.fatal_error("Cannot fetch SKU for the price of instance {0}".format(instance_type))
        price_object = prices['terms']['OnDemand'][sku]
        if len(price_object) != 1:
            act.fatal_error("Format error: more than one entry for SKU {0}: {1}".format(sku, price_object))
        price_dimension = price_object.popitem()[1]['priceDimensions'].popitem()[1]
        if 'pricePerUnit' in price_dimension:
            instance_price = price_dimension['pricePerUnit'].get('USD', '0')
            return float(instance_price)
        else:
            act.fatal_error("Unable to find a single instance price for instance {0} sku {1}".format(
                             instance_type,
                             sku))
    else:
        act.fatal_error("Request to AWS EC2 pricing API {0} did not succeed: {1}".format(PRICE_URL, prices.status_code))
