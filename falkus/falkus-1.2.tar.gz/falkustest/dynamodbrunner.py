import os
import logging
import subprocess
import time
import socket
from contextlib import closing

DYNAMO_DB_URL = "https://s3.eu-central-1.amazonaws.com/dynamodb-local-frankfurt/dynamodb_local_latest.zip"


class DynamoDbRunner:

    def __init__(self, dynamodb_path=".", port=8000, max_port_to_try=None, ddbargs=("-inMemory",)):
        self._installation_path = dynamodb_path
        self._ddb_path = os.path.join(self._installation_path, "dynamodb")
        self._ddb_lib_path = os.path.join(self._ddb_path, "DynamoDBLocal_lib")
        self._ddb_jar_path = os.path.join(self._ddb_path, "DynamoDBLocal.jar")
        self._ddb_args = [a.strip() for a in ddbargs]
        if "-port" in self._ddb_args:
            raise Exception("dynamodb port must be specifyed using the dedicated argument")
        self._port = port
        self._max_port_to_try = max_port_to_try
        self.p = None

    def get_endpoint(self):
        return "http://localhost:{}".format(self._port)

    def run(self):
        self._install_dynamo_db()
        self._check_port()
        call_args = ["java",
                     "-Djava.library.path={}".format(self._ddb_lib_path),
                     "-jar",
                     "{}".format(self._ddb_jar_path),
                     "-port",
                     str(self._port)
                     ]
        call_args.extend(self._ddb_args)
        logging.info("starting dynamodb with command: %s", " ".join(call_args))
        self.p = subprocess.Popen(call_args)
        self._wait_for_dynamodb()
        if self.p.poll():
            raise Exception("dynamodb terminated unexpectedly")

    def shutdown(self):
        logging.info("terminating dynamodb")
        if self.p.poll():
            raise Exception("dynamodb terminated unexpectedly before shutdown "
                            "- you might have used another dynamodb")
        self.p.terminate()

    def __enter__(self):
        self.run()

    def __exit__(self, exc_type, exc_value, traceback):
        self.shutdown()

    def _check_port(self):
        logging.info("checking port %d", self._port)
        while True:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                try:
                    s.bind(('', self._port))
                    logging.info("port available %d", self._port)
                    return
                except Exception:
                    if self._max_port_to_try and self._max_port_to_try > self._port:
                        self._port += 1
                    else:
                        raise Exception("could not start dynamodb because port %d is busy", self._port)

    def _wait_for_dynamodb(self):
        logging.info("waiting for dynamodb accepting connection on port %d", self._port)
        for i in range(1, 100):
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                try:
                    s.connect(("127.0.0.1", self._port))
                    return
                except Exception:
                    time.sleep(0.1)

    def _install_dynamo_db(self):
        if os.path.isdir(self._ddb_path) and os.path.isfile(self._ddb_jar_path):
            logging.info("dynamodb already available in %s", self._ddb_jar_path)
            return
        if os.path.isdir(self._ddb_path):
            logging.error("could not install dynamodb in %s, path already exists", self._ddb_path)
            raise Exception("dynamodb installation error")
        if not os.path.isdir(self._installation_path):
            os.makedirs(self._installation_path)
        zippath = os.path.join(self._installation_path, "dynamodb.zip")
        if not os.path.isfile(zippath):
            _download(DYNAMO_DB_URL, zippath)
        _unzip(zippath, self._ddb_path)
        _rm(zippath)


def _download(url, output_file):
    import requests
    logging.info("downloading %s to %s", url, output_file)
    r = requests.get(url)
    with open(output_file, "wb") as handle:
        for data in r.iter_content():
            handle.write(data)


def _unzip(zip_file, path=None):
    import zipfile
    logging.info("unzipping %s to %s", zip_file, path if path else "the same directory")
    with zipfile.ZipFile(zip_file, 'r') as z:
        if path:
            z.extractall(path)
        else:
            z.extractall()


def _rm(file_path):
    logging.info("removing file %s", file_path)
    os.remove(file_path)
