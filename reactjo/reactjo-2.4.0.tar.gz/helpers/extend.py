import os, subprocess
from helpers.worklist import worklist as wl
from helpers.compose import paint

def extend():
    src = 'https://github.com/aaron-price/reactjo-extension-template.git'
    target = os.getcwd()
    rc_home = ""
    out_home = ""
    LATEST_VERSION = '2.4.0'

    while rc_home == "":
        rc_home = input(paint("Please name your extension (e.g. reactjo_django): "))
    while out_home == "":
        out_home = input(paint("What will the main output directory be called (e.g. backend, frontend, etc): "))

    ext_path = target + '/' + rc_home
    subprocess.run([ 'git', 'clone', '-b', 'v' + LATEST_VERSION, src, rc_home ])

    os.chdir(os.path.join(rc_home))
    subprocess.run(['git','remote', 'rm', 'origin'])

    # Update the extension_constants
    extension_constants_string = """
        # file_manager('$out/some/path') == 'super_root/project_path/{out}/some/path'
        OUTPUT_HOME = '{out}'

        # file_manager('$rc/assets') == 'super_root/reactjorc/extensions/{rc}/assets'
        RC_HOME = '{rc}'
    """.format(
        out=out_home,
        rc=rc_home
    ).replace('    ','')
    extension_constants_path = os.path.join('helpers/extension_constants.py')
    file = open(extension_constants_path, 'w')
    file.write(extension_constants_string)
    file.close()

    # Fill in the readme constants
    readme_path = os.path.join('README.md')
    readme_file = open(readme_path, 'r').read()
    readme_file = readme_file.replace('extension_name_here', rc_home)
    file = open(readme_path, 'w')
    file.write(readme_file)
    file.close()

    # Fill in the --version cmd in entry.py
    entry_path = os.path.join('entry.py')
    entry_file = open(entry_path, 'r').read()
    entry_file = entry_file.replace('extension_name_here', rc_home)
    file = open(entry_path, 'w')
    file.write(entry_file)
    file.close()

    # Fill in the 'writing an extension' constants
    howto_path = os.path.join('WRITING_AN_EXTENSION.md')
    howto_file = open(howto_path, 'r').read()
    howto_file = howto_file.replace('extension_name_here', rc_home)
    file = open(howto_path, 'w')
    file.write(howto_file)
    file.close()

    wl('Built an extension')
