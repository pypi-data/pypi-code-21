"""exceptions.py: collection of exceptions for Datareader libraries"""

class DatareaderException(Exception):
    """base class for Datareader exceptions"""
    pass
class DatareaderWarning(UserWarning):
    """base class for Datareader warnings"""
    pass
class PaginationWarning(DatareaderWarning):
    """hard limit reached for recursive page diving"""
    pass
class UnsupportedSource(DatareaderException):
    """unsupported source requested (CYA)"""
    pass
class InvalidEnum(DatareaderException):
    """unsupported enum selection"""
    pass

###########
## Utils ##
###########
class UtilsNLTKDownloadFailed(DatareaderException):
    """Unable to download lexicon from NLTK corpus"""
    pass
class VaderClassificationException(DatareaderException):
    """Invalid options for mapping vader->pandas"""
    pass

############
## Stocks ##
############
class StocksException(DatareaderException):
    """base class for Datareader.stocks"""
    pass
class StocksPricesException(StocksException):
    """base class for Datareader.stocks.prices"""
    pass
class StocksNewsException(StocksException):
    """base class for Datareader.stocks.prices"""
    pass

###########
## Coins ##
###########
class CoinsException(DatareaderException):
    """base class for Datareader.coins"""
    pass
class SymbolNotSupported(CoinsException):
    """symbol not supported by API source"""
    pass
class TickerNotFound(CoinsException):
    """unable to find more information about requested ticker"""
    pass
