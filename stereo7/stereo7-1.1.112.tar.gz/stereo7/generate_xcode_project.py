from __future__ import division
import os
import fileutils
import shutil
from project import Project


def clone():
    out_folder = '{}/proj.ios'.format(fileutils.root_dir)
    if os.path.isdir(out_folder):
        shutil.rmtree(out_folder)
    cmd = 'git clone git@bitbucket.org:stereo7_tools/template_proj_ios_syn.git {}'.format(out_folder)
    print cmd
    os.system(cmd)
    shutil.rmtree('{}/.git'.format(out_folder))
    os.remove('{}/.gitignore'.format(out_folder))


def get_project_folder(arg_parser):
    folder = fileutils.root_dir + '/proj.ios/'
    return folder


def replace_values(kind, file):
    content = open(file).read()
    content = content.replace('@{PACKAGE_NAME}', Project.instance.package)
    content = content.replace('@{APP_BUNDLE_NAME}', Project.instance.app_bundle_name)
    if kind:
        if Project.instance.with_pro_version:
            content = content.replace('@{FACEBOOK_APP_ID}', Project.instance.services['ios'][kind].facebook_id)
            content = content.replace('@{FLURRY_APP_ID}', Project.instance.services['ios'][kind].flurry_id)
            content = content.replace('@{APPODEAL_APP_ID}', Project.instance.services['ios'][kind].appodeal_id)
        else:
            content = content.replace('@{FACEBOOK_APP_ID}', Project.instance.services['ios'].facebook_id)
            content = content.replace('@{FLURRY_APP_ID}', Project.instance.services['ios'].flurry_id)
            content = content.replace('@{APPODEAL_APP_ID}', Project.instance.services['ios'].appodeal_id)

    fileutils.write(file, content)


def copy_resources(arg_parser):
    proj_folder = get_project_folder(arg_parser)
    icons_lite = '{}/store/icons/'.format(fileutils.root_dir)
    icons_pro = '{}/store/icons/pro/'.format(fileutils.root_dir)
    if Project.instance.with_pro_version:
        icons_lite += 'lite/'
    icons = [20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180]
    for size in icons:
        shutil.copy2('{}Icon-{}.png'.format(icons_lite, size), '{}ios/Images.xcassets/AppIcon.lite.appiconset/{}.png'.format(proj_folder, size))
        if Project.instance.with_pro_version:
            shutil.copy2('{}Icon-{}.png'.format(icons_pro, size), '{}ios/Images.xcassets/AppIcon.pro.appiconset/{}.png'.format(proj_folder, size))


def run(arg_parser):
    clone()
    replace_values('', get_project_folder(arg_parser) + 'Syndicate.xcodeproj/project.pbxproj')
    replace_values('lite', get_project_folder(arg_parser) + 'ios/info.lite.plist')
    replace_values('pro', get_project_folder(arg_parser) + 'ios/info.pro.plist')
    copy_resources(arg_parser)
