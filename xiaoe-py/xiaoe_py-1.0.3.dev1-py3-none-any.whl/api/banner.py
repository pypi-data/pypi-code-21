from xiaoe.type import BannerQueryData


class Banner(object):
    @classmethod
    def query(cls, banner_query_data: BannerQueryData, poster):
        path = '/banner.get/'
        print(banner_query_data.data)
        return poster.post(path, banner_query_data.data)
