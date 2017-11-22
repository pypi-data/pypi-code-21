import logging
import logging.handlers

def loggingprint(*params):

    try:
        text = ''

        for param in params:
            if isinstance(param, basestring):
                text += param + ' '
            elif isinstance(param, list):

                # for list_item in param:
                #     if isinstance(list_item, basestring):
                #         text += list_item + ' '
                #     elif isinstance(list_item, dict):
                #         text += list_item + ' '

                text += (' '.join(str(param)))
                text += ' '

        text = text.strip()

        logging.info(text)
    except Exception as e:
        logging.info('Error when logging')

