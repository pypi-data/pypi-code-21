# -*- coding: utf-8 -*-

"""Console script for awssh."""

import click
import awssh
import subprocess
from termcolor import colored

REGION_HELP = """AWS Region, Overrides the ENV and shared config.
                 Execute 'awssh region_aliases' to see the aliases
                available VS typing full region name"""


@click.group(
    help="Helper to SSH into instances and list ips for mussh")
def main():
    """ Entry Point """
    pass


@main.command(help='List IPS for all instances and mark EIPs')
@click.option("--region", "-r",
              help="AWS Region, overrides ENV and shared config")
@click.option("--private", "-p", is_flag=True)
def ls(region=None, private=False):

    defs = {}

    if private:
        defs.update({"privateip": True})

    awsh = awssh.Awssh(region=region)
    servers = awsh.return_server_list(**defs)

    if len(servers) <= 0:
        click.echo("No ec2 instances found")
        return

    click.echo('-------------------------')
    click.echo('\t{0} = EIP'.format(colored('✓', 'green')))
    click.echo('-------------------------')

    for k, v in enumerate(servers):
        click.echo(
            '{0} [{1}]: {2}'.format(
                colored(
                    v['Eip'],
                    'green'),
                v['Ip'],
                v['Name']))


@main.command(
    help="List ip's for use with mussh. Fuzzy search enabled by default")
@click.option("--region", "-r", help=REGION_HELP)
@click.option("--exact", "-e", is_flag=True, default=False,
              help='Disable ffuzzy search and return exact Tag[Name] matches')
@click.option("--private", "-p", is_flag=True)
@click.argument('name', default='')
def ips(name, region=None, exact=False, private=False):
    defs = {}

    if private:
        defs.update({"privateip": True})

    defs.update({"exact": exact})

    awsh = awssh.Awssh(region=region)
    ips = awsh.list_ips(name, **defs)
    if len(ips) <= 0:
        return

    for ip in ips:
        click.echo(ip)


@main.command(help='SSH Into instances')
@click.option("--user", "-u", default='ec2-user', help='The SSH User')
@click.option(
    "--agent",
    "-A",
    is_flag=True,
    default=False,
    help='Forward SSH Agent')
@click.option(
    "--tty",
    "-t",
    default=False,
    is_flag=True,
    help="TTY SSH Option")
@click.option("--region", "-r", help=REGION_HELP)
@click.option("--private", "-p", is_flag=True, help='Flag to use private IPs')
@click.option("--identity", "-i", help='Identity file / SSH Private Key')
def ssh(user, tty, region=None, agent=False, private=False, identity=None):
    ''' SSH Helper '''
    awsh = awssh.Awssh(region=region)

    defs = {
        'privateip': private
    }

    servers = awsh.return_server_list(**defs)

    if len(servers) <= 0:
        click.echo("No servers available")
        return

    click.echo('-------------------------')
    click.echo('\t{0} = EIP'.format(colored('✓', 'green')))
    click.echo('-------------------------')

    for k, v in enumerate(servers):
        idx = k + 1
        if idx < 10:
            idx = ' {0}'.format(idx)

        click.echo(
            '{0}) {1} [{2}]: {3}'.format(
                idx,
                colored(
                    v['Eip'],
                    'green'),
                v['Ip'],
                v['Name']))

    prompt = 'Select a server to ssh into [1-{0}]'.format(len(servers))

    ans = click.prompt(prompt, type=int)

    if ans <= 0 or ans > len(servers):
        click.echo("Invalid selection")
        return

    if ans > 0 and ans <= len(servers):
        server = servers[(ans - 1)]

        if tty:
            tty = "-t"
        else:
            tty = ""

        # agent forwarding
        if agent:
            agent = "-A"
        else:
            agent = ''

        if identity:
            identity = '-i {0}'.format(identity)

        click.echo("---------------------")
        click.echo(
            "Server: {0}({1})".format(
                server['Name'],
                server['Ip'].strip()))
        click.echo("User: {0}".format(user))
        click.echo("---------------------")

        subprocess.call(
            'ssh {2} {3} {4} {0}@{1}'.format(
                user,
                server['Ip'].strip(),
                tty,
                agent,
                identity),
            shell=True)


@main.command(help='SSH Connect via Bastion host')
@click.option("--user", "-u", default='ec2-user', help='The ssh user')
@click.option("--region", "-r", help=REGION_HELP)
@click.option(
    "--agent",
    "-A",
    is_flag=True,
    default=False,
    help='Forward SSH Agent')
@click.option("--identity", "-i", help='Identity file / SSH Private Key')
def bssh(user, region, agent, identity=None):

    awsh = awssh.Awssh(region=region)
    servers = awsh.return_server_list()

    if len(servers) <= 0:
        click.echo("No servers available")
        return

    click.echo("-----------------------")
    click.echo('\t{0} = EIP'.format(colored('✓', 'green')))
    click.echo("-----------------------")

    for k, v in enumerate(servers):
        idx = k + 1
        if idx < 10:
            idx = ' {0}'.format(idx)

        click.echo(
            '{0}) {1} [{2}]: {3}'.format(
                idx,
                colored(
                    v['Eip'],
                    'green'),
                v['Ip'],
                v['Name']))

    prompt = 'Select the bastion host to proxy thru [1-{0}]'.format(
        len(servers))

    ans = click.prompt(prompt, type=int)

    if ans <= 0 or ans > len(servers):
        click.echo("Invalid selection")
        return

    bastion = servers[(ans - 1)]

    servers = awsh.return_server_list(**{'privateip': True})

    click.echo("-----------------------")
    click.echo('Private IPs')
    click.echo("-----------------------")

    for k, v in enumerate(servers):
        idx = k + 1
        if idx < 10:
            idx = ' {0}'.format(idx)

        click.echo(
            '{0}) {1} [{2}]: {3}'.format(
                idx,
                colored(
                    v['Eip'],
                    'green'),
                v['Ip'],
                v['Name']))

    prompt = 'Select the host to SSH into [1-{0}]'.format(len(servers))

    ans = click.prompt(prompt, type=int)

    if ans <= 0 or ans > len(servers):
        click.echo("Invalid selection")
        return

    server = servers[(ans - 1)]

    click.echo("---------------------")
    click.echo(
        "Bastion: {0}({1})".format(
            bastion['Name'],
            bastion['Ip'].strip()))
    click.echo(
        "Server: {0}({1})".format(
            server['Name'],
            server['Ip'].strip()))
    click.echo("User: {0}".format(user))
    click.echo("---------------------")

    agent_flag = ""

    if agent:
        agent_flag = "-A"

    if identity:
        identity = '-i {0}'.format(identity)

    cmd = "ssh {3} {4} -o ProxyCommand='ssh -W %h:%p {0}@{1}' {0}@{2}".format(
        user, bastion['Ip'].strip(), server['Ip'].strip(), agent_flag,
        identity)

    subprocess.call(
        cmd,
        shell=True)


@main.command(help="scp transfer files")
@click.argument("local_path", type=click.Path(exists=True))  # noqa
@click.argument("remote_path", type=click.Path(exists=False))  # noqa
@click.option("--user", "-u", default='ec2-user', help='The ssh user')
@click.option("--region", "-r", help=REGION_HELP)
def scp(local_path, remote_path, user='ec2-user', region=None):
    awsh = awssh.Awssh(region=region)

    servers = awsh.return_server_list()

    if len(servers) <= 0:
        click.echo("No servers available")
        return

    click.echo('-------------------------')
    click.echo('\t{0} = EIP'.format(colored('✓', 'green')))
    click.echo('-------------------------')

    for k, v in enumerate(servers):
        idx = k + 1
        if idx < 10:
            idx = ' {0}'.format(idx)

        click.echo(
            '{0}) {1} [{2}]: {3}'.format(
                idx,
                colored(
                    v['Eip'],
                    'green'),
                v['Ip'],
                v['Name']))

    prompt = 'Select a server to ssh into [1-{0}]'.format(len(servers))

    ans = click.prompt(prompt, type=int)

    if ans <= 0 or ans > len(servers):
        click.echo("Invalid selection")
        return

    if ans > 0 and ans <= len(servers):
        server = servers[(ans - 1)]

        click.echo("---------------------")
        click.echo(
            "Server: {0}({1})".format(
                server['Name'],
                server['Ip'].strip()))
        click.echo("User: {0}".format(user))
        click.echo('Local Path: %s' % click.format_filename(local_path))  # noqa
        click.echo('Remote Path:{0}'.format(remote_path))
        click.echo("---------------------")
        subprocess.call('scp -r {0} {2}@{3}:{1}'.format(local_path,
                                                        remote_path, user, server['Ip'].strip()), shell=True)  # noqa


@main.command(help="View region aliases")
def region_aliases():

    awsh = awssh.Awssh()
    aliases = awsh.alias_regions()

    for k, v in aliases[0].items():
        click.echo("{0} = {1}".format(k, v))


# @main.command()
# def tester():

    # assh = awssh.Awssh(region='uw2')
    # print(awssh.Awssh.get_region())


if __name__ == "__main__":
    main()
