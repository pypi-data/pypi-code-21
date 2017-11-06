"""Pagination functionality"""

class PaginationResult:
    """Helper class to wrap a set of objects for pagination"""
    def __init__(self, results, page, page_count, next_page_url, previous_page_url):
        self.results = results
        self.page = page
        self.page_count = page_count
        self.next_page_url = next_page_url
        self.previous_page_url = previous_page_url
