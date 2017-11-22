from xiaoe.type import ColumnQueryData, ColumnRoleQueryData, ColumnDetailQueryData


class Column(object):
    @classmethod
    def query(cls, data: ColumnQueryData, poster):
        path = '/column.all.get/'
        return poster.post(path, data.data)

    @classmethod
    def query_have_role(cls, data: ColumnRoleQueryData, poster):
        path = '/column.haverole.get/'
        return poster.post(path, data.data)

    @classmethod
    def detail(cls, data: ColumnDetailQueryData, poster):
        path = '/column.detail.get/'
        return poster.post(path, data.data)
