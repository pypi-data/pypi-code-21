import csv
import os
import click
from YaDiskClient.YaDiskClient import YaDisk
from concurrent.futures import ThreadPoolExecutor, wait
from time import sleep

from mc_tools.cli import cli
from mc_tools.config.config import conf


class CertPublisher:
    def __init__(self, src_file_csv, ya_dir):
        self.src_file_csv = src_file_csv
        self.ya_dir = ya_dir

        self.ya = YaDisk(conf['ya']['login'], conf['ya']['pass'])
        self.certs = {
            c['displayname'].split(".")[0]: c['path']
            for c in self.ya.ls('/{}'.format(ya_dir))
        }

    def share_cert_for(self, name):
        retries = 0
        while retries <= 5:
            retries += 1
            try:
                cert = self.certs[name]
                return self.ya.publish_doc(cert)
            except Exception as e:
                click.echo(repr(e))
                sleep(1)
        return "###"

    def process_one(self, client, clients_processed):
        name, mail = client[:2]
        name = name.strip("'")
        mail = mail.strip("'")
        ref = self.share_cert_for(name)
        res = (name.strip(), mail, ref)
        click.echo(res)
        clients_processed.append(res)

    def publish(self):
        # Read & schedule
        executor = ThreadPoolExecutor(max_workers=10)
        tasks = []
        clients_processed = []
        with open(self.src_file_csv) as inp:
            reader = csv.reader(inp, delimiter=',')
            for client in reader:
                tasks.append(executor.submit(self.process_one,
                                             client, clients_processed))
        # Execute
        wait(tasks)
        click.echo("Processed {} certs".format(len(tasks)))
        # Write out
        out_path = os.path.join(
            os.path.dirname(self.src_file_csv),
            os.path.basename(self.src_file_csv).split(".")[0] + "_done.csv"
        )
        with open(out_path, "w") as out:
            writer = csv.writer(out, delimiter=',')
            for p in clients_processed:
                writer.writerow(p)
        return out_path


@cli.command()
@click.argument('src_file_csv', type=click.Path(exists=True))
@click.argument('ya_dir')
def publish(src_file_csv, ya_dir):
    click.echo("##### Sharing certs from '{}'".format(src_file_csv))
    click.echo("##### Yandex certs dir: '{}'".format(ya_dir))
    out_path = CertPublisher(src_file_csv, ya_dir).publish()
    click.echo("##### Done: {}".format(out_path))
