import os
import shutil
from collections import defaultdict

from configparser import RawConfigParser

from ._settings import ANDROID as ANDROID_SETTINGS
from ._settings import COMPILER as ANDROID_COMPILER

#----------------------------------------------------------------------
def __updatedict__(dm, ds):
    """Update content from ds in dm, if no exists then create it."""

    for key in ds.keys():
        if isinstance(ds[key], dict):
            if key in dm:
                ds[key].update(dm[key])

        elif isinstance(ds[key], list):
            if key in dm:
                ds[key] = set(ds[key] + dm[key])

        elif isinstance(ds[key], (int, float, str, bytes)):
            if key in dm:
                ds[key] = dm[key]

    dm.update(ds)
    return dm


#----------------------------------------------------------------------
def get_p4a_args(settings, service=False):
    """"""
    ANDROID = __updatedict__(settings.ANDROID, ANDROID_SETTINGS)


    #overwrite configuration for compile in server
    if service:
        ANDROID = __updatedict__(ANDROID_COMPILER, ANDROID)



    PORT = ANDROID['PORT']
    IP = ANDROID['IP']

    APK_NAME = ANDROID['APK']['name']
    #NAME = settings.__str__()[settings.__str__().find('"')+1:settings.__str__().find('.')]
    NAME = os.path.split(settings.BASE_DIR)[-1]
    VERSION = ANDROID['APK']['version']

    NUMERICVERSION = ANDROID['APK'].get('numericversion',  int(''.join([v.rjust(2, '0') for v in '{}.0.0'.format(VERSION).split('.')[:3]])))

    PACKAGE = ANDROID['APK']['package']
    ICON = ANDROID['APK']['icon']
    PRESPLASH = ANDROID['APK']['icon']
    ORIENTATION = ANDROID['APK']['orientation']


    if ANDROID['PERMISSIONS']:
        PERMISSIONS = []
        for permission in set(list(ANDROID['PERMISSIONS']) + list(ANDROID['__PERMISSIONS'])):
            #PERMISSIONS += "--permission={}\n".format(permission)
            PERMISSIONS.append(permission)
        #PERMISSIONS =  " ".join(PERMISSIONS)

    if service:
        BUILD_DIR = os.path.join(ANDROID['BUILD']['build'], 'example', 'build')
        RECIPES_DIR = os.path.join(ANDROID['BUILD']['build'], 'example', 'recipes')
        APP_DIR = os.path.join(ANDROID['BUILD']['build'], 'example', 'app')
    else:
        BUILD_DIR = os.path.join(ANDROID['BUILD']['build'], NAME, 'build')
        RECIPES_DIR = os.path.join(ANDROID['BUILD']['build'], NAME, 'recipes')
        APP_DIR = os.path.join(ANDROID['BUILD']['build'], NAME, 'app')
#         BUILD_DIR = os.path.join(ANDROID['BUILD']['build'], 'build')
#         RECIPES_DIR = os.path.join(ANDROID['BUILD']['build'], 'recipes')
#         APP_DIR = os.path.join(ANDROID['BUILD']['build'], 'app')

    WHITELIST = os.path.join(RECIPES_DIR, 'whitelist')

    REQUIREMENTS = ",".join(ANDROID['BUILD']['__requirements'] + ANDROID['BUILD']['requirements'])

    ANDROID_SDK = ANDROID['ANDROID']['SDK']
    ANDROID_SDK_API = ANDROID['ANDROID']['API']

    CRYSTAX_NDK = ANDROID['ANDROID']['CRYSTAX_NDK']
    CRYSTAX_NDK_VERSION = ANDROID['ANDROID']['CRYSTAX_NDK_VERSION']

    BUILD_TOOL = ANDROID['ANDROID']['BUILD_TOOL']

    ARCH = ANDROID['ANDROID']['ARCH']

    BUILD = ANDROID['BUILD']



    #EXTRA_OPTIONS = ""
    APP_MULTITHREAD = ANDROID['APP']['multithread']
    APP_LOGS = ANDROID['APP']['logs']

    if APP_MULTITHREAD:
        print("Use multithread for Django server is NOT compatible with Jnius!!!")


    if ANDROID['APK']['intent_filters']:
        INTENT_FILTERS = ANDROID['APK']['intent_filters']
    else:
        INTENT_FILTERS = False


    locals_ = locals()

    for key in ANDROID.get('CUSTOM', {}):
        #eval('CUSTOM_{} = {}'.format(key, ANDROID['CUSTOM'][key]))
        locals_['CUSTOM_{}'.format(key)] = ANDROID['CUSTOM'][key]


    return locals()



#----------------------------------------------------------------------
def update_apk(settings, service=False):
    """"""
    ARGS = get_p4a_args(settings, service)
    set_env(settings)

    build_dir = os.path.dirname(ARGS['BUILD_DIR'])
    app_dir = os.path.join(build_dir, 'app')
    resources_dir = os.path.join(app_dir, 'resources')
    #os.makedirs(app_dir, exist_ok=True)
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)
    #if os.path.exists(resources_dir):
        #shutil.rmtree(resources_dir)
    os.makedirs(resources_dir, exist_ok=True)
    os.makedirs(ARGS['BUILD_DIR'], exist_ok=True)

    #generate icon apk
    icon = settings.ANDROID['APK']['icon']
    shutil.copyfile(icon, os.path.join(resources_dir, 'icon.png'))

    #generate static html for splash
    splash_html = settings.ANDROID['SPLASH']['static_html']
    if splash_html:
        splash_resources = settings.ANDROID['SPLASH']['resources']
        splash_build = os.path.join(app_dir, 'resources', 'splash.html')
        shutil.copyfile(splash_html, splash_build)
        for rsc in splash_resources:
            shutil.copy(rsc, resources_dir)
        parcefiles([splash_build], ARGS)
    else:
        from djangoforandroid import src
        load = os.path.join(os.path.dirname(src.__file__), 'splash.html')
        shutil.copyfile(load, os.path.join(app_dir, 'resources', 'splash.html'))
        parcefiles([os.path.join(app_dir, 'resources', 'splash.html')], ARGS)


    #generate main.py
    from djangoforandroid import src
    raw_main = os.path.join(os.path.dirname(src.__file__), 'main.py')
    build_main = os.path.join(app_dir, 'main.py')
    shutil.copyfile(raw_main, build_main)
    parcefiles([build_main], ARGS)

    #move project
    project_dir = settings.BASE_DIR
    project_build = os.path.join(app_dir, ARGS['NAME'])
    #if os.path.exists(project_build):
        #shutil.rmtree(project_build)
    shutil.copytree(project_dir, project_build)


    #if ARGS['BUILD']['include_exts']:
        #for root, dirs, files in os.walk(project_build):
            #for file in files:
                #path = os.path.join(root, file)
                #if path.endswith(tuple(ARGS['BUILD']['include_exts'])):
                    #continue
                #else:
                    #print("removing {} from build".format(path))
                    #os.remove(path)

    #if ARGS['BUILD']['exclude_dirs']:
        #for dir_ in ARGS['BUILD']['exclude_dirs']:
            #path = os.path.join(project_build, dir_)
            #if os.path.exists(path):
                #print("removing {} from build".format(path))
                #shutil.rmtree(path, ignore_errors=True)

    #for root, dirs, files in os.walk(project_build):
        #if '__pycache__' in dirs:
            #dirs.remove('__pycache__')
            #path = os.path.join(root, '__pycache__')
            #print("removing {} from build".format(path))
            #shutil.rmtree(path, ignore_errors=True)


    #generate d4a.config
    from djangoforandroid import src
    raw_p4a = os.path.join(os.path.dirname(src.__file__), 'd4a.config')
    build_p4a = os.path.join(build_dir, 'd4a.config')
    shutil.copyfile(raw_p4a, build_p4a)
    parcefiles([build_p4a], ARGS)

    #copy defauts recipes
    from djangoforandroid import recipes
    recipes_dir = os.path.dirname(recipes.__file__)
    recipes_build = os.path.join(build_dir, 'recipes')
    if os.path.exists(recipes_build):
        shutil.rmtree(recipes_build)
    shutil.copytree(recipes_dir, recipes_build)

    #merge recipes
    if 'recipes' in settings.ANDROID['BUILD'] and settings.ANDROID['BUILD']['recipes']:
        recipes = settings.ANDROID['BUILD']['recipes']
        for dir_ in os.listdir(recipes):
            dir_ = os.path.join(recipes, dir_)
            shutil.copytree(dir_, os.path.join(recipes_build, os.path.split(dir_)[-1]))

    #merge whitelist
    if 'whitelist' in settings.ANDROID['BUILD'] and settings.ANDROID['BUILD']['whitelist']:
        lines = open(settings.ANDROID['BUILD']['whitelist'], 'r').readlines()
        file = open(ARGS['WHITELIST'], 'a')
        file.writelines(lines)
        file.close()


#----------------------------------------------------------------------
def overwrite_p4a(settings, service=False):
    """"""
    ARGS = get_p4a_args(settings, service)
    from djangoforandroid import src

    ##replace PythonActivity
    ##activity_build = os.path.join(ARGS['BUILD_DIR'], 'dists', 'djangoserver', 'src', 'org', 'kivy', 'android', 'PythonActivity.java')
    #activity_build = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'src', 'org', 'kivy', 'android', 'PythonActivity.java')
    #activity_dir = os.path.join(os.path.dirname(src.__file__), 'PythonActivity.java')
    #if os.path.exists(activity_build):
        ##os.remove(activity_build)
        #shutil.copy(activity_dir, activity_build)
    ##statusbarcolor = settings.ANDROID['APK']['statusbarcolor']
    ##navigationbarcolor = settings.ANDROID['APK']['navigationbarcolor']
    ###download = settings.ANDROID['APK']['download_name']
    ##parcefiles([activity_build], {'STATUS_BAR_COLOR': statusbarcolor, 'NAVIGATION_BAR_COLOR': navigationbarcolor,})


    KWARGS = {
        'STATUS_BAR_COLOR': settings.ANDROID['APK']['statusbarcolor'],
        'NAVIGATION_BAR_COLOR': settings.ANDROID['APK']['navigationbarcolor'],
    }


    #just replace .java
    for file in ['PythonService.java', 'PythonUtil.java', 'PythonActivity.java']:
        file_build = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'src', 'org', 'kivy', 'android', file)
        file_dir = os.path.join(os.path.dirname(os.path.dirname(src.__file__)), 'core', 'bootstraps', 'webview', 'build', 'src', 'org', 'kivy', 'android', file)
        if os.path.exists(file_build):
            shutil.copy(file_dir, file_build)

    #parce files
    for file in ['PythonActivity.java']:
        file_build = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'src', 'org', 'kivy', 'android', file)
        #download = settings.ANDROID['APK']['download_name']
        parcefiles([file_build], KWARGS)


    ##replace build.py
    ##buildpy_build = os.path.join(ARGS['BUILD_DIR'], 'dists', 'djangoserver', 'build.py')
    #buildpy_build = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'build.py')
    #buildpy_dir = os.path.join(os.path.dirname(src.__file__), 'build.py')
    #if os.path.exists(buildpy_build):
        #shutil.copy(buildpy_dir, buildpy_build)

    ##replace AndroidManifest.tmpl.xml
    ##manifest_build = os.path.join(ARGS['BUILD_DIR'], 'dists', 'djangoserver', 'templates', 'AndroidManifest.tmpl.xml')
    #manifest_build = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'templates', 'AndroidManifest.tmpl.xml')
    #manifest_dir = os.path.join(os.path.dirname(src.__file__), 'AndroidManifest.tmpl.xml')
    #if os.path.exists(manifest_build):
        #shutil.copy(manifest_dir, manifest_build)

    #clear webview_includes
    #webview_includes = os.path.join(ARGS['BUILD_DIR'], 'dists', 'djangoserver', 'webview_includes')
    webview_includes = os.path.join(ARGS['BUILD_DIR'], 'build', 'bootstrap_builds', 'webview-python3crystax', 'webview_includes')
    if os.path.exists(webview_includes):
        for file in os.listdir(webview_includes):
            os.remove(os.path.join(webview_includes, file))
    else:
        os.makedirs(webview_includes)



#----------------------------------------------------------------------
def parcefiles(editfiles, kwargs):
    """"""
    for filename in editfiles:
        if not os.path.exists(filename):
            return
        file = open(filename, "r")
        lines = file.readlines()
        file.close()
        new_lines = "".join(lines)
        new_lines = new_lines.replace("{{", "#&<<").replace("}}", ">>&#")
        new_lines = new_lines.replace("{", "{{").replace("}", "}}")
        new_lines = new_lines.replace("#&<<", "{").replace(">>&#", "}")

        #new_lines = new_lines.format(**kwargs)
        d = defaultdict(lambda: 'UNKNOWN')
        d.update(kwargs)


        #class Default(dict):
            #def __missing__(self, key):
                #return key

            ##----------------------------------------------------------------------
            #def get(self, k, d=None):
                #""""""
                #k
                #return k

        #d = Default(**kwargs)


        new_lines = new_lines.format_map(d)

        file = open(filename, "w")
        file.write(new_lines)
        file.close()



#----------------------------------------------------------------------
def clean_build(settings):
    """"""
    ARGS = get_p4a_args(settings)
    shutil.rmtree(ARGS['BUILD_DIR'])


#----------------------------------------------------------------------
def post_update_apk(settings):
    """"""
    ARGS = get_p4a_args(settings)
    build_dir = os.path.dirname(ARGS['BUILD_DIR'])
    app_dir = os.path.join(build_dir, 'app')
    project_build = os.path.join(app_dir, ARGS['NAME'])

    if ARGS['BUILD']['exclude_dirs']:
        for dir_ in ARGS['BUILD']['exclude_dirs']:
            path = os.path.join(project_build, dir_)
            if os.path.exists(path):
                print("removing {} from build".format(path))
                shutil.rmtree(path, ignore_errors=True)

    if ARGS['BUILD']['exclude_files']:
        for file in ARGS['BUILD']['exclude_files']:
            path = os.path.join(project_build, file)
            if os.path.exists(path):
                print("removing {} from build".format(path))
                os.remove(path)

    if ARGS['BUILD']['include_exts']:
        for root, dirs, files in os.walk(project_build):
            for file in files:
                path = os.path.join(root, file)
                if path.endswith(tuple(ARGS['BUILD']['include_exts'])):
                    continue
                else:
                    print("removing {} from build".format(path))
                    os.remove(path)

    for root, dirs, files in os.walk(project_build):
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
            path = os.path.join(root, '__pycache__')
            print("removing {} from build".format(path))
            shutil.rmtree(path, ignore_errors=True)


#def read_configuration(settings, list_=False, argv_=False, file=False, dict_=False):

    #ARGS = get_p4a_args(settings)
    #build_dir = os.path.dirname(ARGS['BUILD_DIR'])
    #build_p4a = os.path.join(build_dir, 'd4a.config')
    #argv = []

    #if file:
        #return build_p4a

    #with open(build_p4a) as fd:
        #lines = fd.readlines()
    #lines = filter(lambda l:l.startswith("--"), lines)
    #lines = list(map(lambda l:l.replace("\n", ""), lines))


    #if list_:
        #return lines
    #elif argv_:
        #return [item for list_ in [argv.split("=") for argv in lines] for item in list_]
    #elif dict_:
        #return {a[0].replace('--', ''):a[1] for a in [argv.split("=") for argv in lines] if len(a) == 2}
    #else:
        #return " ".join(lines)


#----------------------------------------------------------------------
def read_apk_args(args):
    """"""
    apk_args = {}



    return apk_args


#----------------------------------------------------------------------
def read_configuration(settings):

    ARGS = get_p4a_args(settings)
    build_dir = os.path.dirname(ARGS['BUILD_DIR'])
    build_p4a = os.path.join(build_dir, 'd4a.config')


    config = RawConfigParser()
    config.readfp(open(build_p4a))


    class args:

        #----------------------------------------------------------------------
        def __init__(self):
            """"""

            self.c = dict(config.items("App"))
            #self.c.update({t[0]:t[1].lower()=='true' for t in config.items("App") if t[1] in ['True', 'False']})


        #----------------------------------------------------------------------
        def __getattr__(self, attr):
            """"""

            if not self.c[attr]:
                return False

            if self.c[attr].lower() in ['true', 'false']:
                return self.c[attr].lower() == 'true'

            elif self.c[attr].lstrip('-+').isdigit():
                return int(self.c[attr])

            elif self.c[attr][0] == '[' and  self.c[attr][-1] == ']':
                return eval(self.c[attr])


            else:
                return self.c[attr]

    return args()



#----------------------------------------------------------------------
def set_env(settings):
    """"""
#     os.environ['NDK_PROJECT_PATH'] = settings.ANDROID['ANDROID']['CRYSTAX_NDK']
