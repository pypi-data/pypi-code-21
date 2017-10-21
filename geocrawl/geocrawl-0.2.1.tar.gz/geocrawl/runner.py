from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from geocrawl.spiders.geo_spider import (
    GeocachingSpider,
    ShortGeocachingSpider,
    ShortSouvenirGeocachingSpider,
    SouvenirGeocachingSpider
)


def print_item(item, response, spider):
    print(item)


def print_item_title(item, response, spider):
    print(item['title'])


def return_item_title(item, response, spider):
    return item['title']


def get_all(**kwargs):
    process = CrawlerProcess(get_project_settings())
    process.crawl(GeocachingSpider, **kwargs)
    process.start()


def get_short_caches(**kwargs):
    process = CrawlerProcess(get_project_settings())
    process.crawl(ShortGeocachingSpider, **kwargs)
    process.start()


def get_short_souvenirs(**kwargs):
    process = CrawlerProcess(get_project_settings())
    process.crawl(ShortSouvenirGeocachingSpider, **kwargs)
    process.start()


def get_souvenirs(**kwargs):
    process = CrawlerProcess(get_project_settings())
    process.crawl(SouvenirGeocachingSpider, **kwargs)
    process.start()


if __name__ == '__main__':
    # get_all(on_item_scraped=print_item_title)
    # get_short_caches(on_item_scraped=print_item_title)
    # get_short_souvenirs(on_item_scraped=print_item_title)
    get_souvenirs(on_item_scraped=print_item_title)
