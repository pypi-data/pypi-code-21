#pylint: disable=ungrouped-imports
from collections import OrderedDict
import math
try:
	from urllib.parse import urlparse, parse_qs, urlencode, urlunsplit
except ImportError:
	from urlparse import urlparse, parse_qs, urlunsplit
	from urllib import urlencode


class Paginator(object):
	PER_PAGE = 50
	PAGE_QS = 'p'

	def __init__(self, query, page, url, per_page=None, page_qs=None):
		self.per_page = self.PER_PAGE if per_page is None else per_page
		self.page_qs = self.PAGE_QS if page_qs is None else page_qs
		self.total_count = query.count()
		page = int(page)
		if page > 1:
			query = query.offset(self.per_page * (page - 1))
		self.items = query.limit(self.per_page).all()
		self.page = page
		self.last_page = int(math.ceil(self.total_count / self.per_page))
		self.pages = range(1, int(self.last_page) + 1)

		self._url = urlparse(url)
		self._url_params = OrderedDict(parse_qs(self._url.query).items())
		if self.page_qs in self._url_params:
			del self._url_params[self.page_qs]
		self.url = self.url_for(self.page)

	def url_for(self, page):
		query_params = self._url_params.copy()
		query_params[self.page_qs] = [page]
		query_string = urlencode(query_params, doseq=True)

		return urlunsplit((
			self._url.scheme, self._url.netloc, self._url.path, query_string, ''
		))

	def render_dict(self):
		links = {
			'self': self.url,
			'first': self.url_for(1),
			'last': self.url_for(self.last_page),
			'next': None,
			'prev': None,
		}
		if self.last_page > self.page:
			links['next'] = self.url_for(self.page + 1)
		if self.page > 1:
			links['prev'] = self.url_for(self.page - 1)

		return {
			'items': self.items,
			'current_page': self.page,
			'total_count': self.total_count,
			'per_page': self.per_page,
			'total_pages': self.last_page,
			'links': links
		}

	def html_link_for(self, page):
		return '<a href="{}"{}>{}</a>'.format(
			self.url_for(page),
			' class="active"' if self.page == page else '',
			page
		)

	def render_html(self):
		pages_html = ''.join([self.html_link_for(page) for page in self.pages])

		# figure out the range of items we're currently browsing
		start = self.per_page * (self.page - 1) + 1
		end = min(self.page * self.per_page, self.total_count)
		if start == end:
			item_range = start
		else:
			item_range = '{}-{}'.format(start, end)

		return (
			'<div class="range">Showing #{} out of {} total</div>'
			'<div class="pages">{}</div>'
		).format(
			item_range, self.total_count, pages_html
		)
