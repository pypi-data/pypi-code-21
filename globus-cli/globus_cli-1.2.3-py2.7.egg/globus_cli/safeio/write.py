import errno
import click


def safeprint(message, write_to_stderr=False, newline=True):
    """
    Wrapper around click.echo used to encapsulate its functionality.
    Also protects against EPIPE during click.echo calls, as this can happen
    normally in piped commands when the consumer closes before the producer.
    """
    try:
        click.echo(message, nl=newline, err=write_to_stderr)
    except IOError as err:
        if err.errno is errno.EPIPE:
            pass
        else:
            raise
