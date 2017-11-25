'''
Manage Android/ReactNative related actions through here.
'''
import os
import json
import xml.etree.ElementTree as ET

from lib.shell import run
from lib.exceptions.InvalidAndroidProject import InvalidAndroidProjectException

PWD = os.getcwd()

BASE_MANIFEST = '/app/src/main/AndroidManifest.xml'
BASE_APK_PATH = '/app/build/outputs/apk/'

NATIVE_ANDROID_MANIFEST = ''.join([PWD, BASE_MANIFEST])
REACT_NATIVE_MANIFEST = ''.join([PWD, '/android', BASE_MANIFEST])

SIGNED_ANDROID_PATH = ''.join([PWD, BASE_APK_PATH, 'app-release.apk'])
UNSIGNED_ANDROID_PATH = ''.join(
    [PWD, BASE_APK_PATH, 'app-release-unsigned.apk'])

SIGNED_REACT_NATIVE_PATH = ''.join(
    [PWD, '/android', BASE_APK_PATH, 'app-release.apk'])
UNSIGNED_REACT_NATIVE_PATH = ''.join([
    PWD, '/android', BASE_APK_PATH, 'app-release-unsigned.apk'
])

PACKAGE_JSON = 'package.json'


def is_android():
    ''' Returns true for any android project (native/RN) '''
    if is_native_android() or is_react_native():
        return True

    return False


def get_manifest_path():
    '''
    Returns native manifest path for native projects,
    and prefixes the native path by a "/android" for RN projects
    '''
    if os.path.isfile(NATIVE_ANDROID_MANIFEST):
        return NATIVE_ANDROID_MANIFEST
    elif os.path.isfile(REACT_NATIVE_MANIFEST):
        return REACT_NATIVE_MANIFEST
    else:
        raise Exception('Not an android project.')


def is_native_android():
    ''' Returns True if the project in cwd is native android project. '''
    if os.path.isfile(NATIVE_ANDROID_MANIFEST):
        return True

    return False


def is_react_native():
    ''' Returns True if the project in cwd is native android project. '''
    if os.path.isfile(REACT_NATIVE_MANIFEST) and os.path.isfile(PACKAGE_JSON):
        return True

    return False


def build():
    ''' Builds the android project. '''
    if is_react_native():
        return run('./android/gradlew -p android assembleRelease')
    elif is_native_android():
        return run('./gradlew assembleRelease')
    else:
        raise InvalidAndroidProjectException()


def clean():
    ''' Builds the android project. '''
    if is_react_native():
        return run('./android/gradlew -p android clean')
    elif is_native_android():
        return run('./gradlew clean')
    else:
        raise InvalidAndroidProjectException()


def signed(path):
    ''' If path matches signed path returns True, else returns False '''
    if path == UNSIGNED_REACT_NATIVE_PATH or path == UNSIGNED_ANDROID_PATH:
        return False

    if path == SIGNED_REACT_NATIVE_PATH or path == SIGNED_ANDROID_PATH:
        return True

    raise InvalidAndroidProjectException()


def apk_path():
    ''' Returns path to apk. '''
    paths = [
        UNSIGNED_REACT_NATIVE_PATH,
        UNSIGNED_ANDROID_PATH,
        SIGNED_ANDROID_PATH,
        SIGNED_REACT_NATIVE_PATH
    ]

    def addexistence(path): return {
        'path': path, 'exists': os.path.isfile(path)}

    def removenonexisting(path): return path['exists'] is True

    pathexists = list(filter(removenonexisting, map(addexistence, paths)))

    # Only take the first entry. (there should be only one)
    return pathexists[0]['path']


def apk_size(path):
    ''' Returns size of apk. '''
    # in megabytes.
    return os.path.getsize(path) >> 20


def build_details():
    ''' Returns the build details of the apks currently in output. '''
    path = apk_path()
    size = apk_size(path)
    is_signed = signed(path)

    return {
        'size': size,
        'apk_path': path,
        'is_signed': is_signed
    }


def parse_manifest():
    ''' Parses the manifest XML file and gets relevant information. '''
    manifestpath = get_manifest_path()
    tree = ET.parse(manifestpath)
    root = tree.getroot()

    # Only interested in the root since it has the packagename.
    packagename = root.attrib['package']

    return {
        'packagename': packagename
    }


def parse_packagejson():
    ''' Parse package.json and return relevant information. '''
    with open(PACKAGE_JSON) as packagejson:
        data = json.load(packagejson)

        return {
            'name': data['name']
        }


def project_details():
    ''' Returns the details  of the project in cwd. '''
    manifestdetails = parse_manifest()

    # For react native, parse package.json too
    if is_react_native():
        packagejsondetails = parse_packagejson()

    # Merge the two dictionaries.
    # Cant destructure here since py<3.5 support is required.
    details = manifestdetails.copy()

    if is_react_native():
        details.update(packagejsondetails)
    else:
        details.update({
            'name': manifestdetails['packagename']
        })

    return details


def launcher_icon():
    ''' Finds appropriate launcher icon for the project. '''

    return find('ic_launcher.png', PWD)


def find(name, path):
    ''' A helper to find a filename in a path. '''
    for root, _, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
