from setuptools import setup
import distutils
import os
import shutil

setup(name='wfeng',
      description='Ammeon workflow engine',
      author='Ammeon',
      author_email='awe-support@ammeon.com, david.john.gee@ipengineer.net',
      version="0.1",
      long_description="The Ammeon Workflow Engine (AWE) uses a workflow, " \
                        "a file containing a series of tasks that are " \
                        "grouped into categories (or phases), to define " \
                        "and execute the steps needed to perform operations " \
                        "on the servers in a deployment. AWE is designed to " \
                        "simplify the complex steps involved in managing a " \
                        "solution (for example, performing upgrades or other " \
                        "maintenance tasks) across multiple servers.",

      license="Apache 2.0",
      packages=['wfeng'],
      scripts=['workfloweng.py'],
      install_requires=['fabric','paramiko','lxml','argparse','pycrypto','ecdsa'],
      keywords="workflow engine orchestration",
      data_files=[("cfg",['cfg/wfeng.cfg']),
                  ("cfg",['cfg/wfeng.ini']),
                  ("xsd",['xsd/workflow.xsd']),
                  ("xsd",['xsd/hosts.xsd']),
                  ("bin/wfeng",['install_common_functions.lib','solaris_def.lib','generic_def.lib','setup.py','RELEASE_INFO.txt']),
                  ("",['RELEASE_INFO.txt']),
                  ("license",['license/LICENSE.txt']),
                  ("license",['license/NOTICE.txt']),
                  (".lock",['.empty']),
                  ("etc",['.empty']),
                  ("log",['.empty'])]
     )
