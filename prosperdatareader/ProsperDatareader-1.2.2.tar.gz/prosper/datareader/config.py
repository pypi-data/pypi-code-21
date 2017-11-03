import prosper.common.prosper_logging as p_logging

LOGGER = p_logging.DEFAULT_LOGGER

def _list_to_str(ticker_list):
    """parses/joins ticker list

    Args:
        ticker_list (:obj:`list` or str): ticker(s) to parse

    Returns:
        (str): list of tickers

    """
    if isinstance(ticker_list, str):
        return ticker_list.upper()
    elif isinstance(ticker_list, list):
        return ','.join(ticker_list).upper()
    else:
        raise TypeError
