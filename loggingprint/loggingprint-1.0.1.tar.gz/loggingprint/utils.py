import logging
import logging.handlers

def loggingprint(*params):
    text = ''

    for param in params:
        text += param + ' '
    text = text.strip()

    logging.info(text)