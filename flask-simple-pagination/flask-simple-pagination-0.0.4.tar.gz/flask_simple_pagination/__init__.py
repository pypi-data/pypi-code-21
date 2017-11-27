from flask import request, jsonify
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, ParseResult

def with_pagination(item_serializer, base_url_factory):
    """
    Decorates a view function so that it will receive a page_no argument and
    can return a Page object, which will be serialized to a json serializer using
    the ItemSerializer
    """
    def outer_wrapper(f):
        def wrapper(*args, **kwargs):

            try:
                page_no = int(request.args.get("page_no", "0"))
            except ValueError:
                page_no = 0

            if page_no < 0:
                page_no = 0

            kwargs["page_no"] = page_no
            page = f(*args, **kwargs)

            assert hasattr(page, "count"), "Page object must have an integer count attribute"
            assert type(page.count) == int, "Page object must have an integer count attribute"
            assert hasattr(page, "next_page"), "Page object must have an integer next_page attribute"
            assert hasattr(page, "previous_page"), "Page object must have an integer previous_page attribute"
            assert hasattr(page, "results"), "Page object must have a results attribute"

            serialized_items = item_serializer().dump(page.results, many=True).data

            base_url = base_url_factory(request)
            if page.next_page is not None:
                next_page = _update_query_params(request.url, page.next_page, base_url=base_url)
            else:
                next_page = None

            if page.previous_page is not None:
                previous_page = _update_query_params(request.url, page.previous_page, base_url=base_url)
            else:
                previous_page = None

            return jsonify({
                "results": serialized_items,
                "count": page.count,
                "next_page": next_page,
                "previous_page": previous_page,
            })

        return wrapper
    return outer_wrapper

def _update_query_params(original_url, new_page_no, base_url=None):
    parse_result = urlparse(original_url)
    scheme = parse_result.scheme
    netloc = parse_result.netloc
    params = parse_result.params
    path = parse_result.path
    query = parse_result.query
    fragment = parse_result.fragment

    if base_url is not None:
        base_parse_result = urlparse(base_url)
        scheme = base_parse_result.scheme
        netloc = base_parse_result.netloc
        path = base_parse_result.path + path

    query_params = parse_qs(parse_result.query)
    query_params["page_no"] = new_page_no
    new_query_string = urlencode(query_params, doseq=True)
    new_parse_result = ParseResult(
        scheme,
        netloc,
        path,
        params,
        new_query_string,
        fragment
    )
    return urlunparse(new_parse_result)


