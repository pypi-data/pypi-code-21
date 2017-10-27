import yaml
import rx
import logging
from enum import Enum
logger = logging.getLogger(name=__name__)




class Tags:
    undifined = '<undifined>'


def with_default(x, default=None):
    return x if x is not None else default


def add_yaml_support_enum(cls, tag):
    fmt = 'YAML support added for {cls} with tag: {tag}.'
    logger.info(fmt.format(cls=cls, tag=tag))

    def representer(dumper, data):
        return dumper.represent_scalar(tag, data.name)
    yaml.add_representer(cls, representer)

    def constructor(loader, node):
        value = loader.construct_scalar(node)
        for v in cls:
            if v.name == value:
                return v
        raise ValueError(
            "Unkown value {value} of type {cls}.".format(value=value, cls=cls))
    yaml.add_constructor(tag, constructor)


def add_yaml_support(cls, tag):
    if issubclass(cls, Enum):
        add_yaml_support_enum(cls, tag)


def notebook_logging_support():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    logger.handlers = [handler]
    logger.info('test')


def urlf(host, port, url, method="http"):
    return "{method}://{host}:{port}{url}".format(method=method, host=host, port=port, url=url)


def rx_block(o):
    return (o.suscribe_on(rx.concurrency.ThreadPoolScheduler())
            .to_blocking().first())
