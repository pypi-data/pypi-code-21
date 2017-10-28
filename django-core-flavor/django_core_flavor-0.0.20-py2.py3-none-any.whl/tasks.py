import json

from celery import current_app
from rest_framework.utils import encoders

from .utils import get_elastic_client


@current_app.task()
def elastic_index(meta, data):
    client = get_elastic_client(meta.app_label)

    return getattr(client, meta.model_name).idx(
        data['id'],
        json.dumps(data, cls=encoders.JSONEncoder)
    )
