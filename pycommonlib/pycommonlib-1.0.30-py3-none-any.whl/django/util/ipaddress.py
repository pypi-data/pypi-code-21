
def get_client_ip_address(request):
    '''
    @summary: get client ip address
    '''
    return request.META.get('X-Forwarded-For',request.META['REMOTE_ADDR'])