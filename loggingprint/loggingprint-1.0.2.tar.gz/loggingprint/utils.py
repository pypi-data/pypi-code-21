import logging
import logging.handlers

def loggingprint(*params):
    text = ''

    for param in params:
        if isinstance(param, basestring):
            text += param + ' '
        elif isinstance(param, list):
            text += (' '.join(param))
            text += ' '
    text = text.strip()

    logging.info(text)