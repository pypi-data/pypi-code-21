# -*- coding: utf-8 -*-

import re


class RangeParseException(Exception):
    '''
    Used for handling errors during range parsing
    '''
    pass


class Range(object):
    def __init__(self, start, end, page=1):
        self.start = start
        self.end = end
        self.page = page

    def get_page_size(self):
        '''

        :return: the size of a page
        '''
        return self.end - self.start + 1

    def content_range(self, length):
        '''

        :param length: the total number of results
        :return: range header string
        '''
        end = self.end if self.end <= length else length - 1
        return 'items %d-%d/%d' % (self.start, end, length)

    @classmethod
    def parse(cls, request, default_start=0, default_end=11, max_end=50):
        '''
        Parse the range headers into a range object. When there are no range headers,
        check for a page 'pagina' parameter, otherwise use the defaults defaults

        :param request: a request object
        :param default_start: default start for  paging (optional, default is 0)
        :param default_end: default end for paging (optional, default is 11)
        :param default_end: maximum end for paging (optional, default is 50, no limits in case of None)
        :return: :class: 'oe_utils.range_parser.Range'
        '''
        if 'Range' in request.headers and request.headers['Range'] is not '':
            match = re.match('^items=([0-9]+)-([0-9]+)$', request.headers['Range'])

            if match:
                start = int(match.group(1))
                end = int(match.group(2))

                if end < start:
                    end = start
                if max_end and end > start + max_end:
                    end = start + max_end
                return cls(start, end)
            else:
                raise RangeParseException('range header does not match expected format')
        elif 'pagina' in request.params:
            page = int(request.params.get('pagina'))
            start = default_start + (default_end + 1) * (page - 1)
            end = default_end * page + page - 1
            return cls(start, end, page)
        else:
            return cls(default_start, default_end)

    def set_response_headers(self, response, total_count):
        '''
        Set the correct range headers on the response

        :param response: a response object
        :param total_count: the total number of results
        '''
        response.headerlist.append(('Access-Control-Expose-Headers', 'Content-Range, X-Content-Range'))
        response.accept_ranges = 'items'
        if total_count is None:
            raise RangeParseException('Provided length value is null')
        if total_count > 0:
            response.content_range = self.content_range(total_count)
