
def check_permissions_is_login(method):
    def run(self,request,*args):
        if request.session.get('is_login',None):
            return method(self,request,args)
        else:
            return request.Response(code=302, text='Not Found', headers={"Location":'login'})
    return run
