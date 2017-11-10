# -*- coding: utf-8 -*-

import sys
import time
import click
from functools import reduce
from ssmrun import __version__
from ssmrun.ssm import Ssm


sys.tracebacklimit = 0

lpad = 13
lfill = '%13s'



@click.command()
@click.argument('target')
@click.argument('command')
@click.option('-s', '--show-stats', is_flag=True)
@click.option('-o', '--show-output', is_flag=True, default=True )
@click.option('-A', '--target-asg', is_flag=True)
@click.option('-S', '--target-stack', is_flag=True)
@click.option('-k', '--target-key', default='Name', help='Target tag key (default: Name)')
@click.option('-c', '--comment', default='ssmrun cli', help='Command invocation comment')
@click.option('-i', '--interval', default=1.0, help='Check interval (default: 1.0s)')
@click.option('-p', '--profile', default=None, help='AWS profile')
@click.option('-r', '--region', default=None, help='AWS region')
def cmd(target, command, show_stats, show_output, target_asg, target_stack, target_key, comment, interval, profile, region):
    """Send SSM AWS-RunShellScript to target, quick emulation of virtual SSH interface"""
    # Parse parameters for the SSM Command
    ssm_document = "AWS-RunShellScript"
    ssm_params = {"commands": [command]}

    # Shortcuts for targeting auto scaling groups and CloudFormation Stacks
    if target_asg:
        target_key = 'aws:autoscaling:groupName'
    if target_stack:
        target_key = 'aws:cloudformation:stack-name'

    ssm = Ssm(profile=profile, region=region)
    cmd = ssm.send_command_to_targets(
        document=ssm_document, key=target_key, value=target,
        comment=comment, parameters=ssm_params)
    #click.echo('==> ' + ssm.command_url(cmd['CommandId']))

    while True:
        time.sleep(interval)
        out = ssm.list_commands(CommandId=cmd['CommandId'])
        # Print final results when done
        if out[0]['Status'] not in ['Pending', 'InProgress']:
            if out[0]['TargetCount'] == out[0]['CompletedCount']:
                command_stats(out[0])
                if show_stats or show_output:
                    res = ssm.list_command_invocations(
                        cmd['CommandId'], Details=True)
                    if len(res) != 0:
                        click.echo()
                        print_command_output_per_instance(res, show_output)
                break
        # Print progress
        click.echo(lfill % ('[' + out[0]['Status'] + '] ') +
                   'Targets: ' + str(out[0]['TargetCount']) +
                   ' Completed: ' + str(out[0]['CompletedCount']) +
                   ' Errors: ' + str(out[0]['ErrorCount'])
                   )
        


@click.command()
@click.argument('ssm-document')
@click.argument('target')
@click.option('-P', '--parameter', default=None, multiple=True, help='Pass one or more params (ex: -P p1="v1" -P p2="v2")')
@click.option('-s', '--show-stats', is_flag=True)
@click.option('-o', '--show-output', is_flag=True)
@click.option('-A', '--target-asg', is_flag=True)
@click.option('-S', '--target-stack', is_flag=True)
@click.option('-k', '--target-key', default='Name', help='Target tag key (default: Name)')
@click.option('-c', '--comment', default='ssmrun cli', help='Command invocation comment')
@click.option('-i', '--interval', default=1.0, help='Check interval (default: 1.0s)')
@click.option('-p', '--profile', default=None, help='AWS profile')
@click.option('-r', '--region', default=None, help='AWS region')
def run(ssm_document, target, parameter, show_stats, show_output, target_asg, target_stack, target_key, comment, interval, profile, region):
    """Send SSM command to target"""
    # Parse parameters for the SSM Command
    ssm_params = {}
    if parameter:
        for p in parameter:
            k, v = p.split('=', 1)
            ssm_params[k] = [v]

    # Shortcuts for targeting auto scaling groups and CloudFormation Stacks
    if target_asg:
        target_key = 'aws:autoscaling:groupName'
    if target_stack:
        target_key = 'aws:cloudformation:stack-name'

    ssm = Ssm(profile=profile, region=region)
    cmd = ssm.send_command_to_targets(
        document=ssm_document, key=target_key, value=target,
        comment=comment, parameters=ssm_params)
    click.echo('==> ' + ssm.command_url(cmd['CommandId']))

    while True:
        time.sleep(interval)
        out = ssm.list_commands(CommandId=cmd['CommandId'])
        # Print final results when done
        if out[0]['Status'] not in ['Pending', 'InProgress']:
            if out[0]['TargetCount'] == out[0]['CompletedCount']:
                command_stats(out[0])
                if show_stats or show_output:
                    res = ssm.list_command_invocations(
                        cmd['CommandId'], Details=True)
                    if len(res) != 0:
                        click.echo()
                        print_command_output_per_instance(res, show_output)
                break
        # Print progress
        click.echo(lfill % ('[' + out[0]['Status'] + '] ') +
                   'Targets: ' + str(out[0]['TargetCount']) +
                   ' Completed: ' + str(out[0]['CompletedCount']) +
                   ' Errors: ' + str(out[0]['ErrorCount'])
                   )


@click.command()
@click.argument('command-id')
@click.option('-i', '--instanceId', default=None, help='Filter on instance id')
@click.option('-s', '--show-stats', is_flag=True)
@click.option('-o', '--show-output', is_flag=True)
@click.option('-p', '--profile', default=None, help='AWS profile')
@click.option('-r', '--region', default=None, help='AWS region')
def show(command_id, instanceid, show_stats, show_output, profile, region):
    """Get status/output of command invocation"""
    ssm = Ssm(profile=profile, region=region)
    out = ssm.list_commands(CommandId=command_id, InstanceId=instanceid)
    url = ssm.command_url(command_id)
    command_stats(out[0], url)

    if show_stats or show_output:
        res = ssm.list_command_invocations(
            command_id, instanceid, Details=True)
        if len(res) != 0:
            click.echo()
            print_command_output_per_instance(res, show_output)


@click.command()
@click.option('-l', '--long-list', is_flag=True, help='Detailed list')
@click.option('-o', '--owner', is_flag=True, help='Show owner')
@click.option('-P', '--platform', is_flag=True, help='Show platform types')
@click.option('-d', '--doc-version', is_flag=True, help='Show document version')
@click.option('-t', '--doc-type', is_flag=True, help='Show document type')
@click.option('-s', '--schema', is_flag=True, help='Show schema version')
@click.option('-p', '--profile', default=None, help='AWS profile')
@click.option('-r', '--region', default=None, help='AWS region')
@click.pass_context
def docs(ctx, long_list, owner, platform, doc_version, doc_type, schema, profile, region):
    """List SSM docutments"""
    ssm = Ssm(profile=profile, region=region)
    docs = ssm.list_documents()
    param_map = {
        'owner': 'Owner',
        'platform': 'PlatformTypes',
        'doc_version': 'DocumentVersion',
        'doc_type': 'DocumentType',
        'schema': 'SchemaVersion'
    }
    click.echo('total ' + str(len(docs)))
    # Map flag params to boto3 SSM list_documents() response
    output = []
    for d in docs:
        doc_info = [d['Name']]
        for k, v in param_map.items():
            # If flag param is set output the response value
            if ctx.params[k] or long_list:
                if v == 'PlatformTypes':
                    # Take first char from each element in the list (ex: WL)
                    doc_info.append(''.join(map(lambda x: x[0], d[v])))
                else:
                    doc_info.append(d[v])
        output.append(doc_info)

    # Find the longest N index across doc_info lists in output
    # Use the generated list for text padding the output
    pad = [reduce(lambda a, b: a if (len(a) > len(b)) else b, x)
           for x in zip(*output)]
    for d in output:
        for i in d:
            click.echo('%s ' % i.ljust(len(pad[d.index(i)])), nl=False)
        click.echo()


@click.command()
@click.argument('ssm-document')
@click.option('-V', '--document-version', default=None, help='Document Version')
@click.option('-p', '--profile', default=None, help='AWS profile')
@click.option('-r', '--region', default=None, help='AWS region')
def get(ssm_document, document_version, profile, region):
    """Get SSM document"""
    ssm = Ssm(profile=profile, region=region)
    doc = ssm.get_document(ssm_docutment, document_version)
    doc_info = doc['Name']
    if 'DocumentVersion' in doc:
        doc_info += ' v' + doc['DocumentVersion']
    if 'DocumentType' in doc:
        doc_info += ' ' + doc['DocumentType']
    click.echo(doc_info)
    click.echo(doc['Content'])


@click.command()
@click.option('-n', '--num-invocations', default=5, help='Number of invocations (defailt: 5)')
@click.option('-s', '--show-stats', is_flag=True)
@click.option('-p', '--profile', default=None, help='AWS profile')
@click.option('-r', '--region', default=None, help='AWS region')
def ls(num_invocations, show_stats, profile, region):
    """List SSM command invocations"""
    ssm = Ssm(profile=profile, region=region)
    invocations = ssm.list_commands()
    for i in invocations[:num_invocations]:
        url = ssm.command_url(i['CommandId'])

        command_stats(i, url)
        if show_stats:
            res = ssm.list_command_invocations(
                i['CommandId'], Details=True)
            if len(res) != 0:
                click.echo()
                print_command_output_per_instance(res)
                click.echo()


def command_stats(invocation, invocation_url=None):
    """Print results from ssm.list_commands()"""
    if invocation_url:
        click.echo('==> ' + invocation_url)

    i = invocation
    click.echo(lfill % ('[' + i['Status'] + '] ') + i['CommandId'])
    click.echo(' ' * lpad + 'Requested: '.ljust(lpad) +
               str(i['RequestedDateTime'].replace(microsecond=0)))
    click.echo(' ' * lpad + 'Docutment: '.ljust(lpad) + i['DocumentName'])
    if len(i['Parameters']) > 0:
        click.echo(' ' * lpad + 'Paramters: '.ljust(lpad))
        for k, v in i['Parameters'].items():
            click.echo(' ' * lpad * 2 + '- ' + k + '="' + v[0] + '"')
    if len(i['InstanceIds']) > 0:
        click.echo(' ' * lpad + 'InstanceIds: '.ljust(lpad) +
                   str(','.join(i['InstanceIds'])))
    if len(i['Targets']) > 0:
        click.echo(' ' * lpad + 'Target: '.ljust(lpad) +
                   i['Targets'][0]['Key'] + ' - ' + i['Targets'][0]['Values'][0])
    click.echo(' ' * lpad + 'Stats: '.ljust(lpad) + 'Targets: ' + str(i['TargetCount']) +
               ' Completed: ' + str(i['CompletedCount']) +
               ' Errors: ' + str(i['ErrorCount']))


def print_command_output_per_instance(invocations, show_output=False):
    """Print results from ssm.list_command_invocations()"""
    for i in invocations:
        click.echo(
            ' ' * lpad + ' '.join(['***', i['Status'], i['InstanceId'], i['InstanceName']]))
        if show_output:
            for cp in i['CommandPlugins']:
                click.echo(cp['Output'])


@click.group()
@click.version_option(version=__version__)
def main(args=None):
    """Utilities for AWS EC2 SSM

       \b
       ssm --help
       ssm <command> --help
    """

main.add_command(docs)
main.add_command(get)
main.add_command(ls)
main.add_command(show)
main.add_command(run)
main.add_command(cmd)

if __name__ == "__main__":
    main()
