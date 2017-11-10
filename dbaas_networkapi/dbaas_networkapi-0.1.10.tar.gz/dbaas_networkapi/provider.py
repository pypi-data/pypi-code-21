# -*- coding: utf-8 -*-

import logging
from networkapiclient.ClientFactory import ClientFactory
from networkapiclient.exception import NetworkAPIClientError
from models import Vip


LOG = logging.getLogger(__name__)


class NetworkProvider(object):
    def __init__(self, dbaas_api):
        self.dbaas_api = dbaas_api
        self.client = ClientFactory(
            networkapi_url=dbaas_api.endpoint,
            user=dbaas_api.user, password=dbaas_api.password
        )
        self.equipment_api = self.client.create_equipamento()
        self.environment_api = self.client.create_ambiente()
        self.ip_api = self.client.create_ip()
        self.vip_api = self.client.create_api_environment_vip()
        self.vip_api_request = self.client.create_api_vip_request()
        self.pool_api = self.client.create_pool()

    def _get_equipment_id(self, name):
        equipment = self.equipment_api.listar_por_nome(nome=name)
        return equipment['equipamento']['id']

    def _get_equipment_environment_id(self, equip_id):
        environment = self.environment_api.listar_por_equip(equip_id=equip_id)
        return environment['ambiente']['id']

    def _get_ip_id(self, ip, environment):
        ip = self.ip_api.buscar_por_ip_ambiente(ip=ip, id_environment=environment)
        return ip['ip']['id']

    def _get_ipv4_for_vip(self, vip_env_id, name):
        ipv4 = self.ip_api.get_available_ip4_for_vip(vip_env_id, name)
        return int(ipv4['ip']['id'])

    def create_vip(self, equipments, port, vip_dns):
        LOG.info("Creating VIP {}: {}".format(self.dbaas_api.finality, equipments))

        new_pool = {
            "environment": self.dbaas_api.environment_pool,
            "lb_method": self.dbaas_api.lb_method,
            "server_pool_members": [],
            "servicedownaction": self.dbaas_api.servicedownaction,
            "default_port": port,
            "healthcheck": {
                "healthcheck_type": self.dbaas_api.healthcheck_type,
                "destination": self.dbaas_api.destination,
                "healthcheck_expect": self.dbaas_api.healthcheck_expect,
                "identifier": "",
                "healthcheck_request": self.dbaas_api.healthcheck_request
            },
            "default_limit": self.dbaas_api.limit,
            "identifier": 'DBaaS_{}'.format(self.dbaas_api.databaseinfra.name)
        }

        for equipment in equipments:
            equipment.id = self._get_equipment_id(equipment.name)
            equipment.environment_id = self._get_equipment_environment_id(equipment.id)
            equipment.ip_id = self._get_ip_id(
                equipment.ip, equipment.environment_id
            )

            LOG.info('Equipment {}: {}'.format(equipment, equipment.__dict__))
            new_pool['server_pool_members'].append({
                "priority": self.dbaas_api.priority,
                "port_real": equipment.port,
                "identifier": equipment.name,
                "limit": self.dbaas_api.limit,
                "member_status": self.dbaas_api.member_status,
                "weight": self.dbaas_api.weight,
                "equipment": {
                    "id": int(equipment.id),
                    "nome": equipment.name
                },
                "ip": {
                    "ip_formated": equipment.ip,
                    "id": int(equipment.ip_id)
                },
                "ipv6": None,
                "id": None
            })

        pool = self.pool_api.save_pool(new_pool)
        pool_id = pool[0]['id']

        new_vip = {
            "business": self.dbaas_api.business,
            "environmentvip": self.dbaas_api.environment_vip,
            "ipv4": self._get_ipv4_for_vip(self.dbaas_api.environment_vip, vip_dns),
            "ipv6": None,
            "name": vip_dns,
            "options": {
                "cache_group": self.dbaas_api.cache_group,
                "persistence": self.dbaas_api.persistence,
                "timeout": self.dbaas_api.timeout,
                "traffic_return": self.dbaas_api.traffic_return,
            },
            "ports": [{
                "options": {
                    "l4_protocol": self.dbaas_api.l4_protocol,
                    "l7_protocol": self.dbaas_api.l7_protocol,
                },
                "pools": [{
                    "l7_rule": self.dbaas_api.l7_rule,
                    "l7_value": '',
                    "server_pool": pool_id
                }],
                "port": port
            }],
            "service": vip_dns.split('.')[0]
        }

        try:
            vip_db = self.vip_api_request.save_vip_request(new_vip)
            vip_id = vip_db[0]['id']
            LOG.info('Vip bd: %s', vip_db)
        except NetworkAPIClientError as e:
            self.delete_pool(pool_id)
            raise NetworkAPIClientError(str(e))
        except Exception as e:
            self.delete_pool(pool_id)
            raise Exception('Unexpected error on save_vip_request... ' + str(e))

        try:
            vip = self.vip_api_request.create_vip(vip_id)
            LOG.info('Vip equipment: %s', vip)
        except NetworkAPIClientError as e:
            self.delete_vip_request(vip_id)
            self.delete_pool(pool_id)
            raise NetworkAPIClientError(str(e))
        except Exception as e:
            self.delete_vip_request(vip_id)
            self.delete_pool(pool_id)
            raise Exception('Unexpected error on save_vip_request... ' + str(e))

        new_vip = Vip()
        new_vip.vip_id = vip_id
        new_vip.pool_id = pool_id
        new_vip.vip_ip = self.get_vip_ip(vip_id)
        new_vip.dscp = self.get_dscp(vip_id)
        new_vip.databaseinfra = self.dbaas_api.databaseinfra
        new_vip.save()

        return new_vip

    def delete_pool(self, pool_id):
        output = self.pool_api.delete_pool(pool_id)
        LOG.info('Removing pool {}: {}'.format(pool_id, output))

    def delete_vip_request(self, vip_id):
        output = self.vip_api_request.delete_vip_request(vip_id)
        LOG.info('Removing vip request {}: {}'.format(vip_id, output))

    def delete_vip(self, vip_ip):
        vip = Vip.objects.get(vip_ip=vip_ip)
        output = self.vip_api_request.remove_vip(vip.vip_id)
        LOG.info('Removing vip from equip {}({}): {}'.format(
            vip.vip_ip, vip.vip_id, output)
        )

        self.delete_vip_request(vip.vip_id)
        vip.delete()

    def get_dscp(self, vip_id):
        data = self.vip_api_request.get_vip_request_details(vip_id)
        return data['vips'][0]['dscp']

    def get_vip_ip(self, vip_id):
        data = self.vip_api_request.get_vip_request_details(vip_id)
        return data['vips'][0]['ipv4']['ip_formated']
