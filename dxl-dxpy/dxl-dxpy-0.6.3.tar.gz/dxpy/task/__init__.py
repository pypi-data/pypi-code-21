"""
==================
Task system design
==================

Serivices
=========
TaskService:
    High level API.
    Dependency: 
        - StoreService (TaskJSON)        
    Output:
        TaskJSON

TaskServiceWeb:
    A RESTful API warper on TaskService.
    Dependency:
        - TaskService (TaskJSON)
    Output:
        TaskJSON

StoreService:
    Dependency:
        - DatabaseWebService (TaskJSON)
    Output:
        TaskPy, TaskJSON

RunService:
    Dependency:
        - TaskStoreService (TaskPy)
    Output:
        TaskPy
        
FactoryService:
    Dependency:
        - TaskStoreService (TaskPy)
    Output:
        TaskPy


Layers:



1:  RunService:
    Internal Representations:
        TaskPy, Task
0:  Database
    Interface representations:
        TaskJSON
    Internal Representations:
        TaskDB, TaskJSON
    Features:
        Managing Serilization of Tasks

    






Task Representations
====================
Overview:        
    All representations have full information.
Representations:
    TaskPy
        Python Object. Properties are objects ready to use
    TaskYAML
        Supports easy dump/load to TaskPython.
        Main serilization format of Tasks.
    TaskJSON
        JSON i/o. For simple communication only.
        Details are stored in filed 'body' as YAML.
    TaskDB
        Not really a representation, true resource of tasks. The only mutable representation.
Transform:
    TaskPy <=> TaskYAML
    TaskPy => TaskJSON    
    TaskJSON => TaskYAML
    TaskJSON <=> TaskDB


Overview
--------
There are four kinds of task objects in dxpy.task.
#. TaskDBModel
    Task resource
Task object is a *representation* of a logical task, which is designed to be:
#. 
#. 

Features
--------
#. self content
    A task object contains **ALL** information to perform a task with the help of task server.
#. subtask list
    A task may be consisted by multiple subtasks. There are two type of tasks, 
#. task state inspect
#. task serilization, database support (Optional)
    retrieve task from file, or database


Task server
-----------
#. Task factory
#. Task query
    #. on running
    #. history (recent)

#. List of tasks
#. Create(Load Tasks):
    #. create from scrach
    #. from file
        #. given path
        #. from database 




SLURM => Resource Unlimited
(Pending system)
OS, Hardware => Resource Limited
"""
from .api import *

