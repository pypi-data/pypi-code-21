# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from boto import sqs
from boto.s3.connection import S3Connection, OrdinaryCallingFormat
from boto.sqs.message import Message, RawMessage
from boto.s3.key import Key
from boto.s3 import connect_to_region

from base64 import b64decode
import json
import os
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


TEMP_DIR = '/tmp'


class MensagemFormatoIncorreto(Exception):
    pass


class Fila(object):
    def __init__(self, sqs_queue, raw_message=True):
        """Inicializa um objeto Balde.

        s3_queue -- Objeto Queue de conexão com SQS através da biblioteca boto.
        """
        self.sqs_queue = sqs_queue
        self.mensagem = None
        self.mensagem_processada = None
        self.raw_message = raw_message
        self.mensagem_atual = None

    def receber_mensagem(self, quantidade=1):
        """Recebe uma mensagem do Amazon SQS."""
        resposta = self.sqs_queue.get_messages(quantidade)
        if len(resposta):
            self.mensagem = resposta
            logger.debug('Total de mensagens recebidas: %s' % len(resposta))
            return len(resposta)
        logger.error('Não há resposta para ser recebida.')
        return False

    def processar_mensagem(self):
        """Processa a mensagem trasnformando-a em um dicionário."""
        mensagem = self.mensagem[0].get_body()
        self.mensagem_atual = self.mensagem[0]
        try:
            self.mensagem_processada = json.loads(mensagem)
        except:
            try:
                mensagem = b64decode(mensagem)
            except Exception:
                logger.error('Mensagem nao foi decodificada.')

            try:
                self.mensagem_processada = json.loads(mensagem)
                logger.debug('Mensagem processada: %s' % self.mensagem_processada)
            except Exception, e:
                self.excluir_mensagem()
                raise MensagemFormatoIncorreto(e)

        self.mensagem.pop(0)

    def send_message(self, message):
        msg = self.raw_message == True and RawMessage() or Message()
        try:
            message = json.dumps(message)
        except:
            return False
        msg.set_body(message)
        status = self.sqs_queue.write(msg)

        return status

    def excluir_mensagem(self):
        """Exclui a mensagem da fila."""
        if self.mensagem_atual:
            self.sqs_queue.delete_message(self.mensagem_atual)
            logger.debug(u'Mensagem excluída da fila.')


class Balde(object):
    def __init__(self, s3_bucket):
        """Inicializa um objeto Balde.

        s3_bucket -- Objeto Bucket de conexão com S3 através da biblioteca boto.
        """
        self.s3_bucket = s3_bucket

    def get(self, filename):
        """Faz download de um arquivo do S3 e retorna um `file`.

        O arquivo é salvo temporáriamente no TEMP_DIR e `file` retornado
        aponta para este arquivo.
        """
        key = Key(self.s3_bucket)
        key.key = filename
        os_filename = os.path.join(TEMP_DIR, filename.replace('/', '_'))
        key.get_contents_to_filename(os_filename)
        f = open(os_filename)
        return f

    def put(self, f, filename, public=True):
        """Faz upload de um arquivo para o S3.

        f -- `file` apontando para o arquivo que será enviado.
        filename -- Nome do arquivo no S3.
        """
        logger.debug('Escrevendo arquivo no S3: ("%s")' % filename)

        if type(f) != file:
            f = open(f)

        key = Key(self.s3_bucket)
        key.key = filename
        key.set_contents_from_file(f)
        if public:
            key.make_public()
        return True

    def delete(self, filename):
        """Remove um arquivo do S3.

        filename -- Nome do arquivo no S3.
        """
        logger.debug('Removendo arquivo no S3: ("%s")' % filename)
        self.s3_bucket.delete_key(filename)
        return True

    def delete_keys(self, keys):
        """Deleta varias chaves ao mesmo tempo"""
        return self.s3_bucket.delete_keys(keys)

    def rename(self, actual, new):
        """Renomeia o arquivo para S3.

        actual -- Nome atual do arquivo no S3.
        new -- Novo nome do arquivo no S3.
        """
        logger.debug('Renomeando o arquivo no S3: ("%s" -> "%s")' % (actual, new))
        key = Key(self.s3_bucket)
        key.key = actual
        key.copy(self.s3_bucket.name, new)

        self.s3_bucket.delete_key(actual)
        return True

    def list(self, prefix):
        """Retorna uma lista contendo o nome das chaves do
        list do boto"""
        return [x.name for x in self.s3_bucket.list(prefix=prefix)]


class AWS(object):
    sqs = False
    bucket = False

    def __init__(self, queue=False, bucket=False,
                 raw_message=True, region='sa-east-1'):

        if queue:
            self.AWS_SQS_QUEUE = queue
        if bucket:
            self.AWS_S3_BUCKET = bucket

        if region:
            self.AWS_REGION = region
        else:
            self.AWS_REGION = 'us-east-1'

        self.raw_message = raw_message

    def connect_sqs(self, nome_fila):
        """Conecta ao Amazon SQS e retorna um objeto Queue."""
        conn = sqs.connect_to_region(region_name=self.AWS_REGION)
        queue = conn.get_queue(nome_fila)
        queue.set_message_class(self.raw_message == True and RawMessage or Message)

        logger.debug('Conectado ao Amazon SQS.')

        return queue

    def connect_s3(self, bucket_name=None):
        """Conecta ao Amazon S3 e retorna um objeto Bucket."""
        conn = connect_to_region(region_name='us-east-1', is_secure=True, calling_format=OrdinaryCallingFormat())

        # us-east-1
        bucket = conn.get_bucket(bucket_name or self.AWS_S3_BUCKET)

        logger.debug('Conectado ao Amazon S3.')

        return bucket

    def get_fila(self, nome_fila):

        return Fila(self.connect_sqs(nome_fila), raw_message=self.raw_message)

    def get_balde(self, bucket_name):

        return Balde(self.connect_s3(bucket_name))
