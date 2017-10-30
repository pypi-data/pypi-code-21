import click


@click.group()
def run():
    pass


@click.command()
def start():
    """ start task database web service """
    from .deamon import DeamonService
    DeamonService.start()
    # input("Press any key to exit\n")


run.add_command(start)
