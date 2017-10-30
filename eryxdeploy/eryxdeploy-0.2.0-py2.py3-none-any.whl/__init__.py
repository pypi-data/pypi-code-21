from eryx_deploy.tasks.deploy_task import DeployTask
from eryx_deploy.tasks.first_deploy_task import FirstDeployTask

from .default_config import *
from .app_stacks import *
from .assets import *

deploy = DeployTask()
first_deploy = FirstDeployTask()
