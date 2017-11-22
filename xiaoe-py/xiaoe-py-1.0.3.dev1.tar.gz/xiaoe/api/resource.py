from xiaoe.type import ResourceQueryData, ResourceQueryByColumnData, ResourceDetailQueryData


class Resource(object):
    @classmethod
    def query(cls, data: ResourceQueryData, poster):
        path = '/all.resourcelist.get/'
        return poster.post(path, data.data)

    @classmethod
    def query_in_column(cls, data: ResourceQueryByColumnData, poster):
        path = '/column.resourcelist.get/'
        return poster.post(path, data.data)

    @classmethod
    def audio_detail(self, data: ResourceDetailQueryData, poster):
        path = '/audio.detail.get/'
        return poster.post(path, data.data)

    @classmethod
    def video_detail(self, data: ResourceDetailQueryData, poster):
        path = '/video.detail.get/'
        return poster.post(path, data.data)

    @classmethod
    def imagetext_detail(self, data: ResourceDetailQueryData, poster):
        path = '/imagetext.detail.get/'
        return poster.post(path, data.data)
