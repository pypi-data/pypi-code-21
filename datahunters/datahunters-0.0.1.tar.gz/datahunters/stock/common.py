"""Base api class.
"""

import abc


class StockImage(object):
  """Class for a single stock image object.
  """
  img_id = ""
  title = ""
  description = ""
  owner = None
  created_date = ""
  full_url = ""
  normal_url = ""
  link = ""


class StockImageAPIBase(object):
  """Base class for stock image apis.
  """
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def search_imgs(self, keywords):
    """Search images using keywords.

    Args:
      keywords: descriptions of the topic.
      num: number of images to return.

    Returns:
      generator for continuously fetching images until None.
    """
    pass

  @abc.abstractmethod
  def get_imgs(self, num=-1):
    """Fetch images from the whole collection.

    Ordered by latest.

    Args:
      num: number of images to return.

    Returns:
       generator for continuously fetching images until None.
    """
    pass