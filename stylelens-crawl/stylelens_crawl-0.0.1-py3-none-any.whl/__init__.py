import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
__version__ = '0.0.1'


from stylelens_crawl.services import DeBow, DoubleSixGirls
