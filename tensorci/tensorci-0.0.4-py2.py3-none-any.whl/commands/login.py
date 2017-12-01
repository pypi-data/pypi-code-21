import click
from tensorci import log
from tensorci.utils import auth
from tensorci.utils.api import api, ApiException
from tensorci.definitions import auth_header_name


@click.command()
@click.option('--email', '-e')
@click.option('--password', '-p')
def login(email, password):
  """
  Log in as a TensorCI user. Request responds with api token that can be used for
  future authed requests to TensorCI API. Email and API token are stored in netrc file.

  :param email: str (required)
  :param password: str (required)
  :return: None
  """
  log('Enter your TensorCI credentials:')

  email = (email or click.prompt('Email')).strip()

  if not email:
    log('Email is required.')
    return

  pw = (password or click.prompt('Password', hide_input=True)).strip()

  if not pw:
    log('Password is required.')
    return

  payload = {'email': email, 'password': pw}

  try:
    resp, headers = api.post('/user/login', payload=payload, return_headers=True)
  except ApiException:
    log('Authentication failed.')
    return

  user_token = headers.get(auth_header_name)

  auth.create(email=email, password=user_token)

  log('Logged in as {}'.format(email))