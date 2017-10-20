from django.core.management.base import BaseCommand, CommandError
import os
import shutil
import platform

from ._tools import get_p4a_args, update_apk, parcefiles, overwrite_p4a, post_update_apk, read_configuration, read_apk_args

from djangoforandroid.core.toolchain import ToolchainCL
#from pythonforandroid.toolchain import ToolchainCL

#P4A = "p4a"
# P4A = "python /home/yeison/Documents/development/djangoforandroid/example/pythonforandroid/toolchain.py"

class Command(BaseCommand):
    help = 'Generate .apk for debug'
    can_import_settings = True

    #----------------------------------------------------------------------
    def add_arguments(self, parser):
        """"""

        parser.add_argument(
            '--debug',
            action='store_true',
            dest='debug',
            default=True,
            help='Debug apk with',
        )

        parser.add_argument(
            '--release',
            action='store_true',
            dest='release',
            default=False,
            help='Release unsigned apk',
        )

        parser.add_argument(
            '--install',
            action='store_true',
            dest='install',
            default=False,
            help='Install apk with adb.',
        )

        parser.add_argument(
            '--run',
            action='store_true',
            dest='run',
            default=False,
            help='Run apk with adb.',
        )

        parser.add_argument(
            '--logcat',
            action='store_true',
            dest='logcat',
            default=False,
            help='Log apk with adb.',
        )



    #----------------------------------------------------------------------
    def handle(self, *args, **options):
        """"""
        from django.conf import settings

        update_apk(settings)
        overwrite_p4a(settings)

        NAME = os.path.split(settings.BASE_DIR)[-1]
        build_dir = os.path.join(settings.ANDROID['BUILD']['build'], NAME)
        #build_dir = os.path.join(settings.ANDROID['BUILD']['build'])
        name = settings.ANDROID['APK']['name']
        version = settings.ANDROID['APK']['version']
        apk_debug = os.path.join(build_dir, '{}-{}-debug.apk'.format(name, version)).replace(' ', '')
        apk_release = os.path.join(build_dir, '{}-{}-release.apk'.format(name, version)).replace(' ', '')
        package = settings.ANDROID['APK']['package']

        #collectstatic
        app_dir = os.path.join(settings.ANDROID['BUILD']['build'], NAME, 'app')
        #app_dir = os.path.join(settings.ANDROID['BUILD']['build'], 'app')
        os.chdir(os.path.join(app_dir, NAME))
        host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
        os.system('{} manage.py collectstatic --noinput'.format(host_python ))

        post_update_apk(settings)

        os.chdir(build_dir)
        argv = read_configuration(settings)

        if options['release']:
            if os.path.exists(apk_release):
                os.remove(apk_release)


            keystore = settings.ANDROID['KEY']['RELEASE_KEYSTORE'].replace('.keystore', '') + ".upload.jks"
            if not os.path.exists(keystore):
                keystore = settings.ANDROID['KEY']['RELEASE_KEYSTORE']

            os.environ['P4A_RELEASE_KEYSTORE'] = keystore
            os.environ['P4A_RELEASE_KEYALIAS'] = settings.ANDROID['KEY']['RELEASE_KEYALIAS']
            os.environ['P4A_RELEASE_KEYSTORE_PASSWD'] = settings.ANDROID['KEY']['RELEASE_KEYSTORE_PASSWD']
            os.environ['P4A_RELEASE_KEYALIAS_PASSWD'] = settings.ANDROID['KEY']['RELEASE_KEYALIAS_PASSWD']


            argv.c['build_mode'] = 'release'

            #self.p4a_sign(settings, argv, apk_release)

            tc = ToolchainCL(argv)
            tc.apk(release=True)
            shutil.copy(apk_release, settings.BASE_DIR)
            run_apk = apk_release


        elif options['debug']:
            if os.path.exists(apk_debug):
                os.remove(apk_debug)

            #host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
            #os.system('{} apk {}'.format(P4A, argv))

            argv.c['build_mode'] = 'debug'
            #ToolchainCL(argv)

            tc = ToolchainCL(argv)
            tc.apk(release=False)
            shutil.copy(apk_debug, settings.BASE_DIR)
            run_apk = apk_debug


        if options['install']:
            print("Installing...")
            os.system("adb start-server")
            os.system("adb install -r {}".format(apk_release))

            if options['run']:
                print("Running...")
                os.system("adb shell monkey -p {PACKAGE} -c android.intent.category.LAUNCHER 1".format(PACKAGE=package))

            if options['logcat']:
                print("Log:")
                os.system("adb logcat")


#     #----------------------------------------------------------------------
#     def p4a_sign(self, settings, argv, apk_release):
#         """"""
#         #host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
#         #os.system('{} apk --release {}'.format(P4A, argv))
#
#         #args = read_apk_args(argv)
#
#         tc = ToolchainCL(argv)
#         tc.apk(release=True)
#
#         shutil.copy(apk_release, settings.BASE_DIR)

#
#     #----------------------------------------------------------------------
#     def manual_sign(self, settings, argv, apk_debug, apk_release):
#         """"""
#         if not os.path.exists(apk_debug):
#             #host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
#             os.system('{} apk {}'.format(P4A, argv))
#
#         apk_unaligned = apk_debug.replace("-debug.apk", "-unaligned.apk")
#         shutil.copy(apk_debug, apk_unaligned)
#
#         v = os.listdir(os.path.join(settings.ANDROID['ANDROID']['SDK'], 'build-tools'))
#         v.sort()
#         zipalign = os.path.join(settings.ANDROID['ANDROID']['SDK'], 'build-tools', v[-1], 'zipalign')
#
#         os.system("jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -storepass {} -keypass {} -keystore {} {} {}".format(os.getenv('P4A_RELEASE_KEYSTORE_PASSWD'), os.getenv('P4A_RELEASE_KEYALIAS_PASSWD'), os.getenv('P4A_RELEASE_KEYSTORE'), apk_unaligned, os.getenv('P4A_RELEASE_KEYALIAS')))
#         os.system("jarsigner -verify -verbose -certs {}".format(apk_unaligned))
#         os.system("{} -v 4 {} {}".format(zipalign, apk_unaligned, apk_release))
#         shutil.copy(apk_release, settings.BASE_DIR)
