from __future__ import print_function
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from base64 import b64encode

import yaml
import time
import json
import os
import re
import subprocess
import traceback
from ._az_util import az_install_kubectl
from ._az_util import kubectl_path
from ._ml_cli_error import MlCliError
from ._util import cli_context
from ._util import print_util


class K8sConstants(object):
    DEFAULT_STORAGE_CONNECTION_STRING = 0
    ACR_SECRET = 1
    KUBE_CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.kube', 'config')
    AML_FE_BLOB_LOCATION = "https://azuremlintfe.blob.core.windows.net/deploymentspecs/azureml-fe-dep-0-latest.yaml"
    WEBSERVICE_LABEL = "webservicename"


class KubernetesOperations:
    def __init__(self, context=cli_context, config_file=None):
        context.update_kube_config()
        config.load_kube_config(config_file=config_file)

    @staticmethod
    def set_current_context(cluster_name):
        try:
            with open(K8sConstants.KUBE_CONFIG_PATH) as f:
                kubeconfig = yaml.load(f)

            for context in kubeconfig['contexts']:
                if context['name'] == cluster_name:
                    kubeconfig['current-context'] = cluster_name
                    with open(K8sConstants.KUBE_CONFIG_PATH, 'w') as f:
                        yaml.safe_dump(kubeconfig, f, default_flow_style=True)
                    return True

        except OSError:
            print("Unable to open kube config file for existing Kubernetes Cluster.")
            return False

        return False



    @staticmethod
    def b64encoded_string(text):
        """
        Returns a string representation of a base64 encoded version of the input text.
        Required because the b64encode method only accept/return bytestrings, but json and yaml require strings
        :param text: Text to encode
        :return string: string representation of the encoded text.
        """
        return b64encode(text.encode()).decode()

    def is_deployment_completed(self, name, namespace, desired_replicas):
        """
        Polls Kubernetes to check if a given deployment has finished being deployed.
        :param name: Name of the deployment
        :param namespace: Namespace containing the deployment.
        :param desired_replicas: Number of replicas requested in the deployment.
        :return (bool, int): ( True if deployment is complete, Number of currently available replicas )
        """
        try:
            api_response = client.ExtensionsV1beta1Api().read_namespaced_deployment_status(name=name,
                                                                                           namespace=namespace)
            return api_response.status.available_replicas == desired_replicas, api_response.status.available_replicas
        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->replace_namespaced_deployment_status: %s\n" % e)
            raise e

    def create_deployment(self, deployment_yaml, namespace, deployment_name, verbose=False):
        """
        Starts the creation of a Kubernetes deployment.
        :param deployment_yaml: Path of the yaml file to deploy
        :param namespace: Namespace to create a deployment in.
        :param deployment_name: Name of the new deployment
        :return: None
        """
        k8s_beta = client.ExtensionsV1beta1Api()
        print("Creating deployment {} in namespace {}".format(deployment_name, namespace))
        try:
            resp = k8s_beta.create_namespaced_deployment(namespace=namespace, body=deployment_yaml)
            if verbose:
                print("Deployment created. status= {} ".format(str(resp.status)))
        except ApiException as e:
            exc_json = json.loads(e.body)
            if "AlreadyExists" in exc_json['reason']:
                k8s_beta.replace_namespaced_deployment(name=deployment_name, body=deployment_yaml, namespace=namespace)
            else:
                print("An error occurred while creating the deployment. {}".format(exc_json['message']))
                raise

    def deploy_deployment_file(self, deployment_yaml_path, max_deployment_time_s, desired_replica_num, secret_name,
                               verbose=False):
        try:
            with open(deployment_yaml_path) as f:
                dep = yaml.load(f)
        except OSError:
            raise MlCliError("Unable to find deployment file, expected at {}".format(deployment_yaml_path))

        return self.deploy_deployment(dep, max_deployment_time_s, desired_replica_num, secret_name, verbose)

    def deploy_deployment(self, dep, max_deployment_time_s=600, desired_replica_num=None, secret_name=None,
                          verbose=False):
        """
        Deploys a Kubernetes Deployment and waits for the deployment to complete.
        :param dep:  yaml data to deploy
        :param max_deployment_time_s: Max time to wait for a deployment to succeed before cancelling.
        :param desired_replica_num: Number of replica pods to create in the deployment
        :param secret_name: Name of the Kubernetes secret that contains the ACR login information for the image
                            specified in the deployment_yaml.
        :param verbose: Verbose printing flag
        :return bool: True if the deployment succeeds.
        """
        namespace = "default"
        deployment_name = dep["metadata"]["name"]
        if desired_replica_num is not None:
            dep["spec"]["replicas"] = desired_replica_num
        else:
            desired_replica_num = dep["spec"]["replicas"]
        if secret_name is not None:
            dep["spec"]["template"]["spec"]["imagePullSecrets"][0]["name"] = secret_name
        self.create_deployment(dep, namespace, deployment_name, verbose)
        start_time = time.time()
        dot_string = '.'
        while time.time() - start_time < max_deployment_time_s:
            is_complete, pods = self.is_deployment_completed(dep["metadata"]["name"], namespace, desired_replica_num)
            pods = 0 if pods is None else pods
            replica_string = 'Deploying {} / {} pods'.format(pods, desired_replica_num)
            dot_string = '{}.'.format(dot_string)
            print('{}{}'.format(replica_string, dot_string), end="\r")

            if is_complete:
                print('')
                print("Deployment Complete")
                return True
            time.sleep(5)
        raise MlCliError("Deployment failed to get the desired number of pods")

    def expose_frontend(self, service_yaml):
        """
        Exposes the azureml-fe deployment as a service.
        :param service_yaml: pyyaml object containing the service payload
        :return: None
        """
        try:
            k8s_core = client.CoreV1Api()
            namespace = 'default'
            print("Exposing frontend on Kubernetes deployment.")
            k8s_core.create_namespaced_service(body=service_yaml, namespace=namespace)

        except ApiException as e:
            exc_json = json.loads(e.body)
            if 'AlreadyExists' in exc_json['reason']:
                return
            print("Exception during service creation: %s" % e)

    def get_service(self, webservicename, label=K8sConstants.WEBSERVICE_LABEL):
        """
        Retrieves a service with a given webservicename
        :param webservicename: Name of the webservice.
        :param label: Optional label on Kubernetes service.
        :return kubernetes.client.V1Service: Returns the webservice specified or None if one was not found.
        """
        try:
            k8s_core = client.CoreV1Api()
            namespace = 'default'
            label_selector = '{}=={}'.format(label, webservicename)
            api_response = k8s_core.list_namespaced_service(namespace, label_selector=label_selector)
            if len(api_response.items) == 0:
                raise ApiException(status=404, reason="Service with label selector: {} not found".format(label_selector))  # pylint: disable=line-too-long

            return api_response.items[0]
        except ApiException as e:
            print("Exception occurred while getting a namespaced service. {}".format(e))
            raise

    def delete_service(self, webservicename):
        """
        Deletes a service with a given webservicename
        :param webservicename:
        :return: None
        """
        try:
            k8s_core = client.CoreV1Api()
            namespace = 'default'
            k8s_core.delete_namespaced_service(webservicename, namespace)

        except ApiException as exc:
            print("Exception occurred in delete_service. {}".format(exc))
            raise

    def create_kubernetes_object_if_not_exist(self, namespace, body, create_func):
        """
        Attempts to create a Kubernetes object.
        :param namespace: Namespace of the the object.
        :param body: Body of the object
        :param create_func: The kubernetes function to be used for creation
        :return bool: True if successful, false if secret already exists.
        """
        retries = 0
        max_retries = 3
        while retries < max_retries:
            try:
                create_func(namespace, body)
                return True
            except ApiException as e:
                if e.status == 409:  # 409 indicates object already exists
                    return False
                retries += 1
                if retries >= max_retries:
                    print("Exception occurred in create_kubernetes_object_if_not_exist: {}".format(e))
                    raise e

    def replace_secrets(self, name, namespace, body):
        """
        Replaces an existing secret. Cannot patch due to immutability.
        :param name: Name of the secret to replace
        :param namespace: Namespace containing the secret
        :param body: Kubernetes.client.V1Secret containing the secret payload
        :return bool: True if successful, false if secret already exists.
        """
        try:
            client.CoreV1Api().delete_namespaced_secret(name, namespace, client.V1DeleteOptions())
            return self.create_kubernetes_object_if_not_exist(namespace, body, client.CoreV1Api().create_namespaced_secret)
        except ApiException as e:
            print("Exception occurred in replace_secrets: {}".format(e))
            raise e

    def replace_config(self, name, namespace, body):
        """
        Replaces an existing ConfigMap.
        :param name: Name of the ConfigMap to replace
        :param namespace: Namespace containing the ConfigMap
        :param body: Kubernetes.client.V1ConfigMap containing the ConfigMap payload
        :return bool: True if successful, false if ConfigMap already exists.
        """
        try:
            client.CoreV1Api().delete_namespaced_config_map(name, namespace, client.V1DeleteOptions())
            return self.create_kubernetes_object_if_not_exist(namespace, body, client.CoreV1Api().create_namespaced_config_map)
        except ApiException as e:
            print("Exception occurred in replace_config: {}".format(e))
            raise e

    def create_or_replace_secret_if_exists(self, secret, secret_name, secret_type):
        """
        Adds a secret to Kubernetes secret storage.
        :param secret: Secret dictionary
        :param secret_name: Name of the secret
        :param secret_type: Type of the secret
        :return bool: True if successful.
        """
        print("Creating Secret {}".format(secret_name))
        namespace = 'default'
        meta = client.V1ObjectMeta(name=secret_name, namespace=namespace)
        body = client.V1Secret(data=secret, metadata=meta, type=secret_type)
        if self.create_kubernetes_object_if_not_exist(namespace, body, client.CoreV1Api().create_namespaced_secret):
            return True
        else:
            return self.replace_secrets(secret_name, namespace, body)

    def create_or_replace_service_config_if_exists(self, webservicename, config):
        """
        Adds a webservice ConfigMap to Kubernetes.
        :param webservicename: Name of the webservice
        :param config: The configuration dictionary
        :return bool: True if successful.
        """
        config_name = webservicename + "-config"
        print("Creating Config {}".format(config_name))
        namespace = 'default'
        meta = client.V1ObjectMeta(name=config_name, namespace="default")
        body = client.V1ConfigMap(data=config, metadata=meta)
        if self.create_kubernetes_object_if_not_exist(namespace, body, client.CoreV1Api().create_namespaced_config_map):
            return True
        else:
            return self.replace_config(config_name, namespace, body)

    def encode_acr_credentials(self, acr_host, acr_uname, acr_pwd, acr_email):
        """
        Encodes ACR credentials for correct storage as a .dockerconfigjson secret.
        :param acr_host: Base url of the acr storage
        :param acr_uname: Username of the ACR
        :param acr_pwd: Password of the ACR
        :param acr_email: Email connected to the ACR
        :return string: Base64 representation of ACR credentials
        """
        return self.b64encoded_string(json.dumps(
            {acr_host:
                {"username": acr_uname,
                 "password": acr_pwd,
                 "email": acr_email,
                 "auth": self.b64encoded_string("{}:{}".format(acr_uname, acr_pwd))
                 }
             }
        ))

    def add_model_dc_secret(self, key, storage_account, event_hub):
        """
        Adds a model data collection secret to Kubernetes.
        :param key: Name of the secret being added
        :param storage_account: The storage account connection string
        :param event_hub: The event hub connection string
        :return: None
        """
        secret = dict()
        secret["storageaccount"] = self.b64encoded_string(storage_account)
        secret["eventhub"] = self.b64encoded_string(event_hub)
        return self.create_or_replace_secret_if_exists(secret, key, "Opaque")

    def add_service_config(self, webservicename, config):
        """
        Adds a webservice ConfigMap to Kubernetes.
        :param webservicename: The name of the webservice
        :param config: The configuration dictionary
        :return: None
        """
        return self.create_or_replace_service_config_if_exists(webservicename, config)

    def delete_deployment(self, webservicename, context):
        """
        Deletes a deployment with a given webservicename
        :param webservicename:
        :param context:
        :return: None
        """
        try:
            k8s_core = client.ExtensionsV1beta1Api()
            namespace = 'default'
            delete_options = client.V1DeleteOptions()
            name = webservicename
            k8s_core.delete_namespaced_deployment(name, namespace, delete_options)
            self.delete_replica_set(name, context)

        except ApiException as exc:
            print("Exception occurred in delete_deployment. {}".format(exc))
            raise

    def get_filtered_deployments(self, label_selector=''):
        """
        Retrieves a list of deployment objects filtered by the given label_selector
        :param label_selector: Formatted label selector i.e. "webservicename==deployed_service_name"
        :return list[Kubernetes.client.ExtensionsV1beta1Deployment:
        """
        k8s_beta = client.ExtensionsV1beta1Api()
        namespace = 'default'
        try:
            deployment_list = k8s_beta.list_namespaced_deployment(namespace, label_selector=label_selector)
            return deployment_list.items
        except ApiException as exc:
            print("Exception occurred in get_filtered_deployments. ".format(exc))
            raise

    def delete_replica_set(self, deployment_name, context):
        try:
            print("Deleting replicaset for deployment {}".format(deployment_name))

            # Pipe output of get_rs_proc to grep_named_rs_row_proc
            get_rs_output = context.check_output(['kubectl', 'get', 'rs']).decode('utf-8')
            rs_regex = r'(?P<rs_name>{}-[0-9]+)'.format(deployment_name)
            s = re.search(rs_regex, get_rs_output)
            if s:
                context.check_call(['kubectl', 'delete', 'rs', s.group('rs_name')])
        except subprocess.CalledProcessError as exc:
            print("Unable to delete replica set for deployment {}. {} {}".format(deployment_name, exc, exc.output))
            raise

    def scale_deployment(self, service_name, num_replicas, context):
        try:
            print("Scaling web service {} to {} pods".format(service_name, num_replicas))
            deployment_name = service_name
            num_replicas = int(num_replicas)
            context.check_call(['kubectl', 'scale', 'deployment', deployment_name,
                                   '--replicas={}'.format(num_replicas)])
            print("If you increased the number of pods, your service may appear 'Unhealthy' when running")
            print("az ml service list realtime")
            print("This will return to 'Healthy' when all new pods have been created.")
        except subprocess.CalledProcessError:
            print("Unable to scale service. {}")

    def create_service(self, service_yaml, webservicename, webservice_type, verbose=False):
        try:
            k8s_core = client.CoreV1Api()
            namespace = 'default'
            with open(service_yaml) as f:
                dep = yaml.load(f)
                dep['metadata']['name'] = str(webservicename)
                dep['metadata']['labels']['webservicename'] = str(webservicename)
                dep['metadata']['labels']['azuremlappname'] = str(webservicename)
                dep['metadata']['labels']['webservicetype'] = str(webservice_type)
                dep['spec']['selector']['webservicename'] = str(webservicename)
                if verbose:
                    print("Payload: {0}".format(dep))
                k8s_core.create_namespaced_service(body=dep, namespace=namespace)
                print("Created service with Name: {0}".format(webservicename))
        except ApiException as e:
            exc_json = json.loads(e.body)
            if 'AlreadyExists' in exc_json['reason']:
                return
            print("Exception during service creation: %s" % e)

    def test_connection_to_cluster(self):
        try:
            api_instance = client.ApisApi()
            api_instance.get_api_versions()
            return True
        except Exception:
            return False


def _check_kubectl_in_path(context):
    try:
        with open(os.devnull, 'w') as devnull:
            context.check_output('kubectl', stderr=devnull)
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


def _install_kubectl(context, verb):
    try:
        az_install_kubectl(context)
        return True
    except PermissionError:
        print("You do not have permissions to install kubectl, please contact your system administrator")
        print_util(traceback.format_exc(), verb)
        return False
    except:
        print("Failed to installed kubectl")
        print_util(traceback.format_exc(), verb)
        return False


def check_for_kubectl(context, verb=False):
    """Checks whether kubectl is present on the system path or in the default installation location"""
    if _check_kubectl_in_path(context):
        print_util("Kubectl found in PATH", verb)
        return True
    elif os.path.exists(kubectl_path(context)):
        # ensure kubectl installation is in path
        print_util("Kubectl exists in default location, adding it to PATH", verb)
        os.environ['PATH'] += os.pathsep + os.path.dirname(kubectl_path(context))
        return True
    else:
        print_util("Kubectl is neither in PATH nor in default location", verb)
        auto_install = context.get_input(
            'kubectl is not installed. One click install? (Y/n): ').lower().strip()
        if 'n' not in auto_install and 'no' not in auto_install:
            return _install_kubectl(context, verb)
        else:
            print('To install Kubectl run the following commands and then re-run az ml env setup')
            print('curl -LO https://storage.googleapis.com/kubernetes-release/release/' +
                  '$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)' +
                  '/bin/linux/amd64/kubectl')
            print('chmod +x ./kubectl')
            print('sudo mv ./kubectl ~/bin')
            return False


def test_acs_k8s(context):
    try:
        ops = KubernetesOperations(context)
        return ops.test_connection_to_cluster()

    except (config.ConfigException, ApiException, OSError) as e:
        print('')
        print('Encountered exception when connecting to Kubernetes cluster.\n {}'.format(e))
        print('Your Kubernetes cluster is not responding as expected.')
        print('Please verify it is healthy. If you set it up via `az ml env setup,` '
              'please contact deployml@microsoft.com to troubleshoot.')
        print('')
        return False


def batch_get_k8s_frontend_url(context):
    if context.k8s_batch_url:
        return context.k8s_batch_url

    frontend_service_name = 'sparkbatch'
    k8s_ops = KubernetesOperations(context)
    try:
        frontend_service = k8s_ops.get_service(frontend_service_name)
        if frontend_service.status.load_balancer.ingress is None:
            raise ApiException(status=404,
                               reason="LoadBalancer has not finished being created for the Kubernetes front end. Please try again in a few minutes.")  # pylint: disable=line-too-long
    except ApiException as exc:
        raise MlCliError("Unable to load details for AzureML Kubernetes front end server.", content=exc)

    base_url = frontend_service.status.load_balancer.ingress[0].ip
    port = frontend_service.spec.ports[0].port
    frontend_url = '{}:{}'.format(base_url, port)
    context.k8s_batch_url = frontend_url

    # write_variables_to_amlenvrc_if_not_exist(context, 'AML_K8S_BATCH_URL',
    #                                          frontend_url, 'a+')

    return frontend_url
