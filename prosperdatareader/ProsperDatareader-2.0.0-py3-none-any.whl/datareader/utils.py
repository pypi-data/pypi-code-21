"""datareader.utils.py: tools for fetching stock news"""
from os import path
import warnings

NLTK_IMPORT = True
try:
    from nltk import download
    import nltk.sentiment as sentiment
except ImportError: #pragma: no cover
    NLTK_IMPORT = False
import pandas as pd

import prosper.datareader.config as config
import prosper.datareader.exceptions as exceptions

HERE = path.abspath(path.dirname(__file__))
_TESTMODE = False

__all__ = ('vader_sentiment')

INSTALLED_PACKAGES = []
def _validate_install(
        package_name,
        logger=config.LOGGER
):
    """make sure required NLTK lexicon is available

    Note:
        Skips NLTK GUI downloader.  Please see RHEL for full lexicon list

    Args:
        package_name (str): name of package on nltk.download()
        logger (:obj:`logging.logger`, optional): logging handle

    Raises:
        (:obj:`exceptions.UtilsNLTKDownloadFailed`)

    """
    if not NLTK_IMPORT:
        raise ImportError('Please use `prosperdatareader[nltk]` import')

    if package_name in INSTALLED_PACKAGES:
        if _TESTMODE:
            warnings.warn(
                'Package already installed',
                exceptions.DatareaderWarning
            )
        logger.info('Package already installed: %s', package_name)
        return

    logger.info('Installing package: %s', package_name)
    install_status = download(package_name)

    if not install_status:
        raise exceptions.UtilsNLTKDownloadFailed(
            'Unable to install: {}'.format(package_name))

    INSTALLED_PACKAGES.append(package_name)

def _get_analyzer():
    """fetch analyzer for grading strings

    Returns:
        (:obj:`nltk.sentiment.vader.SentimentIntensityAnalyzer`)

    """
    if 'vader_lexicon' not in INSTALLED_PACKAGES:
        if _TESTMODE:
            warnings.warn(
                'Package missing',
                exceptions.DatareaderWarning
            )
        _validate_install('vader_lexicon')

    return sentiment.vader.SentimentIntensityAnalyzer()

COLUMN_NAMES = ['neu', 'pos', 'compound', 'neg']
def map_vader_sentiment(
        string_series,
        column_names=COLUMN_NAMES
):
    """apply vader sentiment to an entire column and update the original source

    Args:
        string_series (:obj:`pandas.Series`): column to grade strings from
        column_names (:obj:`list`, optional): column names for vader results
            ['neu', 'pos', 'compound', 'neg']
    Returns:
        (:obj:`pandas.DataFrame`) updated series + vader-sentiments

    """
    analyzer = _get_analyzer()
    if len(column_names) != 4:
        raise exceptions.VaderClassificationException()
    def map_func(grade_str):
        """actual map function that does the heavy lifting

        Args:
            grade_str (str): string to be scored

        Returns:
            (:obj:`list`): original str + polarity scores ('neu', 'pos', 'compound', 'neg')

        """
        row = []
        row.append(grade_str)
        grades = analyzer.polarity_scores(grade_str)
        row.extend([
            grades['neu'],
            grades['pos'],
            grades['compound'],
            grades['neg']
        ])
        return row

    source_col = string_series.name
    columns = [source_col]
    columns.extend(column_names)

    new_df = pd.DataFrame(
        list(map(map_func, string_series)),
        columns=columns
    )

    return new_df

################################################################################

def vader_sentiment(
        full_dataframe,
        grading_column_name,
        vader_columns=COLUMN_NAMES,
        logger=config.LOGGER
):
    """apply vader_sentiment analysis to dataframe

    Args:
        full_dataframe (:obj:`pandas.DataFrame`): parent dataframe to apply analysis to
        grading_column_name (str): column with the data to grade
        vader_columns (:obj:`list`. optional): names to map vader results to ['neu', 'pos', 'compound', 'neg']
        logger (:obj:`logging.logger`, optional): logging handle

    Returns;
        (:obj:`pandas.DataFrame`): updated dataframe with vader sentiment

    """
    logger.info('applying vader sentiment analysis to `%s`', grading_column_name)

    logger.info('--applying vader_lexicon')
    vader_df = map_vader_sentiment(
        full_dataframe[grading_column_name],
        column_names=vader_columns
    )

    logger.info('--merging results into original dataframe')
    joined_df = full_dataframe.merge(
        vader_df,
        how='left',
        on=grading_column_name
    )

    return joined_df
