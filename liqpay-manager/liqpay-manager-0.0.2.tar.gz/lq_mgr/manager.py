from functools import partial

try:
    from liqpay import LiqPay
except ImportError:
    from liqpay.liqpay import LiqPay


class LiqPayAPIWrapper(LiqPay):
    def __getattr__(self, key):
        api_query_func = partial(self.api, 'request')
        def api_query_func_wrapper(request_method):
            def wrapper(**api_args):
                api_args['version'] = '3'
                api_args['action'] = key
                return request_method(api_args)
            return wrapper
        return api_query_func_wrapper(api_query_func)


class LiqPayAPI:
    def __init__(self, public_key, private_key):
        self.__public_key = public_key
        self.__private_key = private_key

    def __enter__(self):
        self.__api_client = LiqPayAPIWrapper(self.__public_key, self.__private_key)
        return self.__api_client

    def __exit__(self, exception_type, exception_value, traceback):
        del self.__api_client
        return all(v is not None
                   for v in (exception_type, exception_value, traceback))
