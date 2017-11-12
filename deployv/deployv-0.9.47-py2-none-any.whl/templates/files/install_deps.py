import subprocess
import shlex
import os
from reqgen import reqgen


def create_user():
    """ Creates the odoo user inside the container without password and then
        changes the password for the root user to odoo.
    """
    commands = ['adduser --home=/home/odoo --disabled-password --gecos "" --shell=/bin/bash odoo',
                'echo "root:odoo" | chpasswd']
    for command in commands:
        subprocess.check_call(shlex.split(command))


def entry_point():
    """ Downloads the entrypoint used as command for any container created with this image
        and gives execution permissions to it.
    """
    commands = [('wget -q -O /entry_point.py https://raw.githubusercontent.com/'
                 'vauxoo/docker_entrypoint/master/entry_point.py'),
                'chmod +x /entry_point.py']
    for command in commands:
        subprocess.check_call(shlex.split(command))


def install_apt_requirements():
    """ Reads the apt_dependencies.txt file copied by the dockerfile in /tmp and parses it to
    install all the apt dependencies inside the container
    """
    with open('/tmp/apt_dependencies.txt', 'r') as fileobj:
        deps = fileobj.readlines()
    for dep in deps:
        cmd = 'apt-get install {name} -yq'.format(name=dep.strip('\n'))
        subprocess.check_call(shlex.split(cmd))


def install_requirements():
    """ Gathers the requirements from all the requirements.txt files it can find in
        the folder where all the repos are with the help of reqgen,
        merges them into one single requirements.txt, and installs them.
    """
    reqgen.generate_merged_file('/home/odoo/full_requirements.txt', '/home/odoo/instance')
    subprocess.check_call(shlex.split('pip install -r /home/odoo/full_requirements.txt'))


def create_paths():
    """ Creates the directories, and intermediate paths if needed, for some of the
        files that will be copied in the image.
    """
    paths = ['/home/odoo/.ssh', '/home/odoo/.local/share', '/var/log/supervisor']
    for path in paths:
        try:
            os.makedirs(path)
        except OSError as error:
            if 'File exists' not in error.strerror:
                raise


def main():
    """ Main method in charge of following the logic required to set up the needed directories,
        install the python dependencies and set the addons path in the odoo config file.
    """
    create_user()
    create_paths()
    entry_point()
    install_apt_requirements()
    install_requirements()
    commands = ['python /home/odoo/getaddons.py /home/odoo/instance/extra_addons',
                'chown -R odoo:odoo /home/odoo']
    for command in commands:
        subprocess.check_call(shlex.split(command))

if __name__ == "__main__":
    main()
