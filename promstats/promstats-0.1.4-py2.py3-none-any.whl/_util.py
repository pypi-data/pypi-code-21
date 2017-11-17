import logging


logger = logging.getLogger(__name__)


def maybe_labels(metric_wrapper_or_metric, tags):
    """Bind labels to metric, if these exist.

    :param metric_wrapper_or_metric
        (prometheus_client.core._MetricWrapper|object): A metric instance,
            or metric wrapper.
    """
    if tags:
        metric = metric_wrapper_or_metric.labels(**tags_to_labels(tags=tags))
    else:
        metric = metric_wrapper_or_metric
    return metric


def tags_to_labels(tags):
    """Parse tags into Prometheus labels."""
    labels = {}
    for tag_item in tags:
        if ':' not in tag_item:
            logger.warning('Your tag %s '
                           'is not in proper format, skipping it. '
                           'It should be a semicolon-delimited string, '
                           'representing a key-value pair.', tag_item)
        else:
            tag_name, tag_value = tag_item.split(':', 1)
            labels[tag_name] = tag_value
    return labels
