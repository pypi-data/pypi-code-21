from rumetr import Rumetr
from rumetr import exceptions
import scrapy


class UploadPipeline(object):
    _client = None

    def process_item(self, item, spider):
        self.spider = spider
        self.item = item

        self.add_complex_if_required()
        self.add_house_if_required()
        self.update_appt()

    def add_complex_if_required(self):
        if not self.c.complex_exists(self.item['complex_id']):
            complex = dict(
                external_id=self.item['complex_id'],
                name=self.item['complex_name'],
                url=self.item.get('complex_url'),
            )
            if self.item.get('addr') is not None and len(self.item['addr']):
                complex['address'] = {
                    'value': self.item['addr'],
                }

            self.c.add_complex(**complex)

    def add_house_if_required(self):
        if not self.c.house_exists(self.item['complex_id'], self.item['house_id']):
            self.c.add_house(
                complex=self.item['complex_id'],
                external_id=self.item['house_id'],
                name=self.item['house_name'],
                url=self.item.get('house_url'),
            )

    def update_appt(self):
        appt = dict(
            complex=self.item['complex_id'],
            house=self.item['house_id'],
            floor=self.item['floor'],
            room_count=self.item['room_count'],
            square=self.item['square'],
            price=self.item['price'],
            is_studio=self.item['is_studio'],
            plan_url=self.item.get('plan_url'),
        )

        try:
            self.c.update_appt(id=self.item['id'], **appt)
        except exceptions.Rumetr404Exception:
            self.c.add_appt(external_id=self.item['id'], **appt)

    @property
    def c(self):
        """
        Caching client for not repeapting checks
        """
        if self._client is None:
            self._parse_settings()
            self._client = Rumetr(**self.settings)
        return self._client

    def _parse_settings(self):
        if hasattr(self, 'settings'):  # parse setting only one time
            return

        self.settings = {
            'auth_key': self._check_required_setting('RUMETR_TOKEN'),
            'developer': self._check_required_setting('RUMETR_DEVELOPER'),
        }
        self.settings.update(self._non_required_settings('RUMETR_API_HOST'))

    def _check_required_setting(self, setting) -> str:

        if setting not in self.spider.settings.keys() or not len(self.spider.settings[setting]):
            raise TypeError('Please set up %s in your scrapy settings' % setting)
        return self.spider.settings[setting]

    def _non_required_settings(self, *args) -> dict:
        return {setting.replace('RUMETR_', '').lower(): self.spider.settings[setting.upper()] for setting in args if setting in self.spider.settings.keys()}


class ApptItem(scrapy.Item):
    complex_name = scrapy.Field()
    complex_id = scrapy.Field()
    complex_url = scrapy.Field()
    addr = scrapy.Field()

    house_id = scrapy.Field()
    house_name = scrapy.Field()
    house_url = scrapy.Field()

    id = scrapy.Field()
    floor = scrapy.Field()
    room_count = scrapy.Field()
    square = scrapy.Field()
    price = scrapy.Field()
    is_studio = scrapy.Field()
    plan_url = scrapy.Field()
