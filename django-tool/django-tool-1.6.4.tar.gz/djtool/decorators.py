from django.http import HttpResponseRedirect, JsonResponse
from django.core.cache import cache
from django.conf import settings
from djtool import ClientOauth, Common
oauth = ClientOauth()
try:
    assert hasattr(settings, 'ADMIN_MODEL')
    assert hasattr(settings, 'UNION_LOGIN_URL')
    Admin = Common.import_model(settings.ADMIN_MODEL)
except:
    raise Exception('请在settings.py配置ADMIN_MODEL, UNION_LOGIN_URL')


def adminlogin(fun):
    def new_fun(request, *args, **kwargs):
        url = request.path.split('/')
        if url[1] == "admin":
            uuid = request.session.get('login')
            try:
                if uuid:
                    admin = Admin.objects.get(uuid=uuid, del_state=1)
                    assert True if cache.get('admin%s' % admin.unionuuid) == 1 else False
                    request.admin = admin
                else:
                    clientid = request.META.get('INVOCATION_ID', '_login')
                    token = request.COOKIES.get(clientid)
                    if token:
                        info = oauth.info(token)
                        if info:
                            admin = Admin.objects.filter(unionuuid=info.get('uuid'), del_state=1)
                            if admin:
                                admin = admin[0]
                            else:
                                admin = Admin.objects.create(unionuuid=info.get('uuid'), showname=info.get('name', ''))
                            request.session['login'] = admin.uuid
                            request.session['info'] = info
                            request.admin = admin
                        else:
                            assert False
                    else:
                        assert False
            except Exception as e:
                print(e)
                if request.session.get('login'):
                    del request.session['login']
                if request.is_ajax():
                    return JsonResponse(Common.msg(61000))
                return HttpResponseRedirect('%s?backurl=%s' % (settings.UNION_LOGIN_URL, 'http://%s%s' % (request.get_host(), request.get_full_path())))
        return fun(request, *args, **kwargs)
    return new_fun
