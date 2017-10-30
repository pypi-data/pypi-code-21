import click

from explorer import Explorer, Device

class Config(object):
    def __init__(self):
        self.device = None
        self.broadcast_address = None

config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--broadcast', default='192.168.1.255')
@config
def cli(config, broadcast):
    config.broadcast_address = broadcast

@cli.command()
@config
def list(config):
    devices = Explorer().discover(config.broadcast_address)

    for device in devices:
        print "{} {} {}".format(device.name, device.ip, device.sn)

@cli.group()
@click.argument('sn')
@click.option('--ip')
@config
def device(config, sn, ip):
    if ip:
        data = {'name': 'NOT_DISCOVERED', 'sn': sn, 'sak': ''}
        config.device = Device(data, ip)
    else:
        devices = Explorer().discover(config.broadcast_address)

        for device in devices:
            if device.sn == sn:
                config.device = device

@device.command()
@config
def status(config):
    status_info = Explorer().status(config.device)

    switch = 'On' if status_info['switch'][0] == 1 else 'Off'
    watt = status_info['watt'][0]

    click.echo('%s %s W' % (switch, watt))

@device.command()
@config
def on(config):
    Explorer().switch(config.device, 'on')

@device.command()
@config
def off(config):
    Explorer().switch(config.device, 'off')

@device.command()
@config
@click.argument('name', required=False)
def name(config, name):
    if name:
        Explorer().set_name(config.device, name)
    else:
        click.echo(config.device.name)

@device.command()
@config
def time(config):
    click.echo(config.device.time())

@device.command()
@config
@click.argument('datetime', required=False)
def timer(config, datetime):
    if datetime:
        click.echo(config.device.set_timer(datetime))
    else:
        click.echo(config.device.timer())

@device.command()
@config
def rules(config):
    config.device.rules()

@device.group()
@config
def rule(config):
    pass

@rule.command()
@config
@click.argument('time')
@click.argument('state')
def add(config, time, state):
    config.device.add_rule(time, state)

@rule.command()
@config
@click.argument('rule_id')
def delete(config, rule_id):
    config.device.delete_rule(rule_id)
