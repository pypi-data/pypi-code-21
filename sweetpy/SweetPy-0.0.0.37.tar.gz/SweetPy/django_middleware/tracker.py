from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from SweetPy.tracker import Tracker
from SweetPy.setting import is_evun_cloud_connected


class request_tracker(MiddlewareMixin):

    def process_request(self, request):
        if is_evun_cloud_connected:
            tracker = Tracker(request)
            request.tracker = tracker
        return None

    def process_response(self, request, response):
        if hasattr(request,'tracker'):
            request.tracker.print_exec_time()
        return response

    def process_exception(self, request, exception):
        print('request_tracker:exception')
        return HttpResponse("in exception")

    # def process_view(request, view_func, view_args, view_kwargs)
    #     process_template_response(request, response)