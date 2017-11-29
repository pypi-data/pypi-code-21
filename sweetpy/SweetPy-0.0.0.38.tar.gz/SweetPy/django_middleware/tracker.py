from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from ..tracker import Tracker
from ..setting import is_evun_cloud_connected
from ..extend.response_plus import create_response,APIResponseHTTPCode


class request_tracker(MiddlewareMixin):

    def process_request(self, request):
        if is_evun_cloud_connected:
            tracker = Tracker(request)
            request.tracker = tracker
        return None

    def process_response(self, request, response):
        if hasattr(request,'tracker'):
            request.tracker.end()
        return response

    def process_exception(self, request, exception):
        if hasattr(request,'tracker'):
            request.tracker.end_by_exection()
        data = create_response(APIResponseHTTPCode.FAIL)
        return data

    # def process_view(request, view_func, view_args, view_kwargs)
    #     process_template_response(request, response)