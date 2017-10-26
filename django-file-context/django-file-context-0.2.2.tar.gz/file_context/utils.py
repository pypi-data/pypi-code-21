# coding: utf-8
import importlib
import logging
logger = logging.getLogger(__name__)


def load_module_member(dotted_path):
    """
    Loads a module member and returns it
    """
    if not dotted_path:
        raise ValueError('dotted path is mandatory')
    try:
        module_name, member_name = dotted_path.rsplit('.', 1)
        module = importlib.import_module(module_name)
        member = getattr(module, member_name)
        return member
    except Exception as ex:
        message = ex.message if hasattr(ex, 'message') else ''
        logger.error('error while loading member %s. error: %s', dotted_path, message, exc_info=True)
        return None


def get_model(model_name):

    """
    model_name must be app.model
    """

    try:
        from django.db.models import get_model
    except:
        from django.apps import apps
        get_model = apps.get_model

    app, model = model_name.split('.')
    if not app or not model:
        raise ValueError('model_name is must be in the format app.model')
    return get_model(app, model)
