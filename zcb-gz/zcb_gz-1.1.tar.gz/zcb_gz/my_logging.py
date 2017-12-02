"""."""
import json
import logging
import os
import logging.config


def setup_logging(
        default_path='logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'):
    """Setup logging configuration."""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    # path = os.path.dirname(os.path.abspath(__file__)) + path
    print(path)
    print('是否找到日志配置文件,%s' % os.path.exists(path))
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
