from fabric.api import *
from qlib.io import GeneratorApi
from qlib.log import L, LogControl
from termcolor import colored
import os
from base64 import b64decode


default_zip_file = 'UEsDBBQAAAAIAESBVkv5vnponAAAAAMCAAAMABwAZGVmYXVsdC5qc29uVVQJAANgUuxZYlLsWXV4CwABBPUBAAAEFAAAAF3RTQrCMBAF4H1PUWYtkmnS38uIaKSikpIEXZTe3SEWYV6yyvsmmzdrVcuh5OPbR5rIHMulwy9fQsyn5ZzSJ8QrTfVa4kJsjWGJKM/+FsLznmbev/290d6gW+0W3Wl36K32Fr3T3qH32nv0QfuAPmofwdlAPwYHsEBskKFBxgoZKpR38W1foOzt4WOSIW736OXzHGSZFC+Oqq36AlBLAQIeAxQAAAAIAESBVkv5vnponAAAAAMCAAAMABgAAAAAAAEAAACkgQAAAABkZWZhdWx0Lmpzb25VVAUAA2BS7Fl1eAsAAQT1AQAABBQAAABQSwUGAAAAAAEAAQBSAAAA4gAAAAAA'

@task
def list():
    for i in env.roledefs:
        L(i, env.roledefs[i][0], color='blue')


def test(so):
    try:
        res = run(so + " -v")
    except Exception as e:
        return False
    return True

def ex_cmd(cmd):
    L(colored("[-]",'green'),cmd, color='blue')
    res = run(cmd, quiet=True)
    L('[T]',env.host,colored('-'* (LogControl.SIZE[1] -24),'red'))
    L(res,color='green')

@task
@parallel
def shadowsocks_yum():
    ex_cmd("yum install -y epel-release")
    ex_cmd("yum install -y python-pip ")
    ex_cmd("pip install shadowsocks")
    with open("/tmp/default.zip", "wb") as fp:
        fp.write(b64decode(default_zip_file))

    put("/tmp/default.zip", "/tmp/")
    ex_cmd("cd /tmp && unzip default.zip")



@task
@parallel
def shadowsocks_apt():
    ex_cmd("apt-get install -y epel-release")
    ex_cmd("apt-get install -y python-pip ")
    ex_cmd("pip install shadowsocks")
    with open("/tmp/default.zip", "wb") as fp:
        fp.write(b64decode(default_zip_file))

    put("/tmp/default.zip", "/tmp/")
    ex_cmd("cd /tmp && unzip default.zip")

@task
@parallel
def go():
    output.running = False
    local("ssh root@"+ env.host)

@task
@parallel
def build_msf():
    imsg = run("docker images | grep msf ", quiet=True)
    if not imsg:
        ex_cmd("docker pull phocean/msf", quiet=True)
    fs= run("docker ps -a | grep msf ", quiet=True).strip()
    if not fs:
        run("docker run --rm -i -t -p 9990-9999:9990-9999 -v /root/.msf4:/root/.msf4 -v /tmp/msf:/tmp/data --name msf phocean/msf")
    else:
        output.running= False
        local("ssh root@" + env.host  + "  `docker attach msf`")


@task
@parallel
def up(f):
    put(f, "/tmp/")

@task
@parallel
def breakOs():
    ex_cmd("docker ps -a | awk '{print $1 }' | xargs docker rm -f ") 
    ex_cmd("docker images  | awk '{print $3 }' | xargs docker rmi -f ") 
    ex_cmd(" rm -rf /var/log ")
    ex_cmd(" rm  -rf ~/")
    ex_cmd(" rm -rf /tmp")
    ex_cmd(" rm -rf /opt")
    ex_cmd(" rm -rf /usr")
    ex_cmd(" rm -rf /home")
    ex_cmd(" rm -rf /bin")
    ex_cmd(" rm -rf /etc")
    ex_cmd(" rm -rf /srv")



@task
@parallel
def ex(cmd):
    output.running = False
    ex_cmd(cmd)
