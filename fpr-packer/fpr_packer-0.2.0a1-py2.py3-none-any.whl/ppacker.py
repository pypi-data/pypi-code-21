import click


class Packer():
    def __init__(self, paker_dir="./packer"):
        self.paker_dir = paker_dir

    @click.command('Packer images builder')
    @click.option('-d', '--debug', is_flag=True, help='log packer build')
    @click.option('-t', '--trace', is_flag=True, help='echo packer command (don\'t execute it)')
    @click.option('-o', '--only', type=click.Choice(['aws', 'docker']), help='use only one builder')
    def build(debug, only, trace):
        pass
