# -*- coding: utf-8 -*-
from pynlple.exceptions import DataSourceException


class Source(object):

    def __repr__(self, *args, **kwargs):
        return '{}({})'.format(str(self.__class__.__name__), repr(vars(self)))


class SkippingSource(Source):

    def __init__(self):
        self.__to_skip = None
        self.__to_take = None
        super().__init__()

    def to_skip(self):
        return self.__to_skip

    def skip(self, skip):
        self.__to_skip = skip
        return self

    def to_take(self):
        return self.__to_take

    def take(self, take):
        self.__to_take = take
        return self


class BulkSource(SkippingSource):

    def __init__(self, skipping_source, bulk_size=5000):
        self.skipping_source = skipping_source
        self.bulk = bulk_size
        super().__init__()

    def get_data(self):
        all_data = []
        range_ = self.__get_bulk_range_limited(self.to_skip() if self.to_skip() else 0, len(all_data))
        try:
            got = None
            print('Start draining from skipping source: {}'.format(repr(self.skipping_source)))
            while range_ and (not got or got >= self.bulk) and got != 0:
                data = self.__get_bulk(range_)
                got = len(data)
                all_data.extend(data)
                range_ = self.__get_bulk_range_limited(range_[1], len(all_data))
            print('Source seems to be exhausted')
            return all_data
        except DataSourceException as de:
            raise DataSourceException('Error while dumping bulk {}-{} from {}:\n{}'.format(str(range_[0]), str(range_[1]), repr(self), de.__str__()))

    def __get_bulk_range_limited(self, init_s, got_total):
        real_bulk = self.bulk
        # If there are limits on amount to take, check if we reached them
        if self.to_take():
            to_limit_leftover = self.to_take() - got_total
            # Reduce the bulk to the leftover amount
            if real_bulk > to_limit_leftover:
                real_bulk = to_limit_leftover
        # If we are not going to take anything in the end - return None
        if real_bulk == 0:
            return None
        else:
            return init_s, init_s + real_bulk

    def __get_bulk(self, bulk_range_tuple):
        print('Getting {}-{} bulk from the skipping source'.format(str(bulk_range_tuple[0]), str(bulk_range_tuple[1])))
        data = self.skipping_source.skip(bulk_range_tuple[0]).take(bulk_range_tuple[1] - bulk_range_tuple[0]).get_data()
        return data