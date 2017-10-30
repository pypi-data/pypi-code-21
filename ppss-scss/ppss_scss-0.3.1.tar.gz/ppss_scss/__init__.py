sourcedir = 'scss/'
routepath = '/css'
workingfolder = '/tmp'
import logging,os, shutil
l = logging.getLogger(__name__)


def getAndCreateDir(settings,key,default,create=True):
    directory = settings.get(key,default)
    if create and not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def clearDir(directory):
    for the_file in os.listdir(directory):
        file_path = os.path.join(directory, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def includeme(config):
    global sourcedir,routepath,workingfolder
    settings = config.get_settings()
    #sourcedir = settings.get('ppss_scss.srcdir','scss/')
    #routepath = settings.get('ppss_scss.routepath','/css/*fizzle')
    #workingfolder = settings.get('ppss_scss.workingfolder','/tmp/css/')
    sourcedir = getAndCreateDir(settings,'ppss_scss.srcdir','scss/')
    routepath = getAndCreateDir(settings,'ppss_scss.routepath','/css/*fizzle',False)
    workingfolder = getAndCreateDir(settings,'ppss_scss.workingfolder','/tmp/css/')
    if settings.get('ppss_scss.delete_on_start','True') == "True":
        clearDir(workingfolder)
    l.info("ppss_scss.sorucedir={src} ppss_scss.routepath = {route}".format(src=sourcedir,route=routepath))
    config.add_route('ppss_scss_compile', routepath)
    config.scan()