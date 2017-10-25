import os

ANDROID = {

    'APK': {
        #'name': "D4A",
        #'version': '0.1',
        #'numericversion': '1';
        #'package': 'com.yeisoncardona.d4a.testapk',
        #'icon': os.path.join(STATIC_ROOT, 'images', 'icon.png'),
        #'numericversion': 0,
        'statusbarcolor': '#000000',
        'navigationbarcolor': '#000000',
        'orientation': 'portrait',
        'intent_filters': None,
    },

    'APP': {
        'multithread': False,
        'logs': 'logs',  #directory for save logs, by default is in the app folder

    },


    'ANDROID': {
        'ARCH': 'armeabi-v7a',
        'SDK': '/absolute/path/to/android-sdk-linux', #https://developer.android.com/studio/index.html
        'API': '21',
        'CRYSTAX_NDK': '/absolute/path/to/crystax-ndk-10.3.2', #https://www.crystax.net/en/download
        'CRYSTAX_NDK_VERSION': '10.3.2',
        'BUILD_TOOL': 'ant',  #ant, gradle
    },


    #'KEY': {
        #'RELEASE_KEYSTORE': os.path.join(BASE_DIR, 'd4a.keystore'),
        #'RELEASE_KEYALIAS': 'd4a',
        #'RELEASE_KEYSTORE_PASSWD': 'MySuperSecurePassw',
        #'RELEASE_KEYALIAS_PASSWD': 'MySuperSecurePassw',
    #},

    'SPLASH': {
        'static_html': False,
        'resources': [],
    },

    'PORT': '8888',
    'IP': '127.0.0.1',

    'PERMISSIONS': [],
    '__PERMISSIONS': ['INTERNET', 'WRITE_EXTERNAL_STORAGE'],

    'BUILD': {
        'build': os.path.expanduser('~/.django-for-android'),
        'recipes': None,  #string
        'whitelist': None,
        'requirements': [],
        '__requirements': ['python3crystax', 'django', 'sqlite3', 'djangoforandroid', 'pytz', 'pyjnius'],
        'exclude_dirs': [],
        'exclude_files': [],
        'include_exts': [],
        },


    #'CUSTOM': {
        #'var1': 'Hola',
        #'var2': 'mundo',
        #'var3': 'I <python3 you',
    #},

}



COMPILER = {



    'ANDROID': {
        'ARCH': 'armeabi-v7a',
        'SDK': '/absolute/path/to/android-sdk-linux', #https://developer.android.com/studio/index.html
        'API': '21',
        'CRYSTAX_NDK': '/absolute/path/to/crystax-ndk-10.3.2', #https://www.crystax.net/en/download
        'CRYSTAX_NDK_VERSION': '10.3.2',
    },


    #'KEY': {
        #'RELEASE_KEYSTORE': os.path.join(BASE_DIR, 'd4a.keystore'),
        #'RELEASE_KEYALIAS': 'd4a',
        #'RELEASE_KEYSTORE_PASSWD': 'MySuperSecurePassw',
        #'RELEASE_KEYALIAS_PASSWD': 'MySuperSecurePassw',
    #},


    'BUILD': {
        'build': os.path.expanduser('~/.django-for-android'),
        'recipes': None,  #string
        'whitelist': None,
        'requirements': [],
        '__requirements': ['python3crystax', 'django', 'sqlite3', 'djangoforandroid', 'pyjnius'],

        },



}

