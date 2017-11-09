from django.conf import settings
from django.core.paginator import EmptyPage, Paginator


def paginate(request, items, per_page=settings.DEFAULT_PER_PAGE,
             page_key='page'):
    """
    Paginate an iterable of items, pulling the page number from the request.

    Returns a tuple of ``(paginator, page)``.
    """
    paginator = Paginator(items, per_page)

    try:
        page_number = int(request.GET[page_key])
        page = paginator.page(page_number)
    except (ValueError, KeyError, EmptyPage):
        page = paginator.page(1)

    return paginator, page
