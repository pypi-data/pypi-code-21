from functools import wraps


def offset_pagination(f):

    @wraps(f)
    def wrapper(self, request, *args, **kwargs):
        params = request.query_params.copy()
        offset = self.paginator.get_offset(request) + 1
        page_size = self.paginator.get_page_size(request)

        params.setdefault('start', offset)
        params.setdefault('num', page_size)

        request.pagination_params = params
        return f(self, request, *args, **kwargs)
    return wrapper
