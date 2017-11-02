from scrapy.http import Request


def recycle_request(request: Request):
    r = request.replace(dont_filter=True)
    r.meta.pop('proxy')
    return r
