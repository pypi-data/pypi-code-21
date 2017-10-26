import tensorflow as tf


def device_name(device_type, device_id):
    return '/{t}:{i}'.format(t=device_type, i=device_id)
