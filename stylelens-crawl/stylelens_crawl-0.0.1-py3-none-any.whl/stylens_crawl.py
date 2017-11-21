import stylelens_product
import os
import json
import logging

from stylelens_crawl import BASE_DIR
from scrapy.crawler import CrawlerProcess
from stylelens_crawl.services.DeBow import DeBow
from stylelens_crawl.services.DoubleSixGirls import DoubleSixGirls


class StylensCrawler(object):
    def __init__(self, service_name):
        self.service_name = service_name
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.DEBUG)
        self.process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'FEED_FORMAT': 'json',
            'FEED_EXPORT_ENCODING': 'UTF-8',
            'FEED_URI': 'out.json',
            'LOG_LEVEL': 'INFO'
        })
        self.api_instance = stylelens_product.ProductApi()

        if os.path.exists(os.path.join(BASE_DIR, 'out.json')):
            os.remove(os.path.join(BASE_DIR, 'out.json'))

    def start(self):

        if self.service_name == 'HC0001':
            self.process.crawl(DoubleSixGirls)
        elif self.service_name == 'HC0002':
            self.process.crawl(DeBow)
        else:
            return False

        self.process.start()
        print('############################### Ended the finding product information.')
        self.save()
        return True

    def save(self):
        inserted_data = {}
        with open(os.path.join(BASE_DIR, 'out.json'), 'r') as file:
            raw_data = json.loads(file.read())
            for data in raw_data:
                if 'is_exist' not in data:
                    result = self.api_instance.add_product(data)
                    inserted_data[data['product_no']] = result.data.product_id
                    self.logger.debug(result)

            for data in raw_data:
                if 'is_exist' in data:
                    try:
                        result = self.api_instance.get_product_by_id(inserted_data[data['product_no']])
                        raw_data = result.data
                        raw_data.tags.extend(data['tags'])
                        modify_product = self.api_instance.update_product(raw_data)
                        self.logger.info(modify_product)
                    except Exception as ex:
                        self.logger.error(ex)
                        self.logger.debug('에러 %s' %data['product_no'])
                        self.logger.debug(data)

