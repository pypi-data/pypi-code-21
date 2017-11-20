import json
import copy
import os
import time
from multiprocessing import Process
import requests
from requests.exceptions import (ConnectionError, ConnectTimeout)
from ..constants import power_status_list, power_status_action
from ..constants import (ACTION_POWER_ON, ACTION_POWER_OFF, ACTION_REBOOT)
from ..constants import (STATE_UNKNOWN, STATE_POWER_ON, STATE_POWER_OFF,
    STATE_POWERING_ON, STATE_POWERING_OFF)
from ..constants import SUPPORTED_MACHINE_TYPES
from .boot_order import boot_order_priority, setting_boot_type
from .boot_order import BOOT_DEVICES
from ..exceptions import *

from oslo_log import log as logging
LOG = logging.getLogger(__name__)

POWER_ACTION_TIMEOUT = 600  # 10 minutes
UNKNOWN_MACHINE_TYPE = 'Unknown'

requests.packages.urllib3.disable_warnings()


class Client(object):
    def __init__(self, username=None, password=None,
                 version=None, ip='127.0.0.1', port=443):

        self._version = version
        self._username = username
        self._password = password
        self._url = 'https://%s' % ip

    def _gen_node_action_url(self, node_id):
        return '{url}/node/{node_id}'.format(url=self._url, node_id=node_id)

    def _get_node_details(self, node_id):
        url = self._gen_node_action_url(node_id)
        try:
            r = requests.get(url,
                             auth=(self._username, self._password),
                             verify=False,
                             timeout=(10, 10))
            result = {
                'status_code': r.status_code,
                'encoding': r.encoding,
                'headers': r.headers,
                'body': r.json()
            }
            return result
        except ConnectionError or ConnectTimeout as ex:
            raise ConnectionFailureException(node_id=node_id, detail=str(ex))
        except Exception as ex:
            raise NodeDetailsException(message=str(ex), node_id=node_id)

    def get_node_status(self, node_id):
        response = self._get_node_details(node_id)
        if response['status_code'] == 200:
            return response['body']['accessState'].lower()
        else:
            return 'unknown'

    def get_node_product_name(self, node_id):
        response = self._get_node_details(node_id)
        product_name = 'Unknown'
        if response['status_code'] == 200:
            body = response['body']
            product_name = body.get('productName', 'Unknown')

        return product_name

    def get_node_info(self, node_id):
        response = self._get_node_details(node_id)
        info = {}
        if response['status_code'] == 200:
            body = response['body']
            info['uuid'] = body.get('uuid', None)
            info['name'] = body.get('hostname', 'Unknown')
            info['product_name'] = body.get('productName', 'Unknown')
            info['power_state'] = power_status_list.get(
                body.get('powerStatus', 0), 0)

            info['chassis_id'] = None  # nullable
            info['target_power_state'] = None  # nullable
            info['provision_state'] = None   # nullable
            info['target_provision_state'] = None  # nullable
            info['provision_updated_at'] = None  # nullable
            info['last_error'] = None  # nullable
            info['instance_uuid'] = None  # nullable
            info['instance_info'] = None  # nullable

            info['raid_config'] = body.get('raidSettings', [])  # An array
            info['target_raid_config'] = []
            info['maintenance'] = False \
                if body.get('accessState', 'unknown') == 'online' else True
            info['maintenance_reason'] = None  # nullable
            info['console_enabled'] = False  # False is by default, what's this
            info['extra'] = {}  # What's this?
            info['properties'] = {}  # What's this?
        else:
            err_msg = "Fail to get node info, http status code is %s, " \
                      "http response is %s" % (response['status_code'], response['body'])
            raise NodeDetailsException(node_id=node_id, detail=err_msg)

        return info

    def _gen_power_action_file_path(self, node_id, action):
        file_name = "{action}_{node_id}_in_progress".format(action=action, node_id=node_id)
        pre_path = "/tmp" if os.path.exists("/tmp") else "./"  # resolve Windows OS problem
        path = os.path.join(pre_path, file_name)
        return path

    def _check_power_action_running(self, node_id):
        power_on_file = self._gen_power_action_file_path(node_id, ACTION_POWER_ON)
        power_off_file = self._gen_power_action_file_path(node_id, ACTION_POWER_OFF)

        if os.path.exists(power_on_file) and os.path.exists(power_off_file):
            now = time.time()
            delta_on = now - os.path.getmtime(power_on_file)
            delta_off = now - os.path.getmtime(power_off_file)

            if (delta_on > POWER_ACTION_TIMEOUT and delta_off > POWER_ACTION_TIMEOUT) or \
               (delta_on <= POWER_ACTION_TIMEOUT and delta_off <= POWER_ACTION_TIMEOUT):
                os.remove(power_on_file)
                os.remove(power_off_file)
                result = None
            elif delta_on > POWER_ACTION_TIMEOUT:
                os.remove(power_on_file)
                result = STATE_POWER_OFF
            elif delta_off > POWER_ACTION_TIMEOUT:
                os.remove(power_off_file)
                result = STATE_POWER_ON

        elif os.path.exists(power_on_file):
            delta = time.time() - os.path.getmtime(power_on_file)
            if delta > POWER_ACTION_TIMEOUT:
                os.remove(power_on_file)
                result = None
            else:
                result = STATE_POWERING_ON

        elif os.path.exists(power_off_file):
            delta = time.time() - os.path.getmtime(power_off_file)
            if delta > POWER_ACTION_TIMEOUT:
                os.remove(power_off_file)
                result = None
            else:
                result = STATE_POWERING_OFF

        else:
            result = None

        return result

    def get_node_power_status(self, node_id):
        result = self._check_power_action_running(node_id)
        if result:
            return result

        response = self._get_node_details(node_id)
        if response['status_code'] == 200:
            result = power_status_list[response['body']['powerStatus']]
        else:
            result = STATE_UNKNOWN
        return result

    def _set_power_status(self, node_id, action):
        url = self._gen_node_action_url(node_id)
        data = {'powerState': action}
        try:
            power_action_file = self._gen_power_action_file_path(node_id, action)
            out_file = open(power_action_file, "w")
            out_file.close()

            requests.put(url,
                         auth=(self._username, self._password),
                         data=json.dumps(data),
                         verify=False)
        except ConnectionError or ConnectTimeout as ex:
            raise ConnectionFailureException(node_id=node_id, detail=str(ex))
        finally:
            if os.path.exists(power_action_file):
                os.remove(power_action_file)

    def set_node_power_status(self, node_id, action):
        if action not in power_status_action:
            raise BadPowerStatusSettingException(action=action)
        action = power_status_action[action]

        p = Process(target=self._set_power_status, args=(node_id, action))
        p.start()

    def get_node_all_boot_info(self, node_id):
        response = self._get_node_details(node_id)
        if response['status_code'] == 200:
            try:
                boot_info = {'bootOrder': response['body']['bootOrder']}
                return boot_info
            except KeyError as ex:
                raise FailToGetBootOrderException(node_id=node_id)

    # This method is not used in XClarity Driver
    def get_node_boot_info(self, node_id):
        response = self._get_node_details(node_id)
        if response['status_code'] == 200:
            boot_order_list = response['body']['bootOrder']['bootOrderList']
            boot_order_table = copy.deepcopy(boot_order_priority)

            for boot_item in boot_order_list:
                boot_item_type = boot_item['bootType'].lower()
                for item in boot_order_table:
                    if item['name'] == boot_item_type:
                        item['value'] = boot_item
                        break

            first_boot_item = None
            for item in boot_order_table:
                if item['value'] is not None:
                    first_boot_item = item['value']
                    break

            return first_boot_item

        else:
            return None

    """
        Change the primary boot device to the real name by checking machine type
    """
    def _gen_real_boot_order(self, machine_type, boot_order, target_device, permanent):
        for item in boot_order['bootOrder']['bootOrderList']:
            if item['bootType'].lower() == 'singleuse':
                singleuse_item = item
            elif item['bootType'].lower() in ['permanent', 'bootorder']:
                # for 3250/3650, permanent boot type is 'Permanent'
                # for SR630, permanent boot type is 'BootOrder'
                permanent_item = item

        if permanent:
            current = permanent_item['currentBootOrderDevices']
            real_target = BOOT_DEVICES[machine_type]['permanent'][target_device]
        else:
            current = singleuse_item['currentBootOrderDevices']
            real_target = BOOT_DEVICES[machine_type]['singleuse'][target_device]

        if real_target in current:
            current.remove(real_target)

        current.insert(0, real_target)

        if not permanent:
            if 'None' in current:
                current.remove('None')
            if 'none' in current:
                current.remove('None')

        LOG.info("Final Boot Info after set boot device is: %s" % json.dumps(boot_order))
        return boot_order

    """
        :param node_id, the id of the node
        :param boot_order, a dict which is like below:
            {
                "bootOrder":{
                    "bootOrderList":[
                        {
                            "bootType":"SingleUse",
                            "currentBootOrderDevices":["PXE Network"],
                            "possibleBootOrderDevices":[
                                "None",
                                "PXE Network",
                                "HardDisk0",
                                "Diagnostics",
                                "CD/DVDRom",
                                "BootToF1",
                                "Hypervisor",
                                "FloppyDisk"
                            ]
                        },  # one boot item
                        ...
                    ]  # boot order list
                }
            }
        :param target_device, the device will be set as primary boot device
        :param permanent, Bool, point out this is configured to
                permanent item (True) or singleuse item
    """
    def set_node_boot_info(self, node_id, boot_order, target_device, permanent):
        try:
            product_name = self.get_node_product_name(node_id)

            machine_type = UNKNOWN_MACHINE_TYPE
            for smt in SUPPORTED_MACHINE_TYPES:
                if smt in product_name.upper():
                    machine_type = smt
                    break

            if machine_type == UNKNOWN_MACHINE_TYPE:
            #    raise UnsupportedMachineType(machine_type=product_name)
                raise Exception("Unsupported Machine Type: %s" % machine_type)

            input_boot_order = self._gen_real_boot_order(machine_type,
                                                         boot_order,
                                                         target_device,
                                                         permanent)

            url = self._gen_node_action_url(node_id)
            r = requests.put(url,
                             auth=(self._username, self._password),
                             data=json.dumps(input_boot_order),
                             verify=False)

            if r.status_code != 200:
                raise Exception("Fail to set node boot info. status code = %s" % r.status_code)

        except ConnectionError or ConnectTimeout as ex:
            raise ConnectionFailureException(node_id=node_id, detail=str(ex))
        # except UnsupportedMachineType:
        #     raise
        except Exception as ex:
            print("Exception! - %s" % str(ex))

    def _get_all_xclarity_jobs(self):
        url = '{url}/jobs'.format(url=self._url)
        r = requests.get(url,
                         auth=(self._username, self._password),
                         verify=False,
                         timeout=(10, 10))

        if r.status_code != 200:
            raise FailToGetAllJobs(status_code=r.status_code)
        else:
            return r.json()

    def node_has_jobs(self, node_id):
        all_jobs = self._get_all_xclarity_jobs()
        count = 0
        for job in all_jobs:
            if job.get('uuid', None) == node_id:
                count += 1
        print("jobs number = %d" % count)
        return True if count > 0 else False

    def ready_for_deployment(self, node_id):
        response = self._get_node_details(node_id)
        result = False
        if response['status_code'] == 200:
            power_status = power_status_list[response['body']['powerStatus']]
            if power_status in ['on', 'off']:
                result = True

        if result:
            result = self.node_has_jobs(node_id)

        return result
