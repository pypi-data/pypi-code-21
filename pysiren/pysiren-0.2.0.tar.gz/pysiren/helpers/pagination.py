from math import ceil


class Pagination:
    def __init__(self, page, page_size, total):
        self.page_size = max(page_size, 1)
        self.total = max(total, 0)

        self.pages_count = int(ceil(self.total / float(self.page_size)))
        self.page = min(max(1, page), max(self.pages_count, 1))

    def prev(self):
        return self.page - 1 if self.has_prev else None

    @property
    def has_prev(self):
        return self.page > 1

    def next(self):
        return self.page + 1 if self.has_next else None

    @property
    def has_next(self):
        return self.page < self.pages_count

    def offset(self):
        return self.page_size * (self.page - 1)

    def get_pagination_set(self):
        if self.pages_count:
            pages = {
                'first': 1,
                'last': self.pages_count,
                'self': self.page,
                'prev': self.prev(),
                'next': self.next()
            }

            return {k: v for k, v in pages.items() if v}
        else:
            return {}
