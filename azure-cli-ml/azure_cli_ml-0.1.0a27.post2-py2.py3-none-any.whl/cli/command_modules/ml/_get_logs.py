import json
import shlex
import traceback
from ._ml_cli_error import MlCliError

from ._util import print_util
from hashlib import md5
from kubernetes import client, config


def _construct_log_line(timestamp, level, requestId, apiName, msg):
    return "{0}, {1}, {2}, {3}, {4}".format(timestamp, level, requestId, apiName, msg)


def _is_json_serializable(log):
    try:
        return json.loads(log)
    except:
        return None


def _get_hash_service_id(service_id):
    return md5(service_id.encode()).hexdigest()


def _get_logger_msg(json_line, message_json):
    return _construct_log_line(json_line['timestamp'],
                              json_line['level'],
                              message_json['requestId'],
                              message_json['apiName'],
                              message_json['message'])

def _get_print_log_msg(json_line, requestId):
    return _construct_log_line(json_line['timestamp'],
                        'PRINT_STATEMENT',
                        requestId,
                        '',
                        json_line['message'])


def _get_gunicorn_log_msg(json_line, empty_requestId):
    return _construct_log_line(json_line['timestamp'],
                              json_line['level'],
                              empty_requestId,
                              '',
                              json_line['message'])


def _process_aml_log(json_line, log_counter, requestId, current_request):
    empty_requestId = '00000000-0000-0000-0000-000000000000'
    logger = json_line.get('logger', None)
    if logger == 'root':
        message_json = json.loads(json_line['message'])
        if requestId is None or message_json['requestId'] == requestId:
            print(_get_logger_msg(json_line, message_json))
            log_counter += 1
            if message_json['requestId'] == requestId:
                current_request = True
        if requestId and requestId != message_json['requestId']:
            current_request = False
    elif logger == 'gunicorn.error' or logger == 'gunicorn.access' or logger == 'create_app':
        if 'exc_info' in json_line:
            json_line['message'] = json_line['message'] + '\n' + json_line['exc_info']
        if requestId is None or requestId == empty_requestId:
            print(_get_gunicorn_log_msg(json_line, empty_requestId))
            log_counter += 1
            if empty_requestId == requestId:
                current_request = True
        if requestId and requestId != empty_requestId:
            current_request = False
    return current_request, log_counter


def _process_logs(log_string, requestId):
    broken_string = log_string.split('\n')
    length_of_log = len(broken_string)
    count = 0
    log_counter = 0
    current_request = False
    while count < length_of_log:
        line = broken_string[count]
        json_line = _is_json_serializable(line)
        if json_line:
            try:
                #try to process the line, if failed just print message as is
                current_request, log_counter = _process_aml_log(json_line, log_counter, requestId, current_request)
            except:
                print(json_line)
                log_counter += 1
        else:
            if requestId is None:
                print(line)
                log_counter += 1
            elif current_request:
                print(line)
                log_counter += 1
        count = count + 1
    print("Received {0} lines of log".format(log_counter))


def get_logs_from_docker(container, requestId=None, verb=False):
    '''
    Uses the container name to get the logs and filter them by requestId
    :param container_name: container name as string
    :param requestId: requestId to filter by as string
    :return: 
    '''
    if requestId is not None and not isinstance(requestId, str):
        raise MlCliError('requestId needs to be of type string')
    try:
        print_util("Trying to get logs from container", verb)
        log_string = container.logs().decode('utf-8')
        print_util("Processing Logs", verb)
        _process_logs(log_string, requestId)
    except Exception as ex:
        raise MlCliError('Failed to get logs', content=ex)


def _get_pod_from_hash(pod_hash):
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod("default")
    result_pod = []
    for pod in pods.items:
        hash = pod.metadata.labels.get('pod-template-hash', None)
        if hash and hash == pod_hash:
            result_pod.append(pod.metadata.name)
    return result_pod


def _kubectl_get_logs(pod_name, kubeconfig, context, log_offset=5000, kubectl_location='/tmp/kubectl-1.6.4'):
    # get the most recent log_offset lines of logs from the pods
    log_cmd = '{0} logs {1} --kubeconfig {2} --tail={3}'.format(kubectl_location, pod_name, kubeconfig,
                                                                      log_offset)
    if context.os_is_unix():
        return context.run_cmd(shlex.split(log_cmd))[0]
    else:
        return context.run_cmd(log_cmd)[0]

def get_logs_from_kubernetes(service_id, kubeconfig, context, requestId=None, log_offset=5000, kubectl_location='kubectl', verb=False):
    ''' 
    This does the following:
    - Gets all the replica sets in a namespace
    - Filters them such that they have the label azuremlappname which is equal to the servicename
    - Takes the one that was created last, as that is the current replicaset
    - Gets the pod hash from that replicaset
    - Gets all the pods and filters them such that they match the pod hash
    - Prints all logs from all the pods using kubectl and filters them on request Id if provided
    :param service_id: Name of the service, this is what is used to find the replicasets 
    :param kubeconfig: location of the kubeconfig file
    :param context: Context object
    :param requestId (optional): requestId to filter the logs by 
    :param log_offset (optional): This is an int that we will use to offset our logs. Basically gets the last log_offset lines of logs
    :param kubectl_location (optional): location of the kubectl file
    :return: None
    '''
    try:
        print_util("loading kubeconfig file", verb)
        config.load_kube_config(kubeconfig)
    except Exception as ex:
        raise MlCliError("Failed loading kubeconfig file", content=ex)
    print_util("Getting Replica sets from default namespace", verb)
    api_instance = client.ExtensionsV1beta1Api()
    replicas = api_instance.list_namespaced_replica_set("default")
    result_replica = None
    hash_id = _get_hash_service_id(service_id)
    print_util("Got hash {0}".format(hash_id), verb)
    for replica in replicas.items:
        labels = replica.metadata.labels
        app_label = labels.get('mmsserviceidhash', None)
        if app_label and app_label == hash_id:
            if result_replica:
                if replica.metadata.creation_timestamp > result_replica.metadata.timestamp:
                    result_replica = replica
            else:
                result_replica = replica
    if result_replica is None:
        print_util("No replicasets found that matches the service id", verb)
        raise MlCliError("Service not found")
    print_util("Found a replicaset matching the service id", verb)
    pod_hash = result_replica.metadata.labels.get('pod-template-hash', None)
    if pod_hash is None:
        print_util("No pod_hash found that matches the service id", verb)
        raise MlCliError("Service not found")
    print_util("Using pod hash {0}".format(pod_hash), verb)
    pods = _get_pod_from_hash(pod_hash)
    if pods is None:
        print_util("No pods found that matches the service id", verb)
        raise MlCliError("Service not found")
    result_log = ''
    print_util("Getting logs from  pods", verb)
    for pod in pods:
        temp = _kubectl_get_logs(pod, kubeconfig, context, log_offset=log_offset, kubectl_location=kubectl_location)
        result_log = result_log + temp
    try:
        print_util("Processing logs from pods", verb)
        _process_logs(result_log, requestId)
    except Exception as ex:
        print_util(traceback.format_exc(), verb)
        raise MlCliError("Failed to parse logs")
