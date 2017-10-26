
def check_permissions_is_login(method):
    def run(instace,request):
        if request.session.get('is_login',None):
            return method(instace,request)
        else:
            return request.Response(code=302, text='Not Found', headers={"Location":'login'})
    return run
