# -*- coding: utf-8 -*-
import MySQLdb
import logging
import re
from django.db import transaction
from system.models import Configuration
from physical.models import Instance
from models import EnvironmentAttr, DatabaseInfraAttr

LOG = logging.getLogger(__name__)

SGBD_MYSQL = 'M'
SGBD_MONGODB = 'G'
SGBD_REDIS = 'R'
CHANGE_INSTANCE_STATUS_SINGLE = """
    UPDATE dbmonitor_database SET ativo = {} WHERE id = {}
    """
CHANGE_INSTANCE_STATUS_HA = """
    UPDATE dbmonitor_instancia SET ativo = {}
    WHERE database_id = {} AND maquina = '{}'
    """

BAREMETAL = '1'
VIRTUALMACHINE = '2'

class DBMonitorProvider(object):

    @classmethod
    def get_credentials(self, environment):
        LOG.info("Getting credentials...")
        from dbaas_credentials.credential import Credential
        from dbaas_credentials.models import CredentialType
        integration = CredentialType.objects.get(type=CredentialType.DBMONITOR)
        return Credential.get_credentials(environment=environment, integration=integration)

    @classmethod
    def auth(self, environment):
        try:
            LOG.info("Conecting with dbmonitor...")
            credentials = self.get_credentials(environment=environment)
            self.DECODE_KEY = credentials.secret
            endpoint, database = credentials.endpoint.split('/')
            host, port = endpoint.split(':')
            connection_timeout_in_seconds = Configuration.get_by_name_as_int(
                'mysql_connect_timeout', default=5)
            self.client = MySQLdb.connect(host=host, port=int(port),
                                          user=credentials.user, passwd=credentials.password,
                                          db=database, connect_timeout=connection_timeout_in_seconds)
            LOG.debug('Successfully connected to mysql %s' %
                      (credentials.endpoint))
        except Exception, e:
            LOG.error(str(e))
            raise e

    @classmethod
    def get_sgbd(self, databaseinfra):
        driver_name = databaseinfra.engine.engine_type.name.lower()
        if re.match(r'^mongo.*', driver_name):
            return SGBD_MONGODB
        elif re.match(r'^mysql.*', driver_name):
            return SGBD_MYSQL
        elif re.match(r'^redis.*', driver_name):
            return SGBD_REDIS
        else:
            LOG.error('Not implemented engine type')
            raise NotImplementedError()

    @classmethod
    def create_instance(self, cursor, databaseinfra, dbmonitor_infraid, instance, instance_number, tipo_mongodb='2'):
        sgbd = self.get_sgbd(databaseinfra)
        instance_dict = {
            'database_id': dbmonitor_infraid,
            'nome': databaseinfra.name[:48] + '-' + str(instance_number),
            'maquina': instance.hostname,
            'dns': instance.dns,
            'porta': instance.port,
            'ativo': 'true',
            'tipo_mongodb': tipo_mongodb,
            'disk_path': '/data',
            'tipo_maquina': VIRTUALMACHINE,
        }

        if sgbd == SGBD_MONGODB:
            sql = """INSERT INTO dbmonitor_instancia (database_id, nome, maquina, dns, porta, ativo, tipo_mongodb, disk_path, tipo_maquina)
                    VALUES (%(database_id)s, '%(nome)s', '%(maquina)s', '%(dns)s', '%(porta)s', %(ativo)s, '%(tipo_mongodb)s', '%(disk_path)s', '%(tipo_maquina)s')
            """ % instance_dict
        else:
            sql = """INSERT INTO dbmonitor_instancia (database_id, nome, maquina, dns, porta, ativo, disk_path, tipo_maquina)
                    VALUES (%(database_id)s, '%(nome)s', '%(maquina)s', '%(dns)s', '%(porta)s', %(ativo)s, '%(disk_path)s', '%(tipo_maquina)s')
            """ % instance_dict

        cursor.execute(sql)

    @classmethod
    @transaction.commit_on_success
    def create_dbmonitor_instance_monitoring(self, instance, instance_number):
        LOG.info('Creating monitoring on DBMonitor for instance')
        databaseinfra = instance.databaseinfra
        environment = databaseinfra.environment

        try:
            self.auth(environment)
            cursor = self.client.cursor()
            infraattr = DatabaseInfraAttr.objects.get(
                dbaas_databaseinfra=databaseinfra)

            self.create_instance(
                cursor=cursor,
                databaseinfra=databaseinfra,
                dbmonitor_infraid=infraattr.dbmonitor_databaseinfra,
                instance=instance,
                instance_number=instance_number,
            )

            self.client.commit()

        except Exception, e:
            LOG.error(str(e))
            raise e

    @classmethod
    @transaction.commit_on_success
    def create_dbmonitor_monitoring(self, databaseinfra):

        LOG.info('Creating monitoring on DBMonitor')
        environment = databaseinfra.environment
        sgbd = self.get_sgbd(databaseinfra)
        if sgbd == SGBD_REDIS:
            instances = databaseinfra.instances.filter(
                instance_type=Instance.REDIS)
        else:
            instances = databaseinfra.instances.all()
        if len(instances) == 1:
            flag_cluster_str = 'false'
            flag_cluster = False
            machine = instances[0].hostname
        else:
            flag_cluster_str = 'true'
            flag_cluster = True
            machine = ''

        if sgbd == SGBD_MYSQL:
            dns, port = databaseinfra.endpoint_dns.split(':')
            replicasetname = ''
        elif sgbd == SGBD_REDIS:
            dns, port = databaseinfra.get_driver().get_dns_port()
            replicasetname = ''
        elif sgbd == SGBD_MONGODB:
            dns, port = databaseinfra.get_driver().get_dns_port()
            replicasetname = databaseinfra.get_driver().get_replica_name()
            if replicasetname is None:
                replicasetname = ''

        self.auth(environment)

        tipo = EnvironmentAttr.objects.get(
            dbaas_environment=environment).dbmonitor_environment

        sql = """INSERT INTO dbmonitor_database ( nome, maquina, sgbd, tipo, dns, porta, versao, usuario, senha,
                             ativo, flag_cluster, coleta_info_sessoes, coleta_info_tablespaces, coleta_info_segmentos,
                             coleta_info_backup, coleta_info_key_buffer, testa_conexao, coleta_tamanho_database,
                             flag_autenticacao, testa_replicacao, testa_lock, replicaset,
                             disk_path, tipo_maquina, dbaas )
                 VALUES (
                 '%(nome)s', '%(maquina)s', '%(sgbd)s', '%(tipo)s', '%(dns)s', '%(porta)s', '%(versao)s', '%(usuario)s',
                 encode('%(senha)s', '%(decodekey)s'),
                 %(ativo)s, %(flag_cluster)s, %(coleta_info_sessoes)s, %(coleta_info_tablespaces)s, %(coleta_info_segmentos)s,
                 %(coleta_info_backup)s, %(coleta_info_key_buffer)s, %(testa_conexao)s, %(testa_lock)s, %(coleta_tamanho_database)s,
                 %(flag_autenticacao)s, %(testa_replicacao)s, '%(replicaset)s',
                 '%(disk_path)s', '%(tipo_maquina)s', %(dbaas)s
                 )
        """ % {
            'nome': databaseinfra.name[:50],
            'maquina': machine,
            'sgbd': sgbd,
            'tipo': tipo,
            'dns': dns,
            'porta': port,
            'versao': databaseinfra.engine.version,
            'usuario': databaseinfra.user,
            'senha': databaseinfra.password,
            'decodekey': self.DECODE_KEY,
            'ativo': 'true',
            'flag_cluster': flag_cluster_str,
            'coleta_info_sessoes': 'true',
            'coleta_info_tablespaces': 'false',
            'coleta_info_segmentos': 'false',
            'coleta_info_backup': 'true',
            'coleta_info_key_buffer': 'false',
            'testa_conexao': 'true',
            'coleta_tamanho_database': 'true',
            'flag_autenticacao': 'true',
            'testa_replicacao': 'true',
            'testa_lock': 'true',
            'replicaset': replicasetname,
            'disk_path': '/data',
            'tipo_maquina': VIRTUALMACHINE,
            'dbaas': 'true'
        }

        try:
            cursor = self.client.cursor()
            cursor.execute(sql)
            dbmonitor_infraid = self.client.insert_id()

            if flag_cluster:
                instance_number = 0
                for instance in instances:
                    instance_number += 1
                    tipo_mongodb = ''
                    if instance_number == 1:
                        tipo_mongodb = '1'
                    elif instance_number == 3:
                        tipo_mongodb = '7'
                    else:
                        tipo_mongodb = '2'

                    self.create_instance(
                        cursor=cursor,
                        databaseinfra=databaseinfra,
                        dbmonitor_infraid=dbmonitor_infraid,
                        instance=instance,
                        instance_number=instance_number,
                        tipo_mongodb=tipo_mongodb)
            self.client.commit()
            dbinfraattr = DatabaseInfraAttr(
                dbaas_databaseinfra=databaseinfra, dbmonitor_databaseinfra=dbmonitor_infraid)
            dbinfraattr.save()
            LOG.info('Monitoring in DBMonitor successfully created')
        except Exception, e:
            LOG.error(str(e))
            raise e

    @classmethod
    @transaction.commit_on_success
    def remove_dbmonitor_monitoring(self, databaseinfra):

        LOG.info('Removing monitoring on DBMonitor')

        try:
            self.auth(databaseinfra.environment)
            infraattr = DatabaseInfraAttr.objects.get(
                dbaas_databaseinfra=databaseinfra)

            cursor = self.client.cursor()
            sql = "UPDATE dbmonitor_database SET ativo = false WHERE id = %s" % (
                infraattr.dbmonitor_databaseinfra)
            cursor.execute(sql)
            sql = "UPDATE dbmonitor_instancia SET ativo = false WHERE database_id = %s" % (
                infraattr.dbmonitor_databaseinfra)
            cursor.execute(sql)
            self.client.commit()

            infraattr.delete()

        except Exception, e:
            LOG.error(str(e))
            raise e

        LOG.info('Monitoring in DBMonitor successfully removed')

    @classmethod
    @transaction.commit_on_success
    def register_backup(self, databaseinfra, start_at, end_at, size, status, type, error):

        from backup.models import BackupInfo

        LOG.info('Registering backup on DBMonitor')
        self.auth(databaseinfra.environment)
        infraattr = DatabaseInfraAttr.objects.get(
            dbaas_databaseinfra=databaseinfra)
        sgbd = self.get_sgbd(databaseinfra)

        if type == BackupInfo.SNAPSHOPT:
            tipo_backup = 'snapshot'
        else:
            raise Exception("Unknown backup type")

        if status == BackupInfo.SUCCESS:
            status_backup = 'COMPLETO'
        elif status == BackupInfo.WARNING:
            status_backup = 'COMPLETO COM ERROS'
        else:
            status_backup = 'FALHA'

        if error is None:
            error = ''

        backup_dict = {
            'database_id': infraattr.dbmonitor_databaseinfra,
            'data_inicio': start_at.strftime("%y-%m-%d %H:%M:%S"),
            'data_fim': end_at.strftime("%y-%m-%d %H:%M:%S"),
            'segundos_decorrido': int((end_at - start_at).total_seconds()),
            'bytes_saida': size,
            'status_backup': status_backup,
            'tipo_backup': tipo_backup,
            'info_adicional': error,
            'compactado': 'false'
        }

        if sgbd == SGBD_MYSQL:
            sql = """INSERT INTO mysql_backup (database_id, data_inicio, data_fim, segundos_decorrido, bytes_saida, status_backup, tipo_backup)
                     VALUES (%(database_id)s, '%(data_inicio)s', '%(data_fim)s', %(segundos_decorrido)s, %(bytes_saida)s, '%(status_backup)s', '%(tipo_backup)s')
            """ % backup_dict
        elif sgbd == SGBD_MONGODB:
            sql = """INSERT INTO mongodb_backup (database_id, data_inicio, data_fim, segundos_decorrido, bytes_saida, status_backup, tipo_backup, info_adicional, compactado)
                     VALUES (%(database_id)s, '%(data_inicio)s', '%(data_fim)s', %(segundos_decorrido)s, %(bytes_saida)s, '%(status_backup)s', '%(tipo_backup)s', "%(info_adicional)s", %(compactado)s)
            """ % backup_dict
        elif sgbd == SGBD_REDIS:
            sql = """INSERT INTO redisdb_backup (database_id, data_inicio, data_fim, segundos_decorrido, bytes_saida, status_backup, tipo_backup, info_adicional)
                     VALUES (%(database_id)s, '%(data_inicio)s', '%(data_fim)s', %(segundos_decorrido)s, %(bytes_saida)s, '%(status_backup)s', '%(tipo_backup)s', "%(info_adicional)s")
            """ % backup_dict

        try:

            cursor = self.client.cursor()
            cursor.execute(sql)
            self.client.commit()

        except Exception, e:
            LOG.error(str(e))
            raise e

        LOG.info('Backup successfully registered on DBMonitor')

    @classmethod
    @transaction.atomic
    def insert_extra_dns(self, database, extra_dns):
        LOG.info('Inserting new extra dns {} for database {}'.format(extra_dns,
                                                                     database))

        databaseinfra = database.databaseinfra
        databaseinfra_attr = DatabaseInfraAttr.objects.get(dbaas_databaseinfra=databaseinfra)

        default_sql = """INSERT INTO dbmonitor_dnsadicional(database_id, dns) VALUES({}, '{}')"""
        custom_sql = default_sql.format(databaseinfra_attr.dbmonitor_databaseinfra,
                                        extra_dns)

        self.auth(databaseinfra.environment)
        try:
            cursor = self.client.cursor()
            cursor.execute(custom_sql)
            self.client.commit()

        except Exception, e:
            LOG.error(str(e))
            raise e

        LOG.info('Extra dns({}) inserted!'.format(extra_dns))

    @classmethod
    @transaction.atomic
    def remove_extra_dns(self, database, extra_dns):
        LOG.info('Removing extra dns {} for database {}'.format(extra_dns,
                                                                database))

        databaseinfra = database.databaseinfra
        databaseinfra_attr = DatabaseInfraAttr.objects.get(dbaas_databaseinfra=databaseinfra)

        default_sql = """DELETE FROM dbmonitor_dnsadicional WHERE database_id={} AND dns='{}'"""
        custom_sql = default_sql.format(databaseinfra_attr.dbmonitor_databaseinfra,
                                        extra_dns)

        self.auth(databaseinfra.environment)
        try:
            cursor = self.client.cursor()
            cursor.execute(custom_sql)
            self.client.commit()

        except Exception, e:
            LOG.error(str(e))
            raise e

        LOG.info('Extra dns({}) deleted!'.format(extra_dns))

    @classmethod
    @transaction.commit_on_success
    def update_dbmonitor_database_version(self, databaseinfra, new_version):
        databaseinfra_attr = DatabaseInfraAttr.objects.get(dbaas_databaseinfra=databaseinfra)

        LOG.info('Updating DBMonitor database version')
        sql = """UPDATE dbmonitor_database
                 set versao = '%(versao)s'
                 WHERE id = '%(database_id)s'
        """ % {
            'versao': new_version,
            'database_id': databaseinfra_attr.dbmonitor_databaseinfra
        }

        try:
            self.auth(databaseinfra.environment)
            cursor = self.client.cursor()
            cursor.execute(sql)

            self.client.commit()
            LOG.info('DBMonitor database version successfully updated!')
        except Exception, e:
            LOG.error(str(e))
            raise e

    @classmethod
    @transaction.commit_on_success
    def update_instance_status(cls, instance, status):
        dbmonitor_infra = DatabaseInfraAttr.objects.get(
            dbaas_databaseinfra=instance.databaseinfra
        )
        if instance.databaseinfra.plan.is_ha:
            query = CHANGE_INSTANCE_STATUS_HA.format(
                status,
                dbmonitor_infra.dbmonitor_databaseinfra,
                instance.hostname.hostname
            )
        else:
            query = CHANGE_INSTANCE_STATUS_SINGLE.format(
                status, dbmonitor_infra.dbmonitor_databaseinfra
            )

        cls.auth(instance.databaseinfra.environment)
        cursor = cls.client.cursor()
        cursor.execute(query)
        cls.client.commit()

    @classmethod
    def disabled_dbmonitor_monitoring_instance(cls, instance):
        LOG.info(
            'Disabling monitoring to instance {} on DBMonitor'.format(
                instance.hostname.hostname
            )
        )

        try:
            cls.update_instance_status(instance, False)
        except Exception, e:
            LOG.error(str(e))
            raise e

        LOG.info(
            'Monitoring to instance {} is disabled on DBMonitor'.format(
                instance.hostname.hostname
            )
        )

    @classmethod
    def enabled_dbmonitor_monitoring_instance(cls, instance):
        LOG.info(
            'Enabling monitoring to instance {} on DBMonitor'.format(
                instance.hostname.hostname
            )
        )

        try:
            cls.update_instance_status(instance, True)
        except Exception, e:
            LOG.error(str(e))
            raise e

        LOG.info(
            'Monitoring to instance {} is enabled on DBMonitor'.format(
                instance.hostname.hostname
            )
        )

    @classmethod
    def get_dbmonitor_databaseinfra(cls, databaseinfra):
        dbmonitor_infras = DatabaseInfraAttr.objects.filter(
            dbaas_databaseinfra=databaseinfra
        )
        if len(dbmonitor_infras) == 1:
            return dbmonitor_infras[0].dbmonitor_databaseinfra
        return None
