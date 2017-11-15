#-*- coding: utf-8 -*-

__version__ = "1.3.7"

import warnings
import requests
import fire
import tarfile
import os
import sys
import kubernetes.client as kubeclient
from kubernetes.client.rest import ApiException
import kubernetes.config as kubeconfig
import yaml
import json
from pprint import pprint
import subprocess
from datetime import timedelta
import importlib.util
import jinja2


class PipelineCli(object):

    # Deprecated
    _kube_deploy_registry = {'jupyter': (['jupyterhub/jupyterhub-deploy.yaml'], []),
                            'jupyterhub': (['jupyterhub/jupyterhub-deploy.yaml'], []),
                            'spark': (['spark/master-deploy.yaml'], ['spark-worker', 'metastore']),
                            'spark-worker': (['spark/worker-deploy.yaml'], []),
                            'metastore': (['metastore/metastore-deploy.yaml'], ['mysql']),
                            'hdfs': (['hdfs/namenode-deploy.yaml'], []),
                            'redis': (['keyvalue/redis-master-deploy.yaml'], []),
                            'presto': (['presto/master-deploy.yaml',
                                        'presto/worker-deploy.yaml'], ['metastore']),
                            'presto-ui': (['presto/ui-deploy.yaml'], ['presto']),
                            'airflow': (['airflow/airflow-deploy.yaml'], ['mysql', 'redis']),
                            'mysql': (['sql/mysql-master-deploy.yaml'], []),
                            'web-home': (['web/home-deploy.yaml'], []),
                            'zeppelin': (['zeppelin/zeppelin-deploy.yaml'], []),
                            'zookeeper': (['zookeeper/zookeeper-deploy.yaml'], []),
                            'elasticsearch': (['elasticsearch/elasticsearch-2-3-0-deploy.yaml'], []),
                            'kibana': (['kibana/kibana-4-5-0-deploy.yaml'], ['elasticsearch'], []), 
                            'kafka': (['stream/kafka-0.11-deploy.yaml'], ['zookeeper']),
                            'cassandra': (['cassandra/cassandra-deploy.yaml'], []),
                            'jenkins': (['jenkins/jenkins-deploy.yaml'], []),
                            'turbine': (['dashboard/turbine-deploy.yaml'], []),
                            'hystrix': (['dashboard/hystrix-deploy.yaml'], []),
                           }

    # Deprecated
    _kube_svc_registry = {'jupyter': (['jupyterhub/jupyterhub-svc.yaml'], []),
                         'jupyterhub': (['jupyterhub/jupyterhub-svc.yaml'], []),
                         'spark': (['spark/master-svc.yaml'], ['spark-worker', 'metastore']), 
                         'spark-worker': (['spark/worker-svc.yaml'], []),
                         'metastore': (['metastore/metastore-svc.yaml'], ['mysql']),
                         'hdfs': (['hdfs/namenode-svc.yaml'], []),
                         'redis': (['keyvalue/redis-master-svc.yaml'], []),
                         'presto': (['presto/master-svc.yaml',
                                     'presto/worker-svc.yaml'], ['metastore']),
                         'presto-ui': (['presto/ui-svc.yaml'], ['presto']),
                         'airflow': (['airflow/airflow-svc.yaml'], ['mysql', 'redis']),
                         'mysql': (['sql/mysql-master-svc.yaml'], []),
                         'web-home': (['web/home-svc.yaml'], []),
                         'zeppelin': (['zeppelin/zeppelin-svc.yaml'], []),
                         'zookeeper': (['zookeeper/zookeeper-svc.yaml'], []),
                         'elasticsearch': (['elasticsearch/elasticsearch-2-3-0-svc.yaml'], []),
                         'kibana': (['kibana/kibana-4-5-0-svc.yaml'], ['elasticsearch'], []),
                         'kafka': (['stream/kafka-0.11-svc.yaml'], ['zookeeper']),
                         'cassandra': (['cassandra/cassandra-svc.yaml'], []),
                         'jenkins': (['jenkins/jenkins-svc.yaml'], []),
                         'turbine': (['dashboard/turbine-svc.yaml'], []),
                         'hystrix': (['dashboard/hystrix-svc.yaml'], []),
                        }

    _Dockerfile_template_registry = {
                                     'predict-cpu': (['predict-Dockerfile-localfile-model-cpu.template'], []),
                                     'train-cpu': (['train-Dockerfile-localfile-model-cpu.template'], []),
                                    }
    _kube_deploy_template_registry = {'predict': (['predict-deploy.yaml.template'], [])}
    _kube_svc_template_registry = {'predict': (['predict-svc.yaml.template'], [])}
    _kube_autoscale_template_registry = {'predict': (['predict-autoscale.yaml.template'], [])}
    _kube_train_cluster_template_registry = {'train-cluster-cpu': (['train-cluster-cpu.yaml.template'], [])}
    
    _pipeline_api_version = 'v1' 
    _default_templates_path = os.path.join(os.path.dirname(__file__), 'templates/')


    def version(self):
        print('')
        print('cli_version: %s' % __version__)
        print('api_version: %s' % PipelineCli._pipeline_api_version)
        print('')
        print('capabilities_enabled: %s' % ['predict', 'prediction_server', 'training_server'])
        print('capabilities_disabled: %s' % ['prediction_cluster', 'training_cluster', 'parameter_tune', 'prediction_router'])
        print('')
        print('Email upgrade@pipeline.ai to enable the advanced capabilities.')
        print('')


    def _templates_path(self):
        print("")
        print("templates_path: %s" % PipelineCli._default_templates_path)
        print("")


    def training_server_pull(self,
                         model_type,
                         model_name,
                         model_tag,
                         build_registry_url='docker.io',
                         build_registry_repo='pipelineai',
                         build_prefix='train'):

        cmd = 'docker pull %s/%s/%s-%s-%s:%s' % (build_registry_url, build_registry_repo, build_prefix, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def training_server_push(self,
                         model_type,
                         model_name,
                         model_tag,
                         build_registry_url='docker.io',
                         build_registry_repo='pipelineai',
                         build_prefix='train'):

        cmd = 'docker push %s/%s/%s-%s-%s:%s' % (build_registry_url, build_registry_repo, build_prefix, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def training_server_logs(self,
                            model_type,
                            model_name,
                            model_tag,
                            build_prefix='train'):

        cmd = 'docker logs -f %s-%s-%s-%s' % (build_prefix, model_type, model_name, model_tag)

        print(cmd)
        print("")

        process = subprocess.call(cmd, shell=True)


    def training_server_shell(self,
                     model_type,
                     model_name,
                     model_tag,
                     build_prefix='train'):

        cmd = 'docker exec -it %s-%s-%s-%s bash' % (build_prefix, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def _service_connect(self,
                         service_name,
                         kube_namespace="default",
                         local_port=None,
                         service_port=None):

        pod = self._get_pod_by_service_name(service_name=service_name)
        if not pod:
            print("")
            print("App '%s' is not running." % service_name)
            print("")
            return
        if not service_port:
            svc = self._get_svc_by_service_name(service_name=service_name)
            if not svc:
                print("")
                print("App '%s' proxy port cannot be found." % service_name)
                print("")
                return
            service_port = svc.spec.ports[0].target_port

        if not local_port:
            print("")
            print("Proxying local port '<randomly-chosen>' to app '%s' port '%s' using pod '%s'." % (service_port, service_name, pod.metadata.name))
            print("")
            print("Use 'http://127.0.0.1:<randomly-chosen>' to access app '%s' on port '%s'." % (service_name, service_port))
            print("")
            print("If you break out of this terminal, your proxy session will end.")
            print("")
            cmd = 'kubectl port-forward %s :%s --all-namespaces' % (pod.metadata.name, service_port)
            print("Running command...")
            print(cmd)
            print("")
            subprocess.call(cmd, shell=True)
            print("")
        else:
            print("")
            print("Proxying local port '%s' to app '%s' port '%s' using pod '%s'." % (local_port, service_port, service_name, pod.metadata.name))
            print("")
            print("Use 'http://127.0.0.1:%s' to access app '%s' on port '%s'." % (local_port, service_name, service_port))
            print("")
            print("If you break out of this terminal, your proxy session will end.")
            print("")
            subprocess.call('kubectl port-forward %s %s:%s' % (pod.metadata.name, local_port, service_port), shell=True)
            print("")


    def _environment_resources(self):
        subprocess.call("kubectl top node", shell=True)

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                              pretty=True)
            deployments = response.items
            for service_name in deployments:
                self._service_resources(service_name)


    def _service_resources(self,
                           service_name):

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, 
                                                                 pretty=True)
            pods = response.items
            for pod in pods: 
                if (service_name in pod.metadata.name):
                    subprocess.call('kubectl top pod %s' % pod.metadata.name, shell=True)
        print("")


    def training_server_pull(self,
                         model_type,
                         model_name,
                         model_tag,
                         build_registry_url='docker.io',
                         build_registry_repo='pipelineai',
                         build_prefix='train'):

        cmd = 'docker pull %s/%s/%s-%s-%s:%s' % (build_registry_url, build_registry_repo, build_prefix, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def training_server_push(self,
                         model_type,
                         model_name,
                         model_tag,
                         build_registry_url='docker.io',
                         build_registry_repo='pipelineai',
                         build_prefix='train'):

        cmd = 'docker push %s/%s/%s-%s-%s:%s' % (build_registry_url, build_registry_repo, build_prefix, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def training_server_logs(self,
                            model_type,
                            model_name,
                            model_tag,
                            build_prefix='train'):

        cmd = 'docker logs -f %s-%s-%s-%s' % (build_prefix, model_type, model_name, model_tag)

        print(cmd)
        print("")

        process = subprocess.call(cmd, shell=True)


    def training_server_shell(self,
                     model_type,
                     model_name,
                     model_tag,
                     build_prefix='train'):

        cmd = 'docker exec -it %s-%s-%s-%s bash' % (build_prefix, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)

    def _create_training_server_Dockerfile(self,
                                      model_type,
                                      model_name,
                                      model_tag,
                                      hyper_params,
                                      templates_path,
                                      build_path):

        print("")
        print("Using templates in '%s'." % templates_path)
        print("(Specify --templates-path if the templates live elsewhere.)")
        print("")

        context = {'PIPELINE_MODEL_TYPE': model_type,
                   'PIPELINE_MODEL_NAME': model_name,
                   'PIPELINE_MODEL_TAG': model_tag}

        context = {**context, **hyper_params}

        model_train_cpu_Dockerfile_templates_path = os.path.join(templates_path, PipelineCli._Dockerfile_template_registry['train-cpu'][0][0])
        path, filename = os.path.split(model_train_cpu_Dockerfile_templates_path)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)
        # TODO:  Create -gpu version as well
        rendered_filename = '%s/generated-%s-%s-%s-Dockerfile-cpu' % (build_path, model_type, model_name, model_tag)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' -> '%s'." % (filename, rendered_filename))

        return rendered_filename


    def training_server_build(self,
                          model_type,
                          model_name,
                          model_tag,
                          model_path,
                          hyper_params={},
                          build_type='docker',
                          build_path='.',
                          templates_path=_default_templates_path,
                          build_registry_url='docker.io',
                          build_registry_repo='pipelineai',
                          build_prefix='train'):

        build_path = os.path.expandvars(build_path)
        build_path = os.path.expanduser(build_path)
        build_path = os.path.abspath(build_path)

        templates_path = os.path.expandvars(templates_path)
        templates_path = os.path.expanduser(templates_path)
        templates_path = os.path.abspath(templates_path)
        templates_path = os.path.relpath(templates_path, build_path)

        model_path = os.path.expandvars(model_path)
        model_path = os.path.expanduser(model_path)
        model_path = os.path.abspath(model_path)
        model_path = os.path.relpath(model_path, build_path)

        if build_type == 'docker':
            generated_Dockerfile = self._create_training_server_Dockerfile(model_type=model_type,
                                                                      model_name=model_name,
                                                                      model_tag=model_tag,
                                                                      hyper_params=hyper_params,
                                                                      templates_path=templates_path,
                                                                      build_path=build_path)

            # TODO:  Expand hyper_params into build arguments
            cmd = 'docker build -t %s/%s/%s-%s-%s:%s --build-arg model_type=%s --build-arg model_name=%s --build-arg model_tag=%s --build-arg model_path=%s -f %s %s' % (build_registry_url, build_registry_repo, build_prefix, model_type, model_name, model_tag, model_type, model_name, model_tag, model_path, generated_Dockerfile, build_path)

            print(cmd)
            print("")
            process = subprocess.call(cmd, shell=True)
        else:
            print("Build type '%s' not found." % build_type)


    def training_server_start(self,
                          model_type,
                          model_name,
                          model_tag,
                          model_path,
                          hyper_params={},
                          memory_limit='2G',
                          core_limit='1000m',
                          build_registry_url='docker.io',
                          build_registry_repo='pipelineai',
                          build_prefix='train'):
        # TODO:  Use expand hyper_params into env vars
        cmd = 'docker run -itd --name=%s-%s-%s-%s -m %s -p 5000:5000 -p 6334:6334  %s/%s/%s-%s-%s:%s' % (build_prefix, model_type, model_name, model_tag, memory_limit, build_registry_url, build_registry_repo, build_prefix, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)

        # TODO:  Update status = TRAINED
 

    def training_server_stop(self,
                         model_type,
                         model_name,
                         model_tag,
                         build_prefix='train'):

        cmd = 'docker rm -f %s-%s-%s-%s' % (build_prefix, model_type, model_name, model_tag)

        print(cmd)
        print("")

        process = subprocess.call(cmd, shell=True)


    def _create_training_cluster_Kubernetes_yaml(self,
                            model_type,
                            model_name,
                            model_tag,
                            hyper_params,
                            ps_replicas,
                            worker_replicas,
                            templates_path=_default_templates_path,
                            build_registry_url='docker.io',
                            build_registry_repo='pipelineai',
                            build_prefix='train',
                            worker_memory_limit=None,
                            worker_core_limit=None):

        templates_path = os.path.expandvars(templates_path)
        templates_path = os.path.expanduser(templates_path)
        templates_path = os.path.abspath(templates_path)

        print("")
        print("Using templates in '%s'." % templates_path)
        print("(Specify --templates-path if the templates live elsewhere.)")
        print("")

        context = {'PIPELINE_MODEL_TYPE': model_type,
                   'PIPELINE_MODEL_NAME': model_name,
                   'PIPELINE_MODEL_TAG': model_tag,
                   'PIPELINE_WORKER_CORE_LIMIT': worker_core_limit,
                   'PIPELINE_WORKER_MEMORY_LIMIT': worker_memory_limit,
                   'PIPELINE_PS_REPLICAS': int(ps_replicas),
                   'PIPELINE_WORKER_REPLICAS': int(worker_replicas),
                   'PIPELINE_BUILD_REGISTRY_URL': build_registry_url,
                   'PIPELINE_BUILD_REGISTRY_REPO': build_registry_repo,
                   'PIPELINE_BUILD_REGISTRY_NAMESPACE': build_prefix}

        context = {**context, **hyper_params}

        model_clustered_template = os.path.join(templates_path, PipelineCli._kube_train_cluster_template_registry['train-cluster-cpu'][0][0])
        path, filename = os.path.split(model_clustered_template)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)
        rendered_filename = './generated-train-cluster-%s-%s-%s-cpu.yaml' % (model_type, model_name, model_tag)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
        print("'%s' -> '%s'." % (filename, rendered_filename))
 

    def training_cluster_connect(self,
                             model_type,
                             model_name,
                             model_tag,
                             local_port=None,
                             service_port=None,
                             build_prefix='train',
                             kube_namespace='default'):

        service_name = '%s-%s-%s-%s' % (build_prefix, model_type, model_name, model_tag)

        self._service_connect(service_name=service_name,
                                       kube_namespace=kube_namespace,
                                       local_port=local_port,
                                       service_port=service_port)

        print("")
        print("capability['training_cluster'] is not enabled.")
        print("")
        self.version()         

 
    def training_cluster_describe(self,
                              model_type,
                              model_name,
                              model_tag,
                              build_prefix='train',
                              kube_namespace='default'):
        service_name = '%s-%s-%s-%s' % (build_prefix, model_type, model_name, model_tag)

        self._service_describe(service_name=service_name)

        print("")
        print("capability['training_cluster'] is not enabled.")
        print("")
        self.version()


    def training_cluster_shell(self,
                     model_type,
                     model_name,
                     model_tag,
                     build_prefix='train'):

        service_name = '%s-%s-%s-%s' % (build_prefix, model_type, model_name, model_tag)

        self._service_shell(service_name=service_name,
                            kube_namespace=kube_namespace)

        print("")
        print("capability['training_cluster'] is not enabled.")
        print("")
        self.version()


    def training_cluster_start(self,
                              model_type,
                              model_name,
                              model_tag,
                              hyper_params,
                              ps_replicas,
                              worker_replicas,
                              templates_path=_default_templates_path,
                              kube_namespace='default',
                              build_registry_url='docker.io',
                              build_registry_repo='pipelineai',
                              build_prefix='train',
                              worker_memory_limit=None,
                              worker_core_limit=None):

        generated_yaml = self._create_training_cluster_Kubernetes_yaml(model_type=model_type,
                                                                 model_name=model_name,
                                                                 model_tag=model_tag,
                                                                 hyper_params=hyper_params,
                                                                 ps_replicas=ps_replicas,
                                                                 worker_replicas=worker_replicas,
                                                                 templates_path=templates_path,
                                                                 build_registry_url=build_registry_url,
                                                                 build_registry_repo=build_registry_repo,
                                                                 build_prefix=build_prefix,
                                                                 worker_memory_limit=worker_memory_limit,
                                                                 worker_core_limit=worker_core_limit)

        for rendered_yaml in rendered_yamls:
        # For now, only handle '-deploy' and '-svc' yaml's
            self._kube_create(yaml_path=generated_yaml,
                              kube_namespace=kube_namespace)

        print("")
        print("capability['training_cluster'] is not enabled.")
        print("")
        self.version()


    def training_cluster_stop(self,
                          model_type,
                          model_name,
                          model_tag,
                          build_prefix='train',
                          kube_namespace='default'):

        service_name = '%s-%s-%s-%s' % (build_prefix, model_type, model_name, model_tag)
        self._service_stop(service_name=service_name,
                           kube_namespace=kube_namespace)

        print("")
        print("capability['training_cluster'] is not enabled.")
        print("")
        self.version()


    def training_cluster_logs(self,
                             model_type,
                             model_name,
                             model_tag,
                             build_prefix='predict',
                             kube_namespace='default'):

        service_name = '%s-%s-%s-%s' % (build_prefix, model_type, model_name, model_tag)

        self._service_logs(service_name=service_name,
                           kube_namespace=kube_namespace)

        print("")
        print("capability['training_cluster'] is not enabled.")
        print("")
        self.version()



    def training_cluster_scale(self,
                           model_type,
                           model_name,
                           model_tag,
                           replicas,
                           build_prefix='train',
                           kube_namespace='default'):

        service_name = '%s-%s-%s-%s' % (build_prefix, model_type, model_name, model_tag)

        self._service_scale(service_name=service_name,
                            replicas=replicas,
                            kube_namespace=kube_namespace)

        print("")
        print("capability['training_cluster'] is not enabled.")
        print("")
        self.version()


    def _service_scale(self,
                       service_name,
                       replicas,
                       kube_namespace='default'):

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        # TODO:  Filter by namespace
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False, 
                                                                              pretty=True)
            found = False
            deployments = response.items
            for deploy in deployments:
                if service_name in deploy.metadata.name:
                    found = True
                    break
            if found:
                print("")
                print("Scaling service '%s' to '%s' replicas." % (deploy.metadata.name, replicas))
                print("")
                cmd = "kubectl scale deploy %s --replicas=%s" % (deploy.metadata.name, replicas)
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
            else:
                print("")
                print("App '%s' is not running." % service_name)
                print("") 


    def _environment_volumes(self):

        print("")
        print("Volumes")
        print("*******")
        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_persistent_volume(watch=False,
                                                            pretty=True)
            claims = response.items
            for claim in claims:
                print("%s" % (claim.metadata.name))

        print("")
        print("Volume Claims")
        print("*************")
        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_persistent_volume_claim_for_all_namespaces(watch=False,
                                                                                     pretty=True)
            claims = response.items
            for claim in claims:
                print("%s" % (claim.metadata.name))


    def _get_deploy_yamls(self, 
                          service_name):
        try:
            (deploy_yamls, dependencies) = PipelineCli._kube_deploy_registry[service_name]
        except:
            dependencies = []
            deploy_yamls = []

        if len(dependencies) > 0:
            for dependency in dependencies:
                deploy_yamls = deploy_yamls + self._get_deploy_yamls(service_name=dependency)

        return deploy_yamls 


    def _get_svc_yamls(self, 
                       service_name):
        try:
            (svc_yamls, dependencies) = PipelineCli._kube_svc_registry[service_name]
        except:
            dependencies = []
            svc_yamls = []
       
        if len(dependencies) > 0:
            for dependency_service_name in dependencies:
                svc_yamls = svc_yamls + self._get_svc_yamls(service_name=dependency_service_name)

        return svc_yamls


    def _kube_apply(self,
                    yaml_path,
                    kube_namespace='default'):

        cmd = "kubectl apply --namespace %s -f %s --save-config --record" % (kube_namespace, yaml_path)
        self._kube(cmd=cmd)


    def _kube_create(self,
                     yaml_path,
                     kube_namespace='default'):

        cmd = "kubectl create --namespace %s -f %s --save-config --record" % (kube_namespace, yaml_path)
        self._kube(cmd=cmd)


    def _kube_delete(self,
                     yaml_path,
                     kube_namespace='default'):

        cmd = "kubectl delete --namespace %s -f %s" % (kube_namespace, yaml_path)
        self._kube(cmd=cmd) 
   
 
    def _kube(self,
             cmd):
        print("")
        print("Running '%s'." % cmd)
        print("")
        subprocess.call(cmd, shell=True)
        print("")


    def _service_stop(self,
                      service_name,
                      kube_namespace='default'):

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False, pretty=True)
            found = False
            deployments = response.items
            for deploy in deployments:
                if service_name in deploy.metadata.name:
                    found = True
                    break
            if found:
                print("")
                print("Deleting service '%s'." % deploy.metadata.name)
                print("")
                cmd = "kubectl delete deploy %s" % deploy.metadata.name
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
                print("Check service status with 'pipeline cluster-status'.")
                print("")
            else:
                print("")
                print("Service '%s' is not running." % service_name)
                print("")


def main():
    fire.Fire(PipelineCli)


if __name__ == '__main__':
    main()
