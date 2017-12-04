import click
from tensorci import log, auth_required
from tensorci.utils.api import api, ApiException


@click.command()
@click.option('--prediction', '-p', help='prediction model belongs to')
def model(prediction):
  auth_required()

  # TODO: create config_file module that pulls from .tensorci.yml
  prediction = prediction or config_file.prediction

  payload = {'prediction': prediction}

  try:
    model = api.get('/prediction/model', payload=payload)
  except ApiException as e:
    log(e.message)
    return

  # TODO: add an arg to specify where to save the model and log where it was saved.
  log('Successfully pulled trained model.')