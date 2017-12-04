import click
from utils.auth import authed

# aliasing this
log = click.echo


# TODO: Get this working as a decorator in conjunction with other @click-based decorators
def auth_required(msg=None):
  if not authed():
    err_msg = msg or "You must be logged in to perfom that action.\n" \
                     "Use 'tensorci login' if you already have an account or visit " \
                     "https://tensorci.com to create a new account."

    log(err_msg)
    exit(1)