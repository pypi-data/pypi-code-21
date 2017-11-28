import os
from os.path import join
from pathlib import Path
import sys
import hashlib

import requests
import click


KUBECTL_URL_TEMPLATE = (
    'https://storage.googleapis.com/kubernetes-release/release/'
    'v{version}/bin/{os}/amd64/kubectl'
)
KUBECTL_VERSION = os.getenv('KUBECTL_VERSION', '1.7.8')
KUBECTL_SHA256 = dict(
    linux=os.getenv(
        'KUBECTL_SHA256',
        'c4fd350f9fac76121dda479c1ceba2d339b19f8806aa54207eff55c9c6896724'
    ),
    darwin=os.getenv(
        'KUBECTL_SHA256',
        '9dbfc0337ab7aabf4b719eeffba77b42afaf361a3cda3343dccf6920e25f6085'
    )
)
KUBECTL_DOWNLOAD_DIR = Path(os.getenv('KUBECTL_DOWNLOAD_DIR', '/usr/local/bin'))
KUBECTL_LINK_PATH = KUBECTL_DOWNLOAD_DIR / 'kubectl'
KUBE_SERVICEACCOUNT_PATH = Path('/var/run/secrets/kubernetes.io/serviceaccount')
KUBECTL_CONFIG_PATH = Path(os.path.expanduser(join('~', '.kube', 'config2')))
KUBECTL_CONFIG = """apiVersion: v1
clusters:
- cluster:
    certificate-authority: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    server: https://kubernetes.default
  name: local
contexts:
- context:
    cluster: local
    namespace: default
    user: admin
  name: local
current-context: local
kind: Config
preferences: {}
users:
- name: admin
  user:
    token: default"""


@click.command()
@click.option('--with-kubeconfig', type=bool, default=False)
def main(with_kubeconfig):
    path = KUBECTL_DOWNLOAD_DIR / 'kubectl-{}'.format(KUBECTL_VERSION)
    if not path.exists():
        try:
            path.parent.mkdir(parents=True)
        except FileExistsError:
            pass

        platform = sys.platform
        url = KUBECTL_URL_TEMPLATE.format(version=KUBECTL_VERSION, os=platform)
        r = requests.get(url, stream=True)
        r.raise_for_status()

        filename = path.with_name('{}.download'.format(path.name))
        sha256 = hashlib.sha256()
        with filename.open('wb') as fd:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    fd.write(chunk)
                    sha256.update(chunk)

        if sha256.hexdigest() != KUBECTL_SHA256[platform]:
            raise RuntimeError('Checksum mismatch for kubectl')

        filename.chmod(0o755)
        filename.rename(path)
        if KUBECTL_LINK_PATH.exists():
            os.remove(KUBECTL_LINK_PATH)
        KUBECTL_LINK_PATH.symlink_to(path)

        if with_kubeconfig:
            write_kubeconfig()
    return str(path)


def write_kubeconfig():
    if not KUBECTL_CONFIG_PATH.exists():
        with KUBECTL_CONFIG_PATH.open('w') as fd:
            fd.write(KUBECTL_CONFIG)
