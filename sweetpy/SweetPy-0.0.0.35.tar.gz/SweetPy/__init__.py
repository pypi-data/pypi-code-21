def check_runserver():
    from sys import argv
    _argv_count = len(argv)
    if _argv_count > 1:
        for i in range(1, _argv_count):
            _argv = argv[i].lower()
            if _argv.startswith('runserver'):
                return True
    return False

if check_runserver():
    import os
    import platform

    def get_dirs_name_by_path(path):
        result = []
        for dirpath, dirnames, filenames in os.walk(path):
            for dir in dirnames:
                result.append(dir)
            break
        return result
    def get_project_setting_path():
        sysstr = platform.system()

        local_path = os.getcwd()
        dirs = get_dirs_name_by_path(local_path)
        for _dir in dirs:
            if sysstr.lower() == 'windows':
                filename = local_path + '\\' + _dir + '\\settings.py'
                if os.path.exists(filename):
                    return _dir
            else:
                filename = local_path + '/' + _dir + '/settings.py'
                if os.path.exists(filename):
                    return _dir

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", get_project_setting_path() + ".settings")

    from rest_framework import response
    import SweetPy.extend.response_plus

    response.Response = SweetPy.extend.response_plus.Response
    from rest_framework import mixins
    import SweetPy.extend.mixins_plus

    mixins.ListModelMixin = SweetPy.extend.mixins_plus.ListModelMixin
    mixins.RetrieveModelMixin = SweetPy.extend.mixins_plus.RetrieveModelMixin
    mixins.DestroyModelMixin = SweetPy.extend.mixins_plus.DestroyModelMixin
    mixins.CreateModelMixin = SweetPy.extend.mixins_plus.CreateModelMixin
    from rest_framework import views
    import SweetPy.extend.view_plus

    views.exception_handler = SweetPy.extend.view_plus.exception_handler
    import SweetPy.extend.swagger_plus
    import SweetPy.setting

    import SweetPy.sweet_framework.sweet_framework_views
    import SweetPy.sweet_framework_cloud.sweet_framework_cloud_views