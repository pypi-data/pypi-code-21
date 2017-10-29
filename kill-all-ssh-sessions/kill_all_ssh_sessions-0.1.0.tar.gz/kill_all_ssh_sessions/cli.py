import click, os, subprocess


@click.command()
def main():
    """This tool kills all the running ssh sessions."""
    click.echo('Killing all the ssh sessions')

    os.system('ps ax | grep ssh | grep @ | grep -v grep | awk \"{print $1}\"')
    try:
        print subprocess.check_output("kill $(ps ax | grep ssh | grep @ | grep -v grep | awk '{print $1}')", shell=True)
    except subprocess.CalledProcessError as e:
        print e.output
    os.system('ps ax | grep ssh | grep @ | grep -v grep | awk \"{print $1}\"')
