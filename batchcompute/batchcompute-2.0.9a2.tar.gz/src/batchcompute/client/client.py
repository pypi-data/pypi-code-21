"""Implementation of batchcompute service Client."""
import time
import datetime
from functools import wraps

from .response import (
    Job, Task, Image, Instance, Image, Cluster, ClusterInstance,
    RawResponse, ListResponse, GetResponse, ActionResponse, 
    CreateResponse, Quota, App, AppRevision, SynchronousInstance,
)
from batchcompute.core import Api
from batchcompute.core.exceptions import (ClientError, FieldError)
from batchcompute.resources import (
    JobDescription, ImageDescription, ClusterDescription,
    ModifyClusterDescription, AppDescription, AppJobDescription,
)
from batchcompute.utils import (
    CamelCasedClass, remap, add_metaclass, get_logger
)
from batchcompute.utils.functions import (
    import_json, add_region, partial, set_api_version, get_api_version, 
    get_all_region,
)
from batchcompute.utils.constants import STRING, DEFAULT_LIST_ITEM, COLLECTION

json = import_json()
logger = get_logger('batchcompute.client')

################
#HELPER CLASSES#
################

class CheckedApi(object):
    """Class to add error checking for all http method.

    If http status code is not 2XX, a ClientError will be raised.
    """

    def __init__(self, 
                 region, 
                 access_key_id, 
                 access_key_secret, 
                 security_token,
                 security_conn,
                 human_readable=False,
                 **headers):
        self._c = Api(
                    region, 
                    access_key_id, 
                    access_key_secret,
                    security_token,
                    security_conn,
                    **headers)
        self._h = human_readable

    def __getattr__(self, attr):
        methods_to_check = [
            'post',
            'put',
            'get',
            'delete',
            'patch',
        ]
        raw_method = getattr(self._c, attr)
        if attr in methods_to_check:
            method = self.check_wrapper(raw_method)
        else:
            method = raw_method
        return method

    def check_wrapper(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            raw_response = f(*args, **kwargs)
            return self._check(raw_response)
        return wrapper

    def _check(self, response):
        """Check http response, return it or raise a ClientError"""
        status = response.status
        if status//100 == 2:
            # Response for a valid request. 
            return response
        else:
            # Response for a invliad request.
            # Body is usually a error json string.
            request_id = response.getheader('x-acs-request-id') or response.getheader('request-id')
            response_body = response.read()
            default_code = "Unkown code"
            default_msg = "Unkown reason"

            from batchcompute.core.exceptions import JsonError
            try:
                error = remap(response_body, self._h)
            except JsonError:
                err_code = "Json Error, a HTML returned from upstream server."
                err_msg = "response_body: %s" % response_body
            else:
                err_code = error.get("Code", default_code) or default_code 
                err_msg = error.get("Message", default_msg) or default_msg 

            logger.error("Error status: %s\n"
                         "Error code: %s\n"
                         "Error request Id: %s\n"
                         "Error message: %s\n",
                         status, err_code, request_id, err_msg)
            raise ClientError(status, err_code, request_id, err_msg)


#####################
#BatchCompute Client#
#####################

class Client(object):
    """Implementation of client to use BatchCompute service."""

    def __init__(self, 
                 region, 
                 access_key_id, 
                 access_key_secret, 
                 security_token="",
                 security_conn=False,
                 human_readable=False,
                 **headers
                 ):
        """
        @params `region`: service region.
        @type `region`: import `region` from batchcompute root package, [
            CN_QINGDAO, CN_SHENZHEN] allowed.
    
        @params `access_key_id`: access key id in Aliyun.
        @type `access_key_id`: usually a {str}. 

        @params `access_key_secret`: access secret key in Aliyun.
        @type `access_key_secret`: usually a {str}. 

        @params `security_token`: STS token.
        @type `security_token`: a {str} STS token.

        @params `security_conn`: use HTTPS.
        @parames `security_conn`: {bool}, default False.

        @params `human_readable`: unused now.
        @type `human_readable`: {bool}, default: False.
            
        """
        self._h= human_readable
        self._sa = CheckedApi(
                    region, 
                    access_key_id, 
                    access_key_secret, 
                    security_token,
                    security_conn,
                    self._h,
                    **headers)

    def _get_id(self, resource):
        if isinstance(resource, STRING):
            id_ = resource
        elif hasattr(resource, 'Id'):
            id_ = resource.Id
        else:
            raise TypeError("""Invalid resource type""")

        if not id_.strip():
            raise TypeError("""Id can't be empty""")
        return id_

    def get_version(self):
        """Get api version number.

        Return the api version number string.
        """
        return get_api_version()

    def set_version(self, value):
        """Set api version number.

        @param `value`: api version number will be sent to batchcompute
            service.
        @type `value`: a {str} as `2015-11-11`
        """
        return set_api_version(value)
    version = property(get_version, set_version, None, "api version")

    @staticmethod
    def register_region(region_name, url, port=80):
        add_region(region_name, url, port)

    @staticmethod
    def get_regions():
        return get_all_region()

    def _do_create(self, resource_type, resource_desc, idempotent_token, params={}, sync=False):
        """Create a new resource in server and return a CreateResponse object. 

        @param `resource_type`: the resource type. 
        @type `resource_type`: a {str}, only ['jobs', 'clusters', 'images'] 
            permitted now.

        @param `resource_desc`: description object.
        @type `resource_desc`: a json {str}, a {dict} or a {`resource_type`}
            instance which descripts a new resource instance, you can 
            reference for the resource related official documentation of 
            BatchCompute service.

        @params `idempotent_token`: token ensure idempotency of requests.
        @type `idempotent_token`: a {str} specified by user.

        @return: A CreateResponse object when request handled successfully.

        @raise: A ClientError object when error occurs.
        """
        resource = resource_type(resource_desc)
        # Validate parameters.
        # It will raise an exception if invalid parameters exist.
        resource.validate()
        
        p = params
        if idempotent_token and isinstance(idempotent_token, STRING):
            p = {
                'IdempotentToken': idempotent_token 
            }
        res = self._sa.post(resource_type.resource_name, params=p, body=resource.dump())
        return CreateResponse(res, self._h)

    def _do_get(self, return_type, resource_name, resource, attrs=[], params={}):
        """Get life-cycle status information of a resource"""
        resource_id = self._get_id(resource)
        res = self._sa.get(resource_name, resource_id, attrs, params)
        return GetResponse(res, return_type, self._h)

    def _do_delete(self, resource_name, resource, params={}):
        """Release a given resource in server."""
        resource_id = self._get_id(resource)
        res = self._sa.delete(resource_name, resource_id, params=params)
        return ActionResponse(res, self._h)

    def _do_action(self, resource_name, resource, action):
        resource_id = self._get_id(resource)
        resource_paths = [resource_name, resource_id, action]
        formatted_resource = '/'.join(resource_paths) 
        # TODO patch method is now not available.
        res = self._sa.post(formatted_resource, '')
        return ActionResponse(res, self._h)

    def create_app(self, app_desc, token=''):
        """Create a new app """

        return self._do_create(AppDescription, app_desc, idempotent_token=token)

    def delete_app(self, app_name, qualifier=""):
        """Release an app """

        params = {
            "Qualifier": qualifier
        }
        return self._do_delete("apps", app_name, params=params)

    def get_app(self, app_name, scope="Private"):
        """Get an app"""

        if scope not in ["Private", "Public"]:
            raise FieldError("scope must be Private or Public")

        params={
            "Scope": scope
        }

        return self._do_get(App, "apps", app_name, params=params)

    def get_app_detail(self, app, qualifier=''):
        """Get the app detail"""

        if not isinstance(qualifier, STRING):
            raise FieldError("detail must be bool and qualifier must be string")

        params = {
            "Detail": "True",
            "Qualifier": qualifier
        }

        return self._do_get(AppDescription, "apps", app, params=params)


    def get_app_revisions(self, app_name):
        """Get the app revisions"""
        params = {
                'Revisions': str(True)
        }
        
        resource_id = self._get_id(app_name)
        res = self._sa.get("apps", resource_id, params=params)
        return ListResponse(res, AppRevision, self._h)

    def list_apps(self, scope='Private', marker='', max_item_count=50):
        """List all apps"""

        p = {
            'Scope': scope,
            'Marker': marker,
            'MaxItemCount': str(max_item_count)
        }

        res = self._sa.get('apps', params=p)
        return ListResponse(res, App, self._h)

    def modify_app(self, app_name, app_desc):
        app = self._get_id(app_name)
        res = self._sa.put('apps', app, body=AppDescription(app_desc).dump())
        return ActionResponse(res, self._h)

    def create_job(self, job_desc, token='', sync=False):
        """Create a new job in server.

        @param `job_desc`: a object descripts a job.
        @type `job_desc`: a json {str}, a {dict} object, or a {Job} object.  

        @param `token`: idempotent token.
        @type `token`: a {str} specified by user.

        @example:

            >>> from batchcompute import Client, ClientError
            ... from batchcompute import CN_QINGDAO as REGION 
            ... from batchcompute.resources import JobDescription, TaskDescription, DAG
            ... # some other codes here
            ... access_key_id = ... # your_access_key_id
            ... access_key_secret = ... # your_access_key_secret
            ... cluster_id = ... # ID of cluster created before
            ... Client = Client(REGION, access_key_id, access_key_secret)
            ... 
            ... try: 
            ...     job_desc = JobDescription()
            ...     map_task = TaskDescription()

            ...     # Create map task.
            ...     map_task.Parameters.Command.CommandLine = "ping -n 3 127.0.0.1"
            ...     map_task.Parameters.Command.PackagePath = ""
            ...     map_task.Parameters.StdoutRedirectPath = "oss://xxx/xxx/" 
            ...     map_task.Parameters.StderrRedirectPath = "oss://xxx/xxx/" 
            ...     map_task.InstanceCount = 3
            ...     # cluster_id is a cluster created in batchcompute service before.
            ...     map_task.ClusterId = cluster_id

            ...     # Create task dag.
            ...     task_dag = DAG()
            ...     task_dag.add_task(task_name='Map', task=map_task)

            ...     # Create job description.
            ...     job_desc.DAG = task_dag
            ...     job_desc.Priority = 99
            ...     job_desc.Name = 'PythonSDKDemo' 
            ...     job_desc.JobFailOnInstanceFail = True
            ...
            ...     job_id = client.create_job(job_desc).Id
            ...     # Wait job finished.
            ...     errs = client.poll(job_id)
            ...     if errs: print ('\n'.join(errs))
            ... except ClientError, e:
            ...     print (e.get_status_code(), e.get_code(), e.get_requestid(), e.get_msg())
        """
        resource_type = JobDescription if isinstance(job_desc, JobDescription) else AppJobDescription
        if sync and resource_type is AppJobDescription:
            resource = resource_type(job_desc)
            # Validate parameters.
            # It will raise an exception if invalid parameters exist.
            resource.validate()

            p = {
                "sync": ""
            }
            if token and isinstance(token, STRING):
                p['IdempotentToken'] = token
            res = self._sa.post(resource_type.resource_name, params=p, body=resource.dump())
            return GetResponse(res, SynchronousInstance, self._h)
        else:
            return self._do_create(resource_type, job_desc, idempotent_token=token)

    def stop_job(self, job):
        """Stop a running or waiting job. 

        @Notice:
            Only running or waiting jobs can be stopped.

        @params `job`: a batchcompute job.
        @type `job`: a 'job-' started {str} or a CreateResponse object.

        @example:
            >>> client = Client(region, id, key)
            ... job_id = 'job-xxxx' 
            ... client.stop_job(job_id)
        """
        return self._do_action('jobs', job, 'stop')

    def start_job(self, job):
        """Restart a stopped job.

        @Notice:
            Only stopped jobs can be restart.

        @params `job`: a batchcompute job.
        @type `job`: a 'job-' started {str} or a CreateResponse object.

        @example:
            >>> client = Client(region, id, key)
            ... job_id = 'job-xxxx' 
            ... client.start_job(job_id)
        """
        return self._do_action('jobs', job, 'start')

    def delete_job(self, job):
        """Release a job. 

        @Notice:
            Only Failed, Stopped, Finished job can be deleted.

        @params `job`: a batchcompute job.
        @type `job`: a 'job-' started {str} or a CreateResponse object.

        @example:
            >>> client = Client(region, id, key)
            ... job_id = 'job-xxxx' 
            ... client.delete_job(job_id)
        """
        return self._do_delete('jobs', job)

    def get_job_description(self, job):
        """Get the description of a job. 

        @params `job`: a batchcompute job.
        @type `job`: a 'job-' started {str} or a CreateResponse object.

        @example:
            >>> client = Client(region, id, key)
            ... job_id = 'job-xxxx' 
            ... job_desc = client.get_job_description(job_id)
            ... print (job_desc.Description) 
            ... print (job_desc.Priority) 
        """
        p = 'description'
        resource_id = self._get_id(job)
        res = self._sa.get('jobs', resource_id, [], p)

        resource_type = AppJobDescription if isinstance(res.read(), AppJobDescription) else JobDescription 

        return GetResponse(res, resource_type, self._h)
            
    def get_job(self, job):
        """Get the running status of a job. 

        @params `job`: a batchcompute job.
        @type `job`: a 'job-' started {str} or a CreateResponse object.

        @example:
            >>> client = Client(region, id, key)
            ... job_id = 'job-xxxx' 
            ... job_status = client.get_job(job_id)
            ... print (job_status.State)
            ... print (job_status.Id)
        """
        return self._do_get(Job, 'jobs', job)

    def change_job_priority(self, job, priority):
        """Change the priority of a given job.

        @Notice:
            Only stopped jobs' priority can be changed.

        @params `job`: a batchcompute job.
        @type `job`: a 'job-' started {str} or a CreateResponse object.

        @params `priority`: priority number.
        @type `priority`: a {int} between 0~999.

        @example:
            >>> client = Client(region, id, key)
            ... job_id = 'job-xxxx' 
            ... client.stop_job(job_id)
            ... assert client.get_job(job_id).State == 'Stopped'
            ... client.change_job_priority(job_id, 99)
            ... client.start_job(job_id)
            ... assert client.get_job_description(job_id).Priority == 99
        """
        if not isinstance(priority, int):
            raise TypeError('Priority must be type of int')

        b = {
            'Priority': priority
        }
        job_id = self._get_id(job)
        res = self._sa.put('jobs', job_id, body=json.dumps(b))
        return ActionResponse(res, self._h)

    def list_jobs(self, marker, max_item_count, state="", cluster_id="", project_id="", **filters):
        """A method to list jobs with paging enabled.

        @params `marker`: start point of this list action. 
        @type `marker`: a {str}, usually the content of `NextMarker` property
            of the latest list action response, empty {str} triggers another
            series of list actions.

        @params `max_item_count`: max item number returned by a single list 
            invocation.
        @type `max_item_count`: a {int} number between 1~100.

        @return: a {ListResponse} object. 

        @example:
            >>> client = Client(region, id, key)
            ... marker = ''
            ... max_item_count = 100
            ... jobs = client.list_jobs(marker, max_item_count)
            ... # NextMarker is used to indicate the start point of next list action.
            ... print jobs.NextMarker 
            ... for job in jobs.Items:
            ...     print (job.State)
        """
        p = {
            'Marker': marker,
            'MaxItemCount': str(max_item_count)
        }

        if state.strip() or ("State" in filters and filters["State"].strip()):
            state_filter = state.strip() or filters["State"]
            p["State"] = state_filter

        if cluster_id.strip() or ("ClusterId" in filters and filters["ClusterId"].strip()):
            cluster_id_filter = cluster_id.strip() or filters["ClusterId"]
            p["ClusterId"] = cluster_id_filter

        if project_id.strip() or ("ProjectId" in filters and filters["ProjectId"].strip()):
            project_id_filter = project_id.strip() or filters["ProjectId"]
            p["ProjectId"] = project_id_filter
            
        res = self._sa.get('jobs', params=p)
        return ListResponse(res, Job, self._h)

    def get_task(self, job, task_name):
        """Get running information of a task.

        @params `job`: a batchcompute job.
        @type `job`: a 'job-' started {str} or a CreateResponse object.

        @params `task_name`: task name.
        @type `task_name`: a {str}.

        @example:
            >>> client = Client(region, id, key)
            ... job_id = 'job-xxxx' 
            ... task_name = 'Map' 
            ... task_status = client.get_task(job_id, task_name)
            ... print (task_status.State)
        """
        task_info = ['tasks', task_name] 
        return self._do_get(Task, 'jobs', job, attrs=task_info)

    def list_tasks(self, job, marker, max_item_count, state="", cluster_id="", **filters):
        """List tasks of a specified job with paging enabled.

        @params `marker`: start point of this list action..
        @type `marker`: a {str}, usually the content of `NextMarker` property
            of the latest list action response, empty {str} triggers another
            series of list actions.

        @params `max_item_count`: max item number returned by a single list 
            invocation.
        @type `max_item_count`: a {int} number between 1~100. 

        @return: a {ListResponse} object. 

        @example:
            >>> client = Client(region, id, key)
            ... marker = ''
            ... max_item_count = 100
            ... job_id = 'job-xxxx' 
            ... tasks = client.list_tasks(job_id, marker, max_item_count)
            ... # NextMarker is used to indicate the start point of next list action.
            ... print (tasks.NextMarker)
            ... for task in tasks.Items:
            ...     print (task.TaskName, task.State)
        """
        job_info = [
            self._get_id(job),
            'tasks'
        ]

        p = {
            'Marker': marker,
            'MaxItemCount': str(max_item_count)
        }

        if state.strip() or ("State" in filters and filters["State"].strip()):
            state_filter = state.strip() or filters["State"]
            p["State"] = state_filter

        if cluster_id.strip() or ("ClusterId" in filters and filters["ClusterId"].strip()):
            cluster_id_filter = cluster_id.strip() or filters["ClusterId"]
            p["ClusterId"] = cluster_id_filter

        res = self._sa.get('jobs', attrs=job_info, params=p)
        return ListResponse(res, Task, self._h)

    def get_instance(self, job, task_name, instance_id):
        """Get instance running information of a task.

        @params `job`: a batchcompute job.
        @type `job`: a 'job-' started {str} or a CreateResponse object.

        @params `task_name`: task name.
        @type `task_name`: a {str}.

        @params `instance_id`: instance id.
        @type `instance_id`: a {int}.

        @example:
            >>> client = Client(region, id, key)
            ... job_id = 'job-xxxx' 
            ... task_name = 'Map' 
            ... instance_id = 1 
            ... instance_status = client.get_instance(job_id, task_name, instance_id)
            ... print (instance_status.State)
        """
        instance_info = [
            'tasks', 
            task_name, 
            'instances', 
            str(instance_id)
        ]
        return self._do_get(Instance, 'jobs', job, attrs=instance_info)

    def list_instances(self, job, task_name, marker, max_item_count, state="", **filters):
        """List instances of a task with paging enabled.

        @params `job`: a batchcompute job.
        @type `job`: a 'job-' started {str} or a CreateResponse object.

        @params `task_name`: task name.
        @type `task_name`: a {str}.

        @params `marker`: start point of this list action.
        @type `marker`: a {str}, usually the content of `NextMarker` property
            of the latest list action response, empty {str} triggers another
            series of list actions.

        @params `max_item_count`: max item number returned by a single list 
            invacation.
        @type `max_item_count`: a {int} number. 

        @return: a {ListResponse} object. 

        @example:
            >>> client = Client(region, id, key)
            ... marker = ''
            ... max_item_count = 100
            ... job_id = 'job-xxxx' 
            ... task_name = 'Map' 
            ... instances = client.list_instances(job_id, task_name, marker, max_item_count)
            ... # NextMarker is used to indicate the start point of next list action.
            ... print (instances.NextMarker)
            ... for instance in instances.Items:
            ...     print (instance.State)
        """
        task_info = [
            self._get_id(job),
            'tasks',
            task_name,
            'instances'
        ]

        p = {
            'Marker': str(marker),
            'MaxItemCount': str(max_item_count)
        }

        if state.strip() or ("State" in filters and filters["State"].strip()):
            state_filter = state.strip() or filters["State"]
            p["State"] = state_filter

        res = self._sa.get('jobs', attrs=task_info, params=p)
        return ListResponse(res, Instance, self._h)

    # Methods related to image.
    def create_image(self, image_desc, token=''):
        """Create a new image in server. 

        @params `image_desc`: a object descripts a image.
        @type `image_desc`: a json {str}, a {dict} object, or a 
            {ImageDescription} object.  

        @params `token`: idempotent token.
        @type `token`: a {str} specified by user.

        @return: a {CreateResponse} object.

        @example:

            >>> from batchcompute import Client, ClientError
            ... from batchcompute.resources import ImageDescription
            ... # some other codes here
            ... Client = Client(REGION, id, key)
            ... 
            ... try: 
            ...     image_desc = ImageDescription()

            ...     image_desc.Name = "PythonSDKImage"
            ...     image_desc.Description = "PythonSDKImage"
            ...     image_desc.EcsImageId = "m-xxxx"
            ...     image_desc.Platform = "Linux" # or Windows
            ...    
            ...     print client.create_image(image_desc).Id
            ... except ClientError, e:
            ...     print (e.get_status_code(), e.get_code(), e.get_requestid(), e.get_msg())

        """
        return self._do_create(ImageDescription, image_desc, idempotent_token=token)

    def delete_image(self, image):
        """Release a image. 

        @params `image`: a batchcompute image.
        @type `image`: a {str} or a CreateResponse object.

        @example:
            >>> client = Client(region, id, key)
            ... image_id = 'm-xxxx' 
            ... client.delete_image(image_id)
        """
        return self._do_delete('images', image)

    def get_image(self, image):
        """Get the running status of a image. 

        @params `image`: a batchcompute image.
        @type `image`: a {str} or a CreateResponse object.

        @example:
            >>> client = Client(region, id, key)
            ... image_id = 'm-xxxx' 
            ... image_status = client.get_image(image_id)
            ... print (image_status.Name)
            ... print (image_status.Id)
        """
        return self._do_get(Image, 'images', image)

    def list_images(self, marker, max_item_count, type_=""):
        """List images with paging enabled.

        @params `marker`: start point of this list action.
        @type `marker`: a {str}, usually the content of `NextMarker` property
            of the latest list action response, empty {str} triggers another
            series of list actions.

        @params `max_item_count`: max item number returned by a single list 
            invacation.
        @type `max_item_count`: a {int} number. 

        @params `type_`: image type to list.
        @type `type_`: a {str}.

        @return: a {ListResponse} object. 

        @example:
            >>> client = Client(region, id, key)
            ... marker = ''
            ... max_item_count = 100
            ... images = client.list_images(marker, max_item_count)
            ... # NextMarker is used to indicate the start point of next list action.
            ... print (images.NextMarker)
            ... for image in images.Items:
            ...     print (image.Name)
        """
        p = {
            'Marker': marker,
            'MaxItemCount': str(max_item_count)
        }
        if type_.strip() and type_.strip() == "System":
            p["Type"] = "System"

        res = self._sa.get('images', params=p)
        return ListResponse(res, Image, self._h)

    def create_cluster(self, cluster_desc, token=''):
        """Create a new cluster in server. 

        @params `cluster_desc`: a object descripts a cluster.
        @type `cluster_desc`: a json {str}, a {dict} object, or a 
            {ClusterDescription} object.  

        @params `token`: idempotent token.
        @type `token`: a {str} specified by user.

        @return: a {CreateResponse} object.

        @example:

            >>> from batchcompute import Client, ClientError
            ... from batchcompute.resources import ClusterDescription, GroupDescription 
            ... # some other codes here
            ... Client = Client(REGION, id, key)
            ... 
            ... try: 
            ...     cluster_desc = ClusterDescription()
            ...     group_desc = GroupDescription()

            ...     group_desc.DesiredVMCount = 1
            ...     group_desc.InstanceType = 'ecs.t1.small'
            ...     cluster_desc.add_group('group1', group_desc)
            ...     cluster_desc.Name = "BatchcomputePythonSDK" 
            ...     # image_id is a image created in batchcompute service before.
            ...     cluster_desc.ImageId = image_id
            ...    
            ...     print client.create_cluster(cluster_desc).Id
            ... except ClientError, e:
            ...     print (e.get_status_code(), e.get_code(), e.get_requestid(), e.get_msg())

        """
        return self._do_create(ClusterDescription, cluster_desc, idempotent_token=token)

    def modify_cluster(self, cluster, modify_cluster_desc):
        """Modify cluster properties.

        @params `cluster`: a batchcompute cluster.
        @type `cluster`: a 'cls-' started {str} or a CreateResponse object.

        @params `modify_cluster_desc`: description for properties needed modified for a cluster.
        @type `modify_cluster_desc`: a {ModifyClusterDescription} class or a relative json {str}.

        @example:
            >>> client = Client(region, id, key)
            ... cluster_id = "cls-xxxx"
            ...
            ... modify_body = ModifyClusterDescription()
            ...
            ... group_desc = ModifyGroupDescription()
            ... group_desc.DesiredVMCount = 0
            ... modify_body.add_group("group1", group_desc)
            ... 
            ... modify_body.UserData = {
                    "foo": "bar"
            ... }
            ... modify_body.EnvVars = {
                    "foo": "bar"
            ... }
            ...
            ... client.modify_cluster(cluster_id, modify_body)

        """

        cluster_id = self._get_id(cluster)
        desc = ModifyClusterDescription(modify_cluster_desc)
        # Validate parameters.
        # It will raise an exception if invalid parameters exist.
        desc.validate()

        res = self._sa.put('clusters', cluster_id, body=desc.dump())
        return ActionResponse(res, self._h)

    def change_cluster_desired_vm_count(self, cluster, **kwargs):
        """Change the desired vm count of a existing cluster. 

        @params `cluster`: a batchcompute cluster.
        @type `cluster`: a 'cls-' started {str} or a CreateResponse object.

        @params `kwargs`: some key-word pair like group_name=desired_vm_count.
        @type `kwargs`: desired_vm_count must be a positive {int} value;

        @example:
            >>> client = Client(region, id, key)
            ... cluster_id = client.create_cluster(... 
            ... client.change_cluster_desired_vm_count(cluster_id, group1=3, group2=4)
        """
        b = {'Groups': {}}
        for group_name, desired_vm_count in kwargs.items():
            if not isinstance(desired_vm_count, int):
                raise TypeError('VM count must be type of int')
            else:
                b["Groups"][group_name] = {"DesiredVMCount": desired_vm_count}

        cluster_id = self._get_id(cluster)
        res = self._sa.put('clusters', cluster_id, body=json.dumps(b))
        return ActionResponse(res, self._h)

    def change_cluster_user_data(self, cluster, data={}):
        """Change the user meta of a existing cluster.

        @params `cluster`: a batchcompute cluster.
        @type `cluster`: a 'cls-' started {str} or a CreateResponse object.

        @params `data`: a collect of user-defined key-value pairs.
        @params `data`: a `dict` object.
        """
        if not isinstance(data, dict):
            raise TypeError("""Invalid data type, must be a dict""")
        b = {'UserData': data}
        
        cluster_id = self._get_id(cluster)
        res = self._sa.put('clusters', cluster_id, body=json.dumps(b))
        return ActionResponse(res, self._h)

    def change_cluster_input_mapping(self, cluster, data={}):
        """Change the input mapping of a existing cluster.

        @params `cluster`: a batchcompute cluster.
        @type `cluster`: a 'cls-' started {str} or a CreateResponse object.

        @params `data`: a collect of user-defined key-value pairs.
        @params `data`: a `dict` object.
        """
        if not isinstance(data, dict):
            raise TypeError("""Invalid data type, must be a dict""")
        b = {'InputMapping': data}
        
        cluster_id = self._get_id(cluster)
        res = self._sa.put('clusters', cluster_id, body=json.dumps(b))
        return ActionResponse(res, self._h)

    def change_cluster_env_vars(self, cluster, data={}):
        """Change the environment of a existing cluster.

        @params `cluster`: a batchcompute cluster.
        @type `cluster`: a 'cls-' started {str} or a CreateResponse object.

        @params `data`: a collect of user-defined key-value pairs.
        @params `data`: a `dict` object.
        """
        if not isinstance(data, dict):
            raise TypeError("""Invalid data type, must be a dict""")
        b = {'EnvVars': data}
        
        cluster_id = self._get_id(cluster)
        res = self._sa.put('clusters', cluster_id, body=json.dumps(b))
        return ActionResponse(res, self._h)

    def delete_cluster(self, cluster):
        """Release a cluster from batchcompute service.

        @params `cluster`: cluster id info.
        @type `cluster`: a `cls-` started {str} or a {CreateResponse} object.

        @example:
            >>> client = Client(region, id, key)
            ... cluster_id = 'cls-xxxx' 
            ... client.delete_cluster(job_id)
        """
        return self._do_delete('clusters', cluster)

    def get_cluster(self, cluster):
        """Get the running status of a cluster. 

        @params `cluster`: cluster id info.
        @type `cluster`: a `cls-` started {str} or a {CreateResponse} object.

        @example:
            >>> client = Client(region, id, key)
            ... cluster_id = 'cls-xxxx' 
            ... cluster_status = client.get_cluster(cluster_id)
            ... print (cluster_status.State)

        """
        return self._do_get(Cluster, 'clusters', cluster)

    def list_clusters(self, marker, max_item_count):
        """List clusters with paging enabled.

        @params `marker`: start point of this list action.
        @type `marker`: a {str}, usually the content of `NextMarker` property
            of the latest list action response, empty {str} triggers another
            series of list actions.

        @params `max_item_count`: max item number returned by a single list 
            invacation.
        @type `max_item_count`: a {int} number. 

        @return: a {ListResponse} object. 

        @example:
            >>> client = Client(region, id, key)
            ... marker = ''
            ... max_item_count = 100
            ... clusters = client.list_clusters(marker, max_item_count)
            ... # NextMarker is used to indicate the start point of next list action.
            ... print clusters.NextMarker 
            ... for cluster in clusters.Items:
            ...     print (cluster.Name)
        """
        p = {
            'Marker': marker,
            'MaxItemCount': str(max_item_count)
        }
        res = self._sa.get('clusters', params=p)
        return ListResponse(res, Cluster, self._h)

    def get_cluster_instance(self, cluster_id, group_name, instance_id):
        """Get running information a instance in cluster.

        @params `cluster_id`: a batchcompute cluster.
        @type `cluster_id`: a 'cls-' started {str} or a CreateResponse object.

        @params `group_name`: group name.
        @type `group_name`: a {str}.

        @params `instance_id`: id of a instance.
        @type `instance_id`: a {str}.

        @example:
            >>> client = Client(region, id, key)
            ... cluster_id = 'cls-xxxx' 
            ... group_name = 'group1' 
            ... instance_id = 'i-xxxxxx' 
            ... instance_status = client.get_cluster_instance(cluster_id, group_name, instance_id)
            ... print (instance_status.InstanceState)
        """
        instance_info = ['groups', group_name, 'instances', instance_id] 
        return self._do_get(ClusterInstance, 'clusters', cluster_id, attrs=instance_info)

    def recreate_cluster_instance(self, cluster_id, group_name, instance_id):
        """Recreate a existing instance in cluster.

        @params `cluster_id`: a batchcompute cluster.
        @type `cluster_id`: a 'cls-' started {str} or a CreateResponse object.

        @params `group_name`: group name.
        @type `group_name`: a {str}.

        @params `instance_id`: id of a instance.
        @type `instance_id`: a {str}.

        @example:
            >>> client = Client(region, id, key)
            ... cluster_id = 'cls-xxxx' 
            ... group_name = 'group1' 
            ... instance_id = 'i-xxxxxx' 
            ... client.recreate_cluster_instance(cluster_id, group_name, instance_id)
        """
        instance_info = ['groups', group_name, 'instances', instance_id, 'recreate'] 
        res = self._sa.post('clusters', cluster_id, attrs=instance_info)
        return ActionResponse(res, self._h)

    def delete_cluster_instance(self, cluster_id, group_name, instance_id):
        """Recreate a existing instance in cluster.

        @params `cluster_id`: a batchcompute cluster.
        @type `cluster_id`: a 'cls-' started {str} or a CreateResponse object.

        @params `group_name`: group name.
        @type `group_name`: a {str}.

        @params `instance_id`: id of a instance.
        @type `instance_id`: a {str}.

        @example:
            >>> client = Client(region, id, key)
            ... cluster_id = 'cls-xxxx' 
            ... group_name = 'group1' 
            ... instance_id = 'i-xxxxxx' 
            ... client.delete_cluster_instance(cluster_id, group_name, instance_id)
        """
        instance_info = ['groups', group_name, 'instances', instance_id] 
        res = self._sa.delete('clusters', cluster_id, attrs=instance_info)
        return ActionResponse(res, self._h)

    def list_cluster_instances(self, cluster_id, group_name, marker, max_item_count):
        """List cluster instances in a specified group.

        @params `cluster_id`: a batchcompute cluster.
        @type `cluster_id`: a 'cls-' started {str} or a CreateResponse object.

        @params `group_name`: group name.
        @type `group_name`: a {str}.

        @params `marker`: start point of this list action.
        @type `marker`: a {str}, usually the content of `NextMarker` property
            of the latest list action response, empty {str} triggers another
            series of list actions.

        @params `max_item_count`: max item number returned by a single list 
            invacation.
        @type `max_item_count`: a {int} number. 

        @return: a {ListResponse} object. 

        @example:
            >>> client = Client(region, id, key)
            ... cluster_id = 'cls-xxxx' 
            ... group_name = 'group1' 
            ...
            ... marker = ''
            ... max_item_count = 100
            ... cluster_instances = client.list_clusters_instances(cluster_id, group_name, marker, max_item_count)
            ... # NextMarker is used to indicate the start point of next list action.
            ... print cluster_instances.NextMarker 
            ... for instance in cluster_instances.Items:
            ...     print (instance.State)
        """
        cluster_info = [cluster_id, 'groups', group_name, 'instances'] 

        p = {
            'Marker': marker,
            'MaxItemCount': str(max_item_count)
        }

        res = self._sa.get('clusters', attrs=cluster_info, params=p)
        return ListResponse(res, ClusterInstance, self._h)

    def get_quotas(self):
        """Get user's quota.

        @return: a {GetResponse} object wrapped all Quota's method. 

        @example:
            >>> client = Client(region, id, key)
            ...
            ... quota = client.get_quotas()
            ... print (quota.AvailableClusterInstanceDataDiskType)
            ... print (quota.AvailableClusterInstanceSystemDiskType)
            ... print (quota.AvailableClusterInstanceType)
        """
        res = self._sa.get('quotas')
        return GetResponse(res, Quota, self._h)

    def easy_list(self, resource_type, *resource_info, **filters):
        """List all items with filters. 

        @param `resource_type`: the resource type.
        @type `resource_type`: a {str}, only ['jobs', 'clusters', 'images',
            'tasks', 'instances'] allowed now.

        @param `resource_info`: position arguments which needed to indicate 
            which job's or task's information is interested.

        @param `filters`: key-value arguments which needed to filter interested
            items from all other items of a given `resource_type`. 

        @return: A {list} of all items meet the requirements information given
             by `filters` parameter.

        @exmaples:
            >>> client = Client(region, id, key)
            ... for job in client.easy_list('jobs', Name='PythonSDK', Description='test list job') 
            ...     print (job.Name, job.Description)
            ...
            ... job_filters = {
            ...     'Name': 'PythonSDK',
            ...     'Description': 'test list job'
            ... }
            ... for job in client.easy_list('jobs', **job_filters):
            ...     print (job.Name, job.Description) 
            ...
            ... for job in client.easy_list('jobs', State=['Waiting', 'Running']):
            ...     print (job.Name, job.Description) 
            ...
            ... state_filter = lambda state: state in ['Waiting', 'Running']
            ... for job in client.easy_list('jobs', State=state_filter):
            ...     print (job.Name, job.Description) 
            ...
            ... job_id = 'job-xxx' 
            ... client.easy_list('tasks', job_id, State='Running')
            ...
            ... job_id = 'job-xxx' 
            ... task_name = 'Map'
            ... client.easy_list('instances', job_id, task_name, State='Running')

        """
        valid_type = [
            'jobs', 
            'clusters', 
            'images',
            'tasks',
            'instances',
        ]

        def filter_(item):
            ret = False
            for attr_name, expected in filters.items(): 

                # decide whether a attr has a desired value. 
                decide_it = lambda attr: attr == expected 
                if isinstance(expected, COLLECTION):
                    decide_it = lambda attr: attr in expected
                elif callable(expected):
                    decide_it = lambda attr: expected(attr)
                    
                if hasattr(item, attr_name):
                    attr = getattr(item, attr_name)
                    if decide_it(attr):
                        continue
                    else:
                        ret = False
                        break
                else:
                        ret = False
                        break
            else:
                ret = True
            return ret

        if resource_type not in valid_type:
            raise FieldError(resource_type)
        else:
            round = 1
            max_item_count = DEFAULT_LIST_ITEM
            next_marker = 0 if resource_type == 'instances' else ''
            internal_list = partial(getattr(self, 'list_' + resource_type), *resource_info)
            while next_marker or round == 1:
                round += 1 
                response = internal_list(next_marker, max_item_count)
                next_marker = response.NextMarker
                for item in response.Items:
                    if filter_(item):
                        yield item
                    else:
                        continue

    def poll(self, job_ids, timeout=86400, interval=3):
        """Wait for all jobs transist to 'Finished' state.

        @param `job_ids`: job ids for polling. 
        @type `job_ids`: a {str}, a {unicode}, a {list} or a {tuple}

        @param `timeout`: timeout value for polling. 
        @type verbose: {int}

        @return: A {list} of {str} indicating the errors when polling, for ex-
            ample: 'Failed' or 'Stopped' job occurs or timeout, you should ch-
            eck whether it is empty ensuring all jobs 'Terminated'.

        @example:
            >>> client = Client(region, id, key)
            ... job_ids = ['job-xxx', 'job-xxx', 'job-xxx']
            ... errs = client.poll(job_ids)
            ... if errs:
            ...     print ('Some jobs mustbe Failed or Stopped', errs) 
        """
        errs = [] 

        if isinstance(job_ids, (list, tuple)):
            jobs = job_ids
        elif isinstance(job_ids, STRING):
            jobs = [job_ids]
        else:
            errs.append('Invalid job ids: %s.'%job_ids)
            return errs

        def is_stable(state):
            return state in ('Finished', 'Failed', 'Stopped')
            
        # Record the start time.
        start = datetime.datetime.now() 
        total = datetime.timedelta(seconds=timeout)
        
        logger.info('Start waiting jobs terminated! JOBS:\n%s'%'\n'.join(jobs))
        
        finished = 0 
        while True:
            states = [state for state in map(lambda job: self.get_job(job).State, jobs)]
            # Record the current time.
            elapsed = datetime.datetime.now() - start
            if elapsed > total:
                # If timeout.
                errs.append('Timeout(%s).'%timeout)
                break
            elif 'Failed' in states or 'Stopped' in states:
                # If any fail or stop occurs!
                for index, job in enumerate(jobs):
                    if states[index] == 'Failed':
                        errs.append('Job %s failed.'%job)
                    if states[index] == 'Stopped':
                        errs.append('Job %s stopped.'%job)
                break
            elif 'Running' in states or 'Waiting' in states:
                # Still some are running or waiting!
                curr_finished = states.count('Finished')
                if curr_finished != finished:
                    logger.info('Current finished: %d, elapsed: %s'%(
                        curr_finished, elapsed))
                    finished = curr_finished
                time.sleep(interval)
                continue
            else:
                # All jobs terminated.
                logger.info('All jobs terminated.')
                break
        for job in jobs:
            # Try to stop all running and waiting jobs.
            if not is_stable(self.get_job(job).State):
                self.stop_job(job)
        return errs
# Add CamelCasedClass metaclass which will change all BatchComputeClient
# user-defined method name to lower-camel-cases. For example: you can invoke
# `listImages` instead of `list_images` method with a BatchComputeClient
# instance.
Client = add_metaclass(Client, CamelCasedClass)
