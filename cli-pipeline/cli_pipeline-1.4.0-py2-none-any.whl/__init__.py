#-*- coding: utf-8 -*-

__version__ = "1.4.0"

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
import jinja2
import urllib3
urllib3.disable_warnings()

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
                                     'predict-server': (['predict-server-local-dockerfile.template'], []),
                                     'train-server': (['train-server-local-dockerfile.template'], []),
                                    }
    _kube_router_deploy_template_registry = {'predict-router-split': (['predict-router-split-deploy.yaml.template'], [])}
    _kube_router_ingress_template_registry = {'predict-router-split': (['predict-router-split-ingress.yaml.template'], [])}
    _kube_router_svc_template_registry = {'predict-router-split': (['predict-router-split-svc.yaml.template'], [])}

    _kube_cluster_autoscale_template_registry = {'predict-cluster': (['predict-cluster-autoscale.yaml.template'], [])}
    _kube_cluster_deploy_template_registry = {'predict-cluster': (['predict-cluster-deploy.yaml.template'], [])}
    _kube_cluster_svc_template_registry = {'predict-cluster': (['predict-cluster-svc.yaml.template'], [])}

    _kube_train_cluster_template_registry = {
                                             'train-cluster': (['train-cluster.yaml.template'], []),
                                            }
    _pipeline_api_version = 'v1'
    _default_pipeline_templates_path = os.path.join(os.path.dirname(__file__), 'templates/')
    _default_image_registry_url = 'docker.io'
    _default_image_registry_repo = 'pipelineai'
    _default_image_registry_train_namespace = 'train'
    _default_image_registry_predict_namespace = 'predict' 
    _default_image_registry_base_tag = 'cpu-1.4.0'
    _default_build_type = 'docker'
    _default_build_context_path = '.'

 
    def version(self):
        print('')
        print('cli_version: %s' % __version__)
        print('api_version: %s' % PipelineCli._pipeline_api_version)
        print('')
        print('default build type: %s' % PipelineCli._default_build_type)

        build_context_path = os.path.expandvars(PipelineCli._default_build_context_path)
        build_context_path = os.path.expanduser(build_context_path)
        build_context_path = os.path.abspath(build_context_path)

        print('default build context path: %s => %s' % (PipelineCli._default_build_context_path, build_context_path))
        print('')
        print('default train base image: %s/%s/%s:%s' % (PipelineCli._default_image_registry_url, PipelineCli._default_image_registry_repo, PipelineCli._default_image_registry_train_namespace, PipelineCli._default_image_registry_base_tag))
        print('default predict base image: %s/%s/%s:%s' % (PipelineCli._default_image_registry_url, PipelineCli._default_image_registry_repo, PipelineCli._default_image_registry_predict_namespace, PipelineCli._default_image_registry_base_tag))
        print('')
        print('capabilities_enabled: %s' % ['train_server', 'predict_server', 'predict', 'version'])
        print('capabilities_disabled: %s' % ['train_cluster', 'predict_cluster', 'optimize', 'experiment'])
        print('')
        print('Email upgrade@pipeline.ai to enable the advanced capabilities.')
        print('')


    def _templates_path(self):
        print("")
        print("templates_path: %s" % PipelineCli._default_pipeline_templates_path)
        print("")


    def predict_cluster_connect(self,
                                model_type,
                                model_name,
                                model_tag,
                                local_port=None,
                                service_port=None,
                                cluster_namespace=None,
                                image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_connect(service_name=service_name,
                              cluster_namespace=cluster_namespace,
                              local_port=local_port,
                              service_port=service_port)

        print("")
        print("capability['cluster'] is not enabled.")
        print("")
        self.version()


    def _service_connect(self,
                         service_name,
                         cluster_namespace=None,
                         local_port=None,
                         service_port=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

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
            cmd = 'kubectl port-forward %s :%s' % (pod.metadata.name, service_port)
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
            for deployment in deployments:
                self._service_resources(deployment.metadata.name)


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


    def _create_predict_server_Dockerfile(self,
                                          model_type,
                                          model_name,
                                          model_tag,
                                          model_path,
                                          image_registry_url,
                                          image_registry_repo,
                                          image_registry_namespace,
                                          image_registry_base_tag,
                                          pipeline_templates_path,
                                          build_context_path):

        print("")
        print("Using templates in '%s'." % pipeline_templates_path)
        print("")

        context = {
                   'PIPELINE_MODEL_TYPE': model_type,
                   'PIPELINE_MODEL_NAME': model_name,
                   'PIPELINE_MODEL_TAG': model_tag,
                   'PIPELINE_MODEL_PATH': model_path,
                   'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
                   'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
                   'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
                   'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag}


        model_predict_cpu_Dockerfile_templates_path = os.path.join(pipeline_templates_path, PipelineCli._Dockerfile_template_registry['predict-server'][0][0])
        path, filename = os.path.split(model_predict_cpu_Dockerfile_templates_path)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)
        rendered_Dockerfile = '%s/.pipeline-generated-%s-%s-%s-%s-Dockerfile' % (build_context_path, image_registry_namespace, model_type, model_name, model_tag)
        with open(rendered_Dockerfile, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'." % (filename, rendered_Dockerfile))

        return rendered_Dockerfile


    def predict_server_build(self,
                             model_type,
                             model_name,
                             model_tag,
                             model_path,
                             build_type=None,
                             build_context_path=None,
                             image_registry_url=None,
                             image_registry_repo=None,
                             image_registry_namespace=None,
                             image_registry_base_tag=None,
                             pipeline_templates_path=None):

        if not build_type:
            build_type = PipelineCli._default_build_type

        if not build_context_path: 
            build_context_path = PipelineCli._default_build_context_path

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        if not image_registry_base_tag:
            image_registry_base_tag = PipelineCli._default_image_registry_base_tag

        if not pipeline_templates_path:
            pipeline_templates_path = PipelineCli._default_pipeline_templates_path

        build_context_path = os.path.expandvars(build_context_path)
        build_context_path = os.path.expanduser(build_context_path)
        build_context_path = os.path.abspath(build_context_path)

        pipeline_templates_path = os.path.expandvars(pipeline_templates_path)
        pipeline_templates_path = os.path.expanduser(pipeline_templates_path)
        pipeline_templates_path = os.path.abspath(pipeline_templates_path)
        pipeline_templates_path = os.path.relpath(pipeline_templates_path, build_context_path)

        model_path = os.path.expandvars(model_path)
        model_path = os.path.expanduser(model_path)
        model_path = os.path.abspath(model_path)
        model_path = os.path.relpath(model_path, build_context_path)

        if build_type == 'docker':
            generated_Dockerfile = self._create_predict_server_Dockerfile(model_type=model_type, 
                                                                model_name=model_name,
                                                                model_tag=model_tag,
                                                                model_path=model_path,
                                                                image_registry_url=image_registry_url,
                                                                image_registry_repo=image_registry_repo,
                                                                image_registry_namespace=image_registry_namespace,
                                                                image_registry_base_tag=image_registry_base_tag,
                                                                pipeline_templates_path=pipeline_templates_path,
                                                                build_context_path=build_context_path)

            cmd = 'docker build -t %s/%s/%s-%s-%s:%s -f %s %s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_type, model_name, model_tag, generated_Dockerfile, build_context_path)

            print(cmd)
            print("")
            process = subprocess.call(cmd, shell=True)
        else:
            print("Build type '%s' not found." % build_type)


    def _create_predict_cluster_Kubernetes_yaml(self,
                                                model_type,
                                                model_name,
                                                model_tag,
                                                memory_limit='2Gi',
                                                core_limit='1000m',
                                                target_core_util_percentage='75',
                                                min_replicas='1',
                                                max_replicas='1',
                                                cluster_namespace=None,
                                                image_registry_url=None,
                                                image_registry_repo=None,
                                                image_registry_namespace=None,
                                                image_registry_base_tag=None,
                                                pipeline_templates_path=None):


        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        if not image_registry_base_tag:
            image_registry_base_tag = PipelineCli._default_image_registry_base_tag

        if not pipeline_templates_path:
            pipeline_templates_path = PipelineCli._default_pipeline_templates_path

        pipeline_templates_path = os.path.expandvars(pipeline_templates_path)
        pipeline_templates_path = os.path.expanduser(pipeline_templates_path)
        print("(Specify --piepline-templates-path if the templates live elsewhere.)")
        pipeline_templates_path = os.path.abspath(pipeline_templates_path)

        print("")
        print("Using templates in '%s'." % pipeline_templates_path)
        print("(Specify --pipeline-templates-path if the templates live elsewhere.)") 
        print("")
 
        context = {
                   'PIPELINE_MODEL_TYPE': model_type,
                   'PIPELINE_MODEL_NAME': model_name,
                   'PIPELINE_MODEL_TAG': model_tag,
                   'PIPELINE_CORE_LIMIT': core_limit,
                   'PIPELINE_MEMORY_LIMIT': memory_limit,
                   'PIPELINE_TARGET_CORE_UTIL_PERCENTAGE': target_core_util_percentage,
                   'PIPELINE_MIN_REPLICAS': min_replicas,
                   'PIPELINE_MAX_REPLICAS': max_replicas,
                   'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
                   'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
                   'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
                   'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag}

        rendered_filenames = []

        model_predict_deploy_yaml_templates_path = os.path.join(pipeline_templates_path, PipelineCli._kube_cluster_deploy_template_registry['predict-cluster'][0][0])
        path, filename = os.path.split(model_predict_deploy_yaml_templates_path)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)
        rendered_filename = './.pipeline-generated-%s-%s-%s-%s-cluster-deploy.yaml' % (image_registry_namespace, model_type, model_name, model_tag)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'." % (filename, rendered_filename))
            rendered_filenames += [rendered_filename]

        model_predict_svc_yaml_templates_path = os.path.join(pipeline_templates_path, PipelineCli._kube_cluster_svc_template_registry['predict-cluster'][0][0])
        path, filename = os.path.split(model_predict_svc_yaml_templates_path)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)    
        rendered_filename = './.pipeline-generated-%s-%s-%s-%s-cluster-svc.yaml' % (image_registry_namespace, model_type, model_name, model_tag)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'." % (filename, rendered_filename)) 
            rendered_filenames += [rendered_filename]

        model_router_deploy_yaml_templates_path = os.path.join(pipeline_templates_path, PipelineCli._kube_router_deploy_template_registry['predict-router-split'][0][0])
        path, filename = os.path.split(model_router_deploy_yaml_templates_path)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)
        rendered_filename = './.pipeline-generated-%s-%s-%s-%s-router-split-deploy.yaml' % (image_registry_namespace, model_type, model_name, model_tag)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'." % (filename, rendered_filename))
            rendered_filenames += [rendered_filename]

        model_router_ingress_yaml_templates_path = os.path.join(pipeline_templates_path, PipelineCli._kube_router_ingress_template_registry['predict-router-split'][0][0])
        path, filename = os.path.split(model_router_ingress_yaml_templates_path)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)
        rendered_filename = './.pipeline-generated-%s-%s-%s-%s-router-split-ingress.yaml' % (image_registry_namespace, model_type, model_name, model_tag)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'." % (filename, rendered_filename))
            rendered_filenames += [rendered_filename]

        model_router_svc_yaml_templates_path = os.path.join(pipeline_templates_path, PipelineCli._kube_router_svc_template_registry['predict-router-split'][0][0])
        path, filename = os.path.split(model_router_svc_yaml_templates_path)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)
        rendered_filename = './.pipeline-generated-%s-%s-%s-%s-router-split-svc.yaml' % (image_registry_namespace, model_type, model_name, model_tag)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'." % (filename, rendered_filename))
            rendered_filenames += [rendered_filename]

        return rendered_filenames


    def predict_server_shell(self,
                     model_type,
                     model_name,
                     model_tag,
                     image_registry_namespace=None):

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        cmd = 'docker exec -it %s-%s-%s-%s bash' % (image_registry_namespace, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def predict_server_push(self,
                         model_type,
                         model_name,
                         model_tag,
                         image_registry_url=None,
                         image_registry_repo=None,
                         image_registry_namespace=None):

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        cmd = 'docker push %s/%s/%s-%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def predict_server_pull(self,
                         model_type,
                         model_name,
                         model_tag,
                         image_registry_url=None,
                         image_registry_repo=None,
                         image_registry_namespace=None):

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        cmd = 'docker pull %s/%s/%s-%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def predict_server_start(self,
                          model_type,
                          model_name,
                          model_tag,
                          image_registry_url=None,
                          image_registry_repo=None,
                          image_registry_namespace=None,
                          memory_limit='2G'):

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        cmd = 'docker run -itd --name=%s-%s-%s-%s -m %s -p 6969:6969 -p 9090:9090 -p 3000:3000 %s/%s/%s-%s-%s:%s' % (image_registry_namespace, model_type, model_name, model_tag, memory_limit, image_registry_url, image_registry_repo, image_registry_namespace, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def predict_server_stop(self,
                         model_type,
                         model_name,
                         model_tag,
                         image_registry_namespace=None): 

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        cmd = 'docker rm -f %s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        print(cmd)
        print("")

        process = subprocess.call(cmd, shell=True)


    def predict_server_logs(self,
                         model_type,
                         model_name,
                         model_tag,
                         image_registry_namespace=None):

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        cmd = 'docker logs -f %s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        print(cmd)
        print("")

        process = subprocess.call(cmd, shell=True)


    def _service_rollout(self,
                         service_name,
                         service_image,
                         service_tag):

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                               pretty=True)
            found = False
            deployments = response.items
            for deployment in deployments:
                if service_name in deployment.metadata.name:
                    found = True
                    break
            if found:
                print("")
                print("Upgrading service '%s' using Docker image '%s:%s'." % (deployment.metadata.name, service_image, service_tag))
                print("")
                cmd = "kubectl set image deploy %s %s=%s:%s" % (deployment.metadata.name, deployment.metadata.name, service_image, service_tag)
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
                cmd = "kubectl rollout status deploy %s" % deployment.metadata.name
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
                cmd = "kubectl rollout history deploy %s" % deployment.metadata.name
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
            else:
                print("")
                print("App '%s' is not running." % service_name)
                print("")


    def _service_history(self,
                         service_name):

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                              pretty=True)
            found = False
            deployments = response.items
            for deployment in deployments:
                if service_name in deployment.metadata.name:
                    found = True
                    break
            if found:
                print("")
                cmd = "kubectl rollout status deploy %s" % deployment.metadata.name
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
                cmd = "kubectl rollout history deploy %s" % deployment.metadata.name
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
            else:
                print("")
                print("App '%s' is not running." % service_name)
                print("")


    def _service_rollback(self,
                          service_name,
                          revision=None):

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                              pretty=True)
            found = False
            deployments = response.items
            for deployment in deployments:
                if service_name in deployment.metadata.name:
                    found = True
                    break
            if found:
                print("")
                if revision:
                    print("Rolling back app '%s' to revision '%s'." % deployment.metadata.name, revision)
                    cmd = "kubectl rollout undo deploy %s --to-revision=%s" % (deployment.metadata.name, revision)
                else:
                    print("Rolling back app '%s'." % deployment.metadata.name)
                    cmd = "kubectl rollout undo deploy %s" % deployment.metadata.name
                print("")
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
                cmd = "kubectl rollout status deploy %s" % deployment.metadata.name
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
                cmd = "kubectl rollout history deploy %s" % deployment.metadata.name
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
            else:
                print("")
                print("App '%s' is not running." % service_name)
                print("")


    def _filter_tar(self,
                    tarinfo):
        # TODO:  Load this pipeline.yml 
        ignore_list = []
        for ignore in ignore_list:
            if ignore in tarinfo.name:
                return None

        return tarinfo


    def _tar(self,
             model_type,
             model_name,
             model_tag,
             model_path,
             tar_path='.',
             filemode='w',
             compression='gz'):

        print('model_type: %s' % model_type)
        print('model_name: %s' % model_name)
        print('model_tag: %s' % model_tag)
        print('model_path: %s' % model_path)
        print('tar_path: %s' % tar_path)
        print('filemode: %s' % filemode)
        print('compression: %s' % compression)

        model_path = os.path.expandvars(model_path)
        model_path = os.path.expanduser(model_path)
        model_path = os.path.abspath(model_path)

        tar_path = os.path.expandvars(tar_path)
        tar_path = os.path.expanduser(tar_path)
        tar_path = os.path.abspath(tar_path)
     
        tar_filename = '%s-%s-%s.tar.gz' % (model_type, model_name, model_tag)
        tar_path = os.path.join(tar_path, tar_filename) 
 
        print("")
        print("Compressing model_path '%s' into tar_path '%s'." % (model_path, tar_path))

        with tarfile.open(tar_path, '%s:%s' % (filemode, compression)) as tar:
            tar.add(model_path, arcname='.', filter=self._filter_tar)
        
        return tar_path


    def predict_cluster_start(self,
                              model_type,
                              model_name,
                              model_tag,
                              memory_limit='2Gi',
                              core_limit='1000m',
                              target_core_util_percentage='75',
                              min_replicas='1',
                              max_replicas='1',
                              cluster_namespace=None,
                              image_registry_url=None,
                              image_registry_repo=None,
                              image_registry_namespace=None,
                              image_registry_base_tag=None,
                              pipeline_templates_path=None,
                              timeout=1200):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        if not image_registry_base_tag:
            image_registry_base_tag = PipelineCli._default_image_registry_base_tag

        if not pipeline_templates_path:
            pipeline_templates_path = PipelineCli._default_pipeline_templates_path

        rendered_yamls = self._create_predict_cluster_Kubernetes_yaml(model_type=model_type,
                                          model_name=model_name,
                                          model_tag=model_tag,
                                          memory_limit=memory_limit,
                                          core_limit=core_limit,
                                          target_core_util_percentage=target_core_util_percentage,
                                          min_replicas=min_replicas,
                                          max_replicas=max_replicas,
                                          image_registry_url=image_registry_url,
                                          image_registry_repo=image_registry_repo,
                                          image_registry_namespace=image_registry_namespace,
                                          image_registry_base_tag=image_registry_base_tag,
                                          pipeline_templates_path=pipeline_templates_path)

        for rendered_yaml in rendered_yamls:
            # For now, only handle '-deploy' and '-svc' yaml's
            if '-deploy' in rendered_yaml or '-svc' in rendered_yaml:
                self._kube_create(yaml_path=rendered_yaml,
                                  cluster_namespace=cluster_namespace)

        print("")
        print("capability['cluster'] is not enabled.")
        print("")
        self.version()


    def _predict_cluster_deploy(self,
                                model_type,
                                model_name,
                                model_tag,
                                model_path,
                                deploy_server_url,
                                timeout=1200):

        model_path = os.path.expandvars(model_path)
        model_path = os.path.expanduser(model_path)
        model_path = os.path.abspath(model_path)

        tar_path = self._tar(model_type=model_type,
                             model_name=model_name,
                             model_tag=model_tag,
                             model_path=model_path,
                             tar_path='.',
                             filemode='w',
                             compression='gz')

        upload_key = 'file'
        upload_value = tar_path 

        full_model_deploy_url = "%s/api/%s/model/deploy/%s/%s/%s" % (deploy_server_url.rstrip('/'), PipelineCli._pipeline_api_version, model_type, model_name, model_tag) 

        with open(tar_path, 'rb') as fh:
            files = [(upload_key, (upload_value, fh))]
            print("")
            print("Deploying model tar.gz '%s' to '%s'." % (tar_path, full_model_deploy_url))
            headers = {'Accept': 'application/json'}
            try:
                response = requests.post(url=full_model_deploy_url, 
                                         headers=headers, 
                                         files=files, 
                                         timeout=timeout)

                if response.status_code != requests.codes.ok:
                    if response.text:
                        print("")
                        pprint(response.text)

                if response.status_code == requests.codes.ok:
                    print("")
                    print("Success!")
                    print("")
                else:
                    response.raise_for_status()
                    print("")
            except requests.exceptions.HTTPError as hte:
                print("Error while deploying model.\nError: '%s'" % str(hte))
                print("")
            except IOError as ioe:
                print("Error while deploying model.\nError: '%s'" % str(ioe))
                print("")
 
        if (os.path.isfile(tar_path)):
            print("")
            print("Cleaning up temporary file tar '%s'..." % tar_path)
            print("")
            os.remove(tar_path)

        print("")
        print("capability['cluster'] is not enabled.")
        print("")
        self.version()


    def optimize(self,
                 model_type,
                 model_name,
                 model_tag,
                 model_path,
                 optimize_type,
                 optimize_params):

        model_path = os.path.expandvars(model_path)
        model_path = os.path.expanduser(model_path)
        model_path = os.path.abspath(model_path)

        print('')
        print("capability['optimize'] is not enabled.")
        print('')
        self.version()


    def predict(self,
                model_type,
                model_name,
                model_tag,
                predict_server_url,
                test_request_path,
                test_request_concurrency=1,
                test_request_mime_type='application/json',
                test_response_mime_type='application/json'):

        from concurrent.futures import ThreadPoolExecutor, as_completed

        with ThreadPoolExecutor(max_workers=test_request_concurrency) as executor:
            for _ in range(test_request_concurrency):
                executor.submit(self._test_single_prediction(
                                              model_type=model_type,
                                              model_name=model_name,
                                              model_tag=model_tag,
                                              predict_server_url=predict_server_url,
                                              test_request_path=test_request_path,
                                              test_request_mime_type=test_request_mime_type,
                                              test_response_mime_type=test_response_mime_type))


    def _test_single_prediction(self,
                 model_type,
                 model_name,
                 model_tag,
                 predict_server_url,
                 test_request_path,
                 test_request_mime_type='application/json',
                 test_response_mime_type='application/json',
                 timeout=15):

        test_request_path = os.path.expandvars(test_request_path)
        test_request_path = os.path.expanduser(test_request_path)
        test_request_path = os.path.abspath(test_request_path)

        print('predict_server_url: %s' % predict_server_url)
        print('model_type: %s' % model_type)
        print('model_name: %s' % model_name)
        print('model_tag: %s' % model_tag)
        print('test_request_path: %s' % test_request_path)
        print('test_request_mime_type: %s' % test_request_mime_type)
        print('test_response_mime_type: %s' % test_response_mime_type)

        full_predict_server_url = "%s/api/%s/model/predict/%s/%s/%s" % (predict_server_url.rstrip('/'), PipelineCli._pipeline_api_version, model_type, model_name, model_tag)
        print("")
        print("Predicting with file '%s' using '%s'" % (test_request_path, full_predict_server_url))
        print("")

        with open(test_request_path, 'rb') as fh:
            model_input_binary = fh.read()

        headers = {'Content-type': test_request_mime_type, 'Accept': test_response_mime_type} 
        from datetime import datetime 

        begin_time = datetime.now()
        response = requests.post(url=full_predict_server_url, 
                                 headers=headers, 
                                 data=model_input_binary, 
                                 timeout=timeout)
        end_time = datetime.now()

        if response.text:
            print("")
            pprint(response.text)

        if response.status_code == requests.codes.ok:
            print("")
            print("Success!")

        total_time = end_time - begin_time
        print("")
        print("Request time: %s milliseconds" % (total_time.microseconds / 1000))
        print("")


    def train_cluster_status(self):
        self._cluster_status()


    def predict_cluster_status(self):
        self._cluster_status()


    def _cluster_status(self):
        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        print("")
        print("Versions")
        print("********")
        self.version()

        print("")
        print("Nodes")
        print("*****")
        self._get_all_nodes()

        self._environment_volumes()

        print("")
        print("Environment Resources")
        print("*********************")        
        self._environment_resources()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_service_for_all_namespaces(watch=False,
                                                                     pretty=True)
            services = response.items
            for svc in services:
                self._service_resources(service_name=svc.metadata.name)

        print("")
        print("Service Descriptions")
        print("********************")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_service_for_all_namespaces(watch=False,
                                                                     pretty=True)
            services = response.items
            for svc in services:
                self._service_describe(service_name=svc.metadata.name)

        print("")
        print("DNS Internal (Public)")
        print("*********************")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_service_for_all_namespaces(watch=False, 
                                                                     pretty=True)
            services = response.items
            for svc in services:
                ingress = 'Not public' 
                if svc.status.load_balancer.ingress and len(svc.status.load_balancer.ingress) > 0:
                    if (svc.status.load_balancer.ingress[0].hostname):
                        ingress = svc.status.load_balancer.ingress[0].hostname
                    if (svc.status.load_balancer.ingress[0].ip):
                        ingress = svc.status.load_balancer.ingress[0].ip               
                print("%s (%s)" % (svc.metadata.name, ingress))

        print("")
        print("Deployments")
        print("***********")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1_beta1.list_deployment_for_all_namespaces(watch=False,
                                                                              pretty=True)
            deployments = response.items
            for deployment in deployments:
                print("%s (Available Replicas: %s)" % (deployment.metadata.name, deployment.status.available_replicas))

        print("")
        print("Pods")
        print("****")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, 
                                                                 pretty=True)
            pods = response.items
            for pod in pods:
                print("%s (%s)" % (pod.metadata.name, pod.status.phase))

        print("")
        print("Note:  If you are using Minikube, use 'minikube service list'.")
        print("")

        #print("")
        #print("Ingress")
        #print("*******")
        #self._get_ingress_urls()


    def _get_pod_by_service_name(self,
                                 service_name):

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        found = False 
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, pretty=True)
            pods = response.items
            for pod in pods:
                if service_name in pod.metadata.name:
                    found = True
                    break
        if found:
            return pod
        else:
            return None


    def _get_svc_by_service_name(self,
                                 service_name):

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        found = False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_service_for_all_namespaces(watch=False, 
                                                                     pretty=True)
            services = response.items
            for svc in services:
                if service_name in svc.metadata.name:
                    found = True
                    break
        if found:
            return svc 
        else:
            return None


    def _get_all_available_services(self):

        available_services = list(PipelineCli._kube_deploy_registry.keys())
        available_services.sort()
        for service in available_services:
            print(service)


    def _get_all_nodes(self):

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_node(watch=False, pretty=True)
            nodes = response.items
            for node in nodes:
                print("%s" % node.metadata.labels['kubernetes.io/hostname'])


    def predict_cluster_shell(self,
                           model_type,
                           model_name,
                           model_tag,
                           cluster_namespace=None,
                           image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_shell(service_name=service_name,
                            cluster_namespace=cluster_namespace)

        print("")
        print("capability['cluster'] is not enabled.")
        print("")
        self.version()


    def _service_shell(self,
                       service_name,
                       cluster_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, 
                                                                 pretty=True)
            pods = response.items
            for pod in pods:
                if service_name in pod.metadata.name:
                    break
            print("")
            print("Connecting to '%s'" % pod.metadata.name)      
            print("")
            subprocess.call("kubectl exec -it %s bash" % pod.metadata.name, shell=True)
        print("")


    def predict_cluster_logs(self,
                          model_type,
                          model_name,
                          model_tag,
                          cluster_namespace=None,
                          image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_logs(service_name=service_name,
                           cluster_namespace=cluster_namespace)

        print("")
        print("capability['cluster'] is not enabled.")
        print("")
        self.version()


    def _service_logs(self,
                      service_name,
                      cluster_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        kubeconfig.load_kube_config()
        kubeclient_v1 = kubeclient.CoreV1Api()
        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = kubeclient_v1.list_pod_for_all_namespaces(watch=False, 
                                                                 pretty=True)
            found = False
            pods = response.items
            for pod in pods:
                if service_name in pod.metadata.name:
                    found = True
                    break
            if found:
                print("")
                print("Tailing logs on '%s'." % pod.metadata.name)
                print("")
                subprocess.call("kubectl logs -f %s" % pod.metadata.name, shell=True)
                print("")
            else:
                print("")
                print("App '%s' is not running." % service_name)
                print("")


    def predict_cluster_describe(self,
                              model_type,
                              model_name,
                              model_tag,
                              cluster_namespace=None,
                              image_registry_namespace=None):

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_describe(service_name=service_name)

        print("")
        print("capability['cluster'] is not enabled.")
        print("")
        self.version()


    def _service_describe(self,
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
                if service_name in pod.metadata.name:
                    break
            print("")
            print("Connecting to '%s'" % pod.metadata.name)
            print("")
            subprocess.call("kubectl describe pod %s" % pod.metadata.name, shell=True)
        print("")


    def predict_cluster_scale(self,
                           model_type,
                           model_name,
                           model_tag,
                           replicas,
                           cluster_namespace=None,
                           image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_scale(service_name=service_name,
                            replicas=replicas,
                            cluster_namespace=cluster_namespace)

        print("")
        print("capability['cluster'] is not enabled.")
        print("")
        self.version()


    # TODO:  See https://github.com/istio/istio/tree/master/samples/helloworld
    #             for more details on how istio + autoscaling work
    def predict_cluster_autoscale(self,
                                  model_type,
                                  model_name,
                                  model_tag,
                                  cpu_percent,
                                  min_replicas,
                                  max_replicas,
                                  cluster_namespace=None,
                                  image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        # TODO:  make sure resources/requests/cpu has been set to something in the yaml
        #        ie. istioctl kube-inject -f helloworld.yaml -o helloworld-istio.yaml
        #        then manually edit as follows:
        #
        #  resources:
        #    requests:
        #      cpu: 100m

        cmd = "kubectl autoscale deployment %s-%s-%s-%s --cpu-percent=%s --min=%s --max=%s" % (image_registry_namespace, model_type, model_name, model_tag, cpu_percent, min_replicas, max_replicas)
        print("")
        print("Running '%s'." % cmd)
        print("")
        subprocess.call(cmd, shell=True)
        cmd = "kubectl get hpa"
        print("")
        print("Running '%s'." % cmd)
        print("")
        subprocess.call(cmd, shell=True)
        print("")


    def _service_scale(self,
                       service_name,
                       replicas,
                       cluster_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

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
                cmd = "kubectl scale deploy %s --replicas=%s --namespace=%s" % (deploy.metadata.name, replicas, cluster_namespace)
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
                    cluster_namespace=None):


        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        cmd = "kubectl apply --namespace %s -f %s --save-config --record" % (cluster_namespace, yaml_path)
        self._kube(cmd=cmd)


    def _kube_create(self,
                     yaml_path,
                     cluster_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        cmd = "kubectl create --namespace %s -f %s --save-config --record" % (cluster_namespace, yaml_path)
        self._kube(cmd=cmd)


    def _kube_delete(self,
                     yaml_path,
                     cluster_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        cmd = "kubectl delete --namespace %s -f %s" % (cluster_namespace, yaml_path)
        self._kube(cmd=cmd) 
   
 
    def _kube(self, cmd):
        print("")
        print("Running '%s'." % cmd)
        print("")
        subprocess.call(cmd, shell=True)
        print("")


    def _get_ingress_urls(self):
        cmd = "kubectl get po -n istio-system -l istio=ingress"
        subprocess.call(cmd, shell=True)
        print("")


    def _get_ingress_url(self,
                         service_name):
    
        cmd = "$(kubectl get po -n istio-system -l istio=ingress -o 'jsonpath={.items[0].status.hostIP}'):$(kubectl get svc istio-ingress -n istio-system -o 'jsonpath={.spec.ports[0].nodePort}')" % service_name

        print("Running '%s'." % cmd)
        print("")
        subprocess.call(cmd, shell=True)
        print("")


    def _traffic_split(self,
                       model_type,
                       model_name,
                       model_tag,
                       split_percentage):

        # TODO:  Generate RouteRule
        cmd = "kubectl apply -f <(istioctl kube-inject -f .pipeline-generated-split-%s-%s-%s-%s.yaml)" % (model_type, model_name, model_tag, split_percentage)

        print("Running '%s'." % cmd)
        print("")
        subprocess.call(cmd, shell=True)
        print("")

        print("capability['experiment'] is not enabled.")
        print("")
        self.version()


    def experiment_add(self,
                       experiment_type,
                       experiment_name,
                       experiment_tag,
                       model_type,
                       model_name,
                       model_tag,
                       router_percentage,
                       router_type='split',
                       optimization_fn=None):

        # TODO:  Generate RouteRule
        cmd = "kubectl apply -f <(istioctl kube-inject -f .pipeline-generated-experiment-%s-%s-%s-%s-%s-%s-%s.yaml)" % (image_registry_namespace, model_type, model_name, model_tag)

        print("Running '%s'." % cmd)
        print("")
        subprocess.call(cmd, shell=True)
        print("")

        print("capability['experiment'] is not enabled.")
        print("")
        self.version()


    def experiment_update(self,
                            experiment_type,
                            experiment_name,
                            experiment_tag,
                            model_type,
                            model_name,
                            model_tag,
                            router_percentage,
                            router_type='split',
                            optimization_fn=None):

        print("")
        print("capability['experiment'] is not enabled.")
        print("")
        self.version()


    def experiment_start(self,
                            experiment_type,
                            experiment_name,
                            experiment_tag):

        print("")
        print("capability['experiment'] is not enabled.")
        print("")
        self.version()


    def experiment_stop(self,
                            experiment_type,
                            experiment_name,
                            experiment_tag):

        print("")
        print("capability['experiment'] is not enabled.")
        print("")
        self.version()

 
    def experiment_status(self,
                            experiment_type,
                            experiment_name,
                            experiment_tag):

        print("")
        print("capability['experiment'] is not enabled.")
        print("")
        self.version()


#    def cluster_start(self,
#                      service_name,
#                      git_home='https://github.com/PipelineAI/pipeline',
#                      git_version='master',
#                      cluster_namespace='default'):

#        deploy_yaml_filenames = []
#        svc_yaml_filenames = []

#        deploy_yaml_filenames = deploy_yaml_filenames + self._get_deploy_yamls(service_name=service_name)
#        deploy_yaml_filenames = ['%s/%s/%s' % (git_home, git_version, deploy_yaml_filename) for deploy_yaml_filename in deploy_yaml_filenames]
#        deploy_yaml_filenames = [deploy_yaml_filename.replace('github.com', 'raw.githubusercontent.com') for deploy_yaml_filename in deploy_yaml_filenames]
#        print("Using '%s'" % deploy_yaml_filenames)
 
#        svc_yaml_filenames = svc_yaml_filenames + self._get_svc_yamls(service_name=service_name)
#        svc_yaml_filenames = ['%s/%s/%s' % (git_home, git_version, svc_yaml_filename) for svc_yaml_filename in svc_yaml_filenames]
#        svc_yaml_filenames = [svc_yaml_filename.replace('github.com', 'raw.githubusercontent.com') for svc_yaml_filename in svc_yaml_filenames]
#        print("Using '%s'" % svc_yaml_filenames)

#        kubeconfig.load_kube_config()
#        kubeclient_v1 = kubeclient.CoreV1Api()
#        kubeclient_v1_beta1 = kubeclient.ExtensionsV1beta1Api()

#        print("")
#        print("Starting service '%s'." % service_name)
#        print("")
#        print("Kubernetes Deployments:")
#        print("")
#        for deploy_yaml_filename in deploy_yaml_filenames:
#            cmd = "kubectl apply --save-config -f %s --record" % deploy_yaml_filename
#            print("Running '%s'." % cmd)
#            print("")
#            subprocess.call(cmd, shell=True)
#            print("")
#        print("")
#        print("Kubernetes Services:")
#        print("")
#        for svc_yaml_filename in svc_yaml_filenames:
#            cmd = "kubectl apply --save-config -f %s --record" % svc_yaml_filename
#            print("Running '%s'." % cmd)
#            print("")
#            subprocess.call(cmd, shell=True)
#            print("")
#        print("")
#        print("Ignore any 'Already Exists' errors.  These are OK.")
#        print("")


    def predict_cluster_stop(self,
                          model_type,
                          model_name,
                          model_tag,
                          cluster_namespace=None,
                          image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_predict_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)
        self._service_stop(service_name=service_name, 
                           cluster_namespace=cluster_namespace)

        print("")
        print("capability['cluster'] is not enabled.")
        print("")
        self.version()


    def _service_stop(self,
                      service_name,
                      cluster_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

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
                cmd = "kubectl delete deploy %s --namespace %s" % (deploy.metadata.name, cluster_namespace)
                print("Running '%s'." % cmd)
                print("")
                subprocess.call(cmd, shell=True)
                print("")
            else:
                print("")
                print("Service '%s' is not running." % service_name)
                print("")



    def train_server_pull(self,
                         model_type,
                         model_name,
                         model_tag,
                         image_registry_url=None,
                         image_registry_repo=None,
                         image_registry_namespace=None):

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        cmd = 'docker pull %s/%s/%s-%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def train_server_push(self,
                         model_type,
                         model_name,
                         model_tag,
                         image_registry_url=None,
                         image_registry_repo=None,
                         image_registry_namespace=None):

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        cmd = 'docker push %s/%s/%s-%s-%s:%s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def train_server_logs(self,
                            model_type,
                            model_name,
                            model_tag,
                            image_registry_namespace=None):

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        cmd = 'docker logs -f %s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        print(cmd)
        print("")

        process = subprocess.call(cmd, shell=True)


    def train_server_shell(self,
                           model_type,
                           model_name,
                           model_tag,
                           image_registry_namespace=None):

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        cmd = 'docker exec -it %s-%s-%s-%s bash' % (image_registry_namespace, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def _create_train_server_Dockerfile(self,
                                      model_type,
                                      model_name,
                                      model_tag,
                                      model_path,
                                      pipeline_templates_path,
                                      build_context_path,
                                      image_registry_url,
                                      image_registry_repo,
                                      image_registry_namespace,
                                      image_registry_base_tag):

        print("")
        print("Using templates in '%s'." % pipeline_templates_path)
        print("(Specify --pipeline-templates-path if the templates live elsewhere.)")
        print("")

        context = {'PIPELINE_MODEL_TYPE': model_type,
                   'PIPELINE_MODEL_NAME': model_name,
                   'PIPELINE_MODEL_TAG': model_tag,
                   'PIPELINE_MODEL_PATH': model_path,
                   'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
                   'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
                   'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
                   'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag}

        model_train_cpu_Dockerfile_templates_path = os.path.join(pipeline_templates_path, PipelineCli._Dockerfile_template_registry['train-server'][0][0])
        path, filename = os.path.split(model_train_cpu_Dockerfile_templates_path)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)
        rendered_filename = '%s/.pipeline-generated-%s-%s-%s-%s-Dockerfile' % (build_context_path, image_registry_namespace, model_type, model_name, model_tag)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
            print("'%s' => '%s'." % (filename, rendered_filename))

        return rendered_filename


    def train_server_build(self,
                          model_type,
                          model_name,
                          model_tag,
                          model_path,
                          build_type=None,
                          build_context_path=None,
                          image_registry_url=None,
                          image_registry_repo=None,
                          image_registry_namespace=None,
                          image_registry_base_tag=None,
                          pipeline_templates_path=None):

        if not build_type:
            build_type = PipelineCli._default_build_type

        if not build_context_path:
            build_context_path = PipelineCli._default_build_context_path

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        if not image_registry_base_tag:
            image_registry_base_tag = PipelineCli._default_image_registry_base_tag

        if not pipeline_templates_path:
            pipeline_templates_path = PipelineCli._default_pipeline_templates_path

        build_context_path = os.path.expandvars(build_context_path)
        build_context_path = os.path.expanduser(build_context_path)
        build_context_path = os.path.abspath(build_context_path)

        pipeline_templates_path = os.path.expandvars(pipeline_templates_path)
        pipeline_templates_path = os.path.expanduser(pipeline_templates_path)
        pipeline_templates_path = os.path.abspath(pipeline_templates_path)
        pipeline_templates_path = os.path.relpath(pipeline_templates_path, build_context_path)

        model_path = os.path.expandvars(model_path)
        model_path = os.path.expanduser(model_path)
        model_path = os.path.abspath(model_path)
        model_path = os.path.relpath(model_path, build_context_path)

        if build_type == 'docker':
            generated_Dockerfile = self._create_train_server_Dockerfile(model_type=model_type,
                                                                       model_name=model_name,
                                                                       model_tag=model_tag,
                                                                       model_path=model_path,
                                                                       build_context_path=build_context_path,
                                                                       image_registry_url=image_registry_url,
                                                                       image_registry_repo=image_registry_repo,
                                                                       image_registry_namespace=image_registry_namespace,
                                                                       image_registry_base_tag=image_registry_base_tag,
                                                                       pipeline_templates_path=pipeline_templates_path)

            cmd = 'docker build -t %s/%s/%s-%s-%s:%s -f %s %s' % (image_registry_url, image_registry_repo, image_registry_namespace, model_type, model_name, model_tag, generated_Dockerfile, build_context_path)

            print(cmd)
            print("")
            process = subprocess.call(cmd, shell=True)
        else:
            print("Build type '%s' not found." % build_type)


    def train_server_start(self,
                           model_type,
                           model_name,
                           model_tag,
                           hyper_params='',
                           memory_limit='2G',
                           core_limit='1000m',
                           image_registry_url=None,
                           image_registry_repo=None,
                           image_registry_namespace=None):
 
        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        cmd = 'docker run -itd -p 6334:6334 -e PIPELINE_MODEL_HYPER_PARAMS=%s --name=%s-%s-%s-%s -m %s %s/%s/%s-%s-%s:%s' % (hyper_params, image_registry_namespace, model_type, model_name, model_tag, memory_limit, image_registry_url, image_registry_repo, image_registry_namespace, model_type, model_name, model_tag)
        print(cmd)
        print("")
        process = subprocess.call(cmd, shell=True)


    def train_server_stop(self,
                         model_type,
                         model_name,
                         model_tag,
                         image_registry_namespace=None):

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        cmd = 'docker rm -f %s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        print(cmd)
        print("")

        process = subprocess.call(cmd, shell=True)


    def _create_train_cluster_Kubernetes_yaml(self,
                                              model_type,
                                              model_name,
                                              model_tag,
                                              model_path,
                                              master_replicas,
                                              ps_replicas,
                                              worker_replicas,
                                              hyper_params='',
                                              image_registry_url=None,
                                              image_registry_repo=None,
                                              image_registry_namespace=None,
                                              image_registry_base_tag=None,
                                              pipeline_templates_path=None,
                                              worker_memory_limit="2Gi",
                                              worker_core_limit="1000m"):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        if not image_registry_base_tag:
            image_registry_base_tag = PipelineCli._default_image_registry_base_tag

        if not pipeline_templates_path:
            pipeline_templates_path = PipelineCli._default_pipeline_templates_path

        pipeline_templates_path = os.path.expandvars(pipeline_templates_path)
        pipeline_templates_path = os.path.expanduser(pipeline_templates_path)
        pipeline_templates_path = os.path.abspath(pipeline_templates_path)

        print("")
        print("Using templates in '%s'." % pipeline_templates_path)
        print("(Specify --pipeline-templates-path if the templates live elsewhere.)")
        print("")

        context = {
                   'PIPELINE_MODEL_TYPE': model_type,
                   'PIPELINE_MODEL_NAME': model_name,
                   'PIPELINE_MODEL_TAG': model_tag,
                   'PIPELINE_MODEL_PATH': model_path,
                   'PIPELINE_MODEL_HYPER_PARAMS': hyper_params,
                   'PIPELINE_WORKER_CORE_LIMIT': worker_core_limit,
                   'PIPELINE_WORKER_MEMORY_LIMIT': worker_memory_limit,
                   'PIPELINE_MASTER_REPLICAS': int(master_replicas),
                   'PIPELINE_PS_REPLICAS': int(ps_replicas),
                   'PIPELINE_WORKER_REPLICAS': int(worker_replicas),
                   'PIPELINE_IMAGE_REGISTRY_URL': image_registry_url,
                   'PIPELINE_IMAGE_REGISTRY_REPO': image_registry_repo,
                   'PIPELINE_IMAGE_REGISTRY_NAMESPACE': image_registry_namespace,
                   'PIPELINE_IMAGE_REGISTRY_BASE_TAG': image_registry_base_tag}

        # TODO:  Merge with hyper_params
        #context = {**context, **hyper_params}

        model_clustered_template = os.path.join(pipeline_templates_path, PipelineCli._kube_train_cluster_template_registry['train-cluster'][0][0])
        path, filename = os.path.split(model_clustered_template)
        rendered = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(context)
        rendered_filename = './.pipeline-generated-%s-cluster-%s-%s-%s.yaml' % (image_registry_namespace, model_type, model_name, model_tag)
        with open(rendered_filename, 'wt') as fh:
            fh.write(rendered)
        print("'%s' => '%s'." % (filename, rendered_filename))

        return rendered_filename


    def train_cluster_connect(self,
                             model_type,
                             model_name,
                             model_tag,
                             local_port=None,
                             service_port=None,
                             cluster_namespace=None,
                             image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_connect(service_name=service_name,
                              cluster_namespace=cluster_namespace,
                              local_port=local_port,
                              service_port=service_port)

        print("")
        print("capability['train_cluster'] is not enabled.")
        print("")
        self.version()


    def train_cluster_describe(self,
                               model_type,
                               model_name,
                               model_tag,
                               cluster_namespace=None,
                               image_registry_namespace=None):
        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_describe(service_name=service_name)

        print("")
        print("capability['train_cluster'] is not enabled.")
        print("")
        self.version()


    def train_cluster_shell(self,
                            model_type,
                            model_name,
                            model_tag,
                            cluster_namespace=None,
                            image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_shell(service_name=service_name,
                            cluster_namespace=cluster_namespace)

        print("")
        print("capability['train_cluster'] is not enabled.")
        print("")
        self.version()


    def train_cluster_start(self,
                            model_type,
                            model_name,
                            model_tag,
                            master_replicas,
                            ps_replicas,
                            worker_replicas,
                            hyper_params='',
                            pipeline_templates_path=None,
                            cluster_namespace=None,
                            image_registry_url=None,
                            image_registry_repo=None,
                            image_registry_namespace=None,
                            image_registry_base_tag=None,
                            worker_memory_limit=None,
                            worker_core_limit=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_url:
            image_registry_url = PipelineCli._default_image_registry_url

        if not image_registry_repo:
            image_registry_repo = PipelineCli._default_image_registry_repo

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        if not image_registry_base_tag:
            image_registry_base_tag = PipelineCli._default_image_registry_base_tag

        if not pipeline_templates_path:
            pipeline_templates_path = PipelineCli._default_pipeline_templates_path

        generated_yaml = self._create_train_cluster_Kubernetes_yaml(model_type=model_type,
                                                                    model_name=model_name,
                                                                    model_tag=model_tag,
                                                                    master_replicas=master_replicas,
                                                                    ps_replicas=ps_replicas,
                                                                    worker_replicas=worker_replicas,
                                                                    hyper_params=hyper_params,
                                                                    image_registry_base_tag=image_registry_base_tag,
                                                                    pipeline_templates_path=pipeline_templates_path,
                                                                    cluster_namespace=cluster_namespace,
                                                                    image_registry_url=image_registry_url,
                                                                    image_registry_repo=image_registry_repo,
                                                                    image_registry_namespace=image_registry_namespace,
                                                                    worker_memory_limit=worker_memory_limit,
                                                                    worker_core_limit=worker_core_limit)

        # For now, only handle '-deploy' and '-svc' yaml's
        self._kube_create(yaml_path=generated_yaml,
                          cluster_namespace=cluster_namespace)

        print("")
        print("capability['train_cluster'] is not enabled.")
        print("")
        self.version()


    def train_cluster_stop(self,
                          model_type,
                          model_name,
                          model_tag,
                          cluster_namespace=None,
                          image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)
        self._service_stop(service_name=service_name,
                           cluster_namespace=cluster_namespace)

        print("")
        print("capability['train_cluster'] is not enabled.")
        print("")
        self.version()


    def train_cluster_logs(self,
                             model_type,
                             model_name,
                             model_tag,
                             cluster_namespace=None,
                             image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_logs(service_name=service_name,
                           cluster_namespace=cluster_namespace)

        print("")
        print("capability['train_cluster'] is not enabled.")
        print("")
        self.version()


    def train_cluster_scale(self,
                           model_type,
                           model_name,
                           model_tag,
                           replicas,
                           cluster_namespace=None,
                           image_registry_namespace=None):

        if not cluster_namespace:
            cluster_namespace = PipelineCli._default_cluster_namespace

        if not image_registry_namespace:
            image_registry_namespace = PipelineCli._default_image_registry_train_namespace

        service_name = '%s-%s-%s-%s' % (image_registry_namespace, model_type, model_name, model_tag)

        self._service_scale(service_name=service_name,
                            replicas=replicas,
                            cluster_namespace=cluster_namespace)

        print("")
        print("capability['train_cluster'] is not enabled.")
        print("")
        self.version()


def main():
    fire.Fire(PipelineCli)


if __name__ == '__main__':
    main()
