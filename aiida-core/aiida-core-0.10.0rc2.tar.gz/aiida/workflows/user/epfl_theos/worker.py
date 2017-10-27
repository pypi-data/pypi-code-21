# -*- coding: utf-8 -*-
from aiida.orm.workflow import Workflow
from aiida.orm.node import Node
from aiida.orm import load_workflow
from aiida.common.utils import classproperty

try:
    from aiida.backends.djsite.db import models
except ImportError:
    from aiida.djsite.db import models
from django.db.models import Q

__copyright__ = u"Copyright (c), This file is part of the AiiDA-EPFL Pro platform. For further information please visit http://www.aiida.net/. All rights reserved"
__license__ = "Non-Commercial, End-User Software License Agreement, see LICENSE.txt file."
__version__ = "0.1.0"
__authors__ = "Nicolas Mounet, Giovanni Pizzi."

class Worker(object):
    """
    General class for workers. They are handling automatically the start of
    a given kind of workflow for a group of nodes. Typically, a small number  
    (~ten) of workers should be launched periodically thanks to e.g. a cron script. 
    """

    # Below we define the strings to be put in the extras used to identify,
    # for a given node, resp. the worker id, its status (running or not), 
    # a boolean to say if it should be run by a worker of this class, and
    # the pk of the workflow associated to it.
    
    @classproperty
    def extra_key_id(cls):
        """
        Key of the extra containing the worker id.
        """
        return "{}_id".format(cls.__name__)
    
    @classproperty
    def extra_key_is_running(cls):
        """
        Key of the extra containing the boolean that
        indicates if the workflow is running.
        """
        return "{}_is_running".format(cls.__name__)

    @classproperty
    def extra_key_to_run(cls):
        """
        Key of the extra containing the boolean that
        indicates if the worker is to be run.
        """
        return "{}_to_run".format(cls.__name__)
    
    @classproperty
    def extra_key_wf_pk(cls):
        """
        Key of the extra containing the workflow pk.
        """
        return "{}_wf_pk".format(cls.__name__)
 
    def __init__(self, worker_id=None, nodes=[], **kwargs):
        """
        Create a new worker.
        
        :param id: string to identify UNIQUELY the worker.
        :param nodes: AiiDA nodes on which the worker will act. Should be an 
            iterable (e.g. g.nodes where g is a group, or the result of a 
            Node.query(...), or a list of nodes).
        :param kwargs: other parameters that are set as attributes
            of the worker
        """
        self.id = worker_id
        self._nodes = list(nodes)   
        for k,v in kwargs.iteritems():
            setattr(self,k,v)

    def generate_workflow(self, node):
        """
        Generate the workflow to be launched by the worker. This method should
        be defined in the worker subclass.
        
        :param node: the AiiDA node on which the workflow will act.
        
        .. note:: This function SHOULD NOT create new nodes without using proper
            inline calculations or the like. Otherwise, provenance will be broken.
        """
        raise NotImplementedError

    def get_running_node(self):
        """
        Get the node currently running with this worker (meaning, for
        which the workflow associated with the worker is running).
        
        :return: the node, or None if no node is currently running.
        :raise ValueError: if there is more than one node running with this
            worker.
        
        .. note:: There should always be at maximum one node running with a 
            given worker.
        """      
        q_id = models.DbExtra.objects.filter(key=self.extra_key_id,
                                             tval=self.id)
        q_is_running = models.DbExtra.objects.filter(key=self.extra_key_is_running,
                                                     bval=True)
        q = Node.query(pk__in=self._nodes, dbextras__in=q_id).filter(
                    dbextras__in=q_is_running).distinct()
        
        if q.count() > 1:
            raise ValueError("More than one node running with worker {}"
                             "".format(self.id))
        
        return q.first() if q else None
    
    def check_and_update_worker(self):
        """
        Check and update the node extras associated with the worker, i.e.:
        * if the workflow is still running, simply return its state and do nothing
        * if the workflow is in FINISHED or ERROR state, switch the 'is_running'
            extra to False, switch the dependent worker 'to_run' extra to True
            (optional) and launch the function 'append_actions_after_completion'
        
        :return: the node pk and the workflow state, or (None,None) if no node
            is running with this worker.
        """
        from aiida.common.datastructures import wf_states
        
        n = self.get_running_node()
        if n is None:
            return None, None
        
        wf_state = load_workflow(n.get_extra(self.extra_key_wf_pk)).get_state()
        
        if wf_state in [wf_states.FINISHED,wf_states.ERROR]:
            self.append_actions_after_completion()
            n.del_extra(self.extra_key_is_running)
            n.set_extra(self.extra_key_is_running, False, exclusive=True)
            
        return n.pk, wf_state
    
    def append_actions_after_completion(self):
        """
        Actions to be launched after completion of a workflow. To be redefined
        (if needed) in each specific subclass.
        Typical actions:
        * put the resulting node(s) in a group,
        * set another worker 'to_run' extra, on the resulting node(s).
        """
        pass
    
    @classmethod
    def get_nodes_still_to_run(cls, nodes):
        """
        Get all the nodes still to be run, i.e. not yet associated with a worker
        of the same class nor running, and that are set as 'to_run'.
        :param nodes: an iterable with AiiDA nodes.
        
        :return: a query set with the nodes still to be run
        """
        q_to_run = models.DbExtra.objects.filter(key=cls.extra_key_to_run,
                                                 bval=True)
        q_is_running = models.DbExtra.objects.filter(key=cls.extra_key_is_running,
                                                     bval=True)
        q_is_taken_care = models.DbExtra.objects.filter(key=cls.extra_key_id)
        # select nodes that are set as 'to_run' and that are NOT running NOR 
        # were taken care already by a worker of the same class, but that are 
        # set as 'to_run'
        return Node.query(pk__in=nodes, dbextras__in=q_to_run).filter(
                        ~Q(dbextras__in=q_is_running)).filter(
                        ~Q(dbextras__in=q_is_taken_care)).distinct()
        
    def set_running_node(self, node):
        """
        Set a node running, building and launching the associated 
        workflow and taking care of all worker extras, i.e.:
        * switching the 'is_running' worker extra to True,
        * putting the workflow pk in the 'wf_pk' extra.
        :param node: an AiiDA node
        """
        from aiida.common.exceptions import UniquenessError
        
        if self.get_running_node():
            raise UniquenessError("Worker is already associated with a node")
        
        try:
            node.set_extra(self.extra_key_id, self.id, exclusive=True)
        except UniquenessError:
            raise UniquenessError("Node {} is already associated with a worker"
                                  "".format(node.pk))
        try:
            node.del_extra(self.extra_key_is_running)
        except AttributeError:
            pass
        node.set_extra(self.extra_key_is_running, True, exclusive=True)
   
        wf = self.generate_workflow(node)
        wf.store()
        try:
            node.del_extra(self.extra_key_wf_pk)
        except AttributeError:
            pass
        node.set_extra(self.extra_key_wf_pk, wf.pk, exclusive=True)
        
        wf.start()
        return wf.pk
    
    def run(self):
        """
        Run all the actions a worker should do periodically, i.e.:
        * check and update the finished node, if any,
        * get the nodes still to be run,
        * if no node is currently running, pick one of them and set it to run
        (launching the appropriate workflow).
        """
        node_pk, wf_state = self.check_and_update_worker()
        print "Node taken care of:", node_pk, ", workflow state", wf_state
        
        if not self.get_running_node():
            #q_nodes_to_run = list(self.get_nodes_still_to_run(self._nodes))
            # Note: I added the 'list' in front to 'fix' the returned query,
            # otherwise it might change before I use it
            #print "Number of nodes still to be run:", len(q_nodes_to_run)
            node_to_run = self.get_nodes_still_to_run(self._nodes).first()
            if node_to_run:
                wf_pk = self.set_running_node(node_to_run)
                print "Launched workflow", wf_pk, "for node", node_to_run.pk
                
        return
    
    @classmethod
    def query_nodes(cls, nodes = None, is_running=None, id=None, to_run=None,
                     has_run=None, wf_state=None, wf_pks=None, **kwargs):
        """
        Method to query the nodes that have particular worker-related
        extras.
        :param nodes: iterable of nodes to query on. If None,
            the query is on all possible nodes.
        :param is_running: query nodes that have the 'is_running' extra for
            this worker class, set to this value.
        :param id: query nodes that associated with a given worker id.
        :param to_run: query nodes that have the 'to_run' extra for
            this worker class, set to this value.
        :param has_run: query nodes that either has already run or is currently
            running (if True), or has not run yet at all (if False).
        :param wf_state: query nodes for which the workflow associated with this
            worker class, has this state (e.g. FINISHED, ERROR, etc.).
        :param wf_pks: query nodes for which the workflow associated with this
            worker class, has a pk in this list.
        
        .. note:: One can pass both the wf_state and wf_pks options
        .. note:: If None is passed to any of the above argument, the related
            query filter is ignored.
        
        :param kwargs: additional parameters to be passed to Node.query(...)
            to select the initial nodes we want to query on.
        
        :return: an Aiida query set of nodes.
        """
        q_extras = []
        if is_running is not None:
            q_extras.append(models.DbExtra.objects.filter(key=cls.extra_key_is_running,
                                                          bval=is_running))
        if to_run is not None:
            q_extras.append(models.DbExtra.objects.filter(key=cls.extra_key_to_run,
                                                          bval=to_run))
        if id is not None:
            q_extras.append(models.DbExtra.objects.filter(key=cls.extra_key_id,
                                                          tval=id))
        if has_run:
            q_extras.append(models.DbExtra.objects.filter(key=cls.extra_key_id))
                
        if nodes is not None:
            kwargs['pk__in'] = nodes
        
        q = Node.query(**kwargs)
        for q_extra in q_extras:
            q = q.filter(dbextras__in=q_extra)
        
        if has_run==False:
            q = q.filter(~Q(dbextras__in=models.DbExtra.objects.filter(
                                                    key=cls.extra_key_id)))
            
        if wf_state is not None:
            if wf_pks is None:
                wf_pks = list(models.DbExtra.objects.filter(dbnode__in=q,
                                            key=cls.extra_key_wf_pk
                                            ).values_list('ival',flat=True))
            wf_pks = Workflow.query(pk__in=wf_pks, state=wf_state
                                                ).values_list('pk',flat=True)
        
        if wf_pks is not None:    
            q = q.filter(dbextras__in=models.DbExtra.objects.filter(
                            key=cls.extra_key_wf_pk, ival__in=wf_pks))
        
        return q.distinct()
        
    @classmethod
    def get_extras(cls, nodes, keys = ['is_running','to_run','wf_pk']):
        """
        Get the worker related extras for all the nodes.
        :param nodes: an iterable with nodes
        :param keys : a list of strings that can be either 'is_running', 'to_run', 
            'wf_pk' or 'id', which indicate the kinds of extra extracted
            
        :return: a dictionary of the form
            {node.pk, {extra1_key: extra1_value, extra2_key: extra2_value, ...}}
        """
        key_dict = {'is_running': cls.extra_key_is_running,
                    'to_run': cls.extra_key_to_run,
                    'id': cls.extra_key_id,
                    'wf_pk': cls.extra_key_wf_pk,
                    }
        
        value_type_dict = {'is_running': 'bval',
                           'to_run': 'bval',
                           'id': 'tval',
                           'wf_pk': 'ival',
                           }
        
        # The line below 'fixes' the nodes list. Otherwise, when it's a query set
        # or an iterable from a Group, it would get empty after the first 
        # iteration on keys.
        node_list = list(nodes)
        result_dict = {}
        for key in keys:
            extras = models.DbExtra.objects.filter(dbnode__in=node_list,
                                          key=key_dict[key]).distinct().values_list(
                                                    'dbnode_id',value_type_dict[key])
            the_dict = dict([ ( pk,dict([(key,value)]) ) for pk,value in extras])
            for k,v in the_dict.iteritems():
                if k in result_dict:
                    result_dict[k].update(v)
                else:
                    result_dict[k] = v
        
        return result_dict

    @classmethod
    def query_workflows(cls, nodes=None, **kwargs):
        """
        Query the workflows associated to the nodes obtained from 
        query_nodes(nodes,**kwargs).
        :param nodes: an iterable with nodes. If None, we query wfs
            launched by this worker class, from all possible nodes
        :param kwargs: additional parameters to be passed to the query_nodes
            method to further select the nodes.
            
        :return: a query set with the corresponding workflows
        """
        the_nodes = nodes
        if kwargs:
            the_nodes = cls.query_nodes(nodes = nodes,**kwargs)
        
        wf_pks = models.DbExtra.objects.filter(dbnode__in=the_nodes,
                key=cls.extra_key_wf_pk).values_list('ival')
                                                        
        return Workflow.query(pk__in=wf_pks)

    @classmethod
    def get_workflow_states(cls, nodes):
        """
        Get the workflow states for all the nodes.
        :param nodes: an iterable with nodes
            
        :return: a dictionary of the form
            {node.pk, {wf_pk: wf_state}}
        """

        node_wf_pks = dict(models.DbExtra.objects.filter(dbnode__in=nodes,
                key=cls.extra_key_wf_pk).values_list('dbnode__pk','ival'))
        
        wf_pks_states = dict(Workflow.query(pk__in=node_wf_pks.values()
                                        ).values_list('pk','state'))
        
        result_dict = dict([ ( node_pk,dict([(wf_pk,wf_pks_states[wf_pk])]) )
                             for node_pk,wf_pk in node_wf_pks.iteritems()])
                                                
        return result_dict
   
    @classmethod
    def reset_nodes(cls, nodes):
        """
        Reset all worker extras of this class except the 'to_run' one.
        :param nodes: an iterable with the nodes to reset.
        """
        for n in nodes:
            try:
                n.del_extra(cls.extra_key_is_running)
                n.del_extra(cls.extra_key_id)
                n.del_extra(cls.extra_key_wf_pk)
            except AttributeError:
                pass

    @classmethod
    def set_nodes_to_run(cls, nodes, to_run = True):
        """
        Set all the nodes to be run, or not to be run, by workers of this class.
        :param nodes: an iterable with the nodes to set to run.
        :param to_run: boolean (True to set them to run, False otherwise)
        """
        for n in nodes:
            try:
                n.del_extra(cls.extra_key_to_run)
            except AttributeError:
                pass
            n.set_extra(cls.extra_key_to_run, to_run, exclusive=True)
            
    @classmethod
    def kill_workflows(cls, nodes):
        """
        Kill all the workflows associated with workers of this class and with
        nodes in 'nodes'.
        :param nodes: an iterable with the concerned nodes.
        """
        from aiida.orm.workflow import WorkflowUnkillable, WorkflowKillError
        
        for n in nodes:
            try:                
                load_workflow(n.get_extra(cls.extra_key_wf_pk)).kill()
            except AttributeError:
                pass
            except (WorkflowUnkillable, WorkflowKillError):
                pass
    
    @classmethod
    def create_workers(cls,num_workers):
        """
        Create 'num_workers' workers, in an AiiDA python script
        that can be launched from command line.
        :param num_wporkers: (int) number of workers to be created (each with
            a unique id)
        """
        from aiida.common.utils import get_new_uuid
        raise NotImplementedError
   
    
def create_bash_script(prefix='workers'):
    """
    Function to create a small bash script that executes the workers in a 
    directory (this bash script is then to be launched by e.g. cron).
    :param prefix: (str) prefix of the name the workers to be executed (i.e.
        all the workers of the form [prefix]*.py will be launched)
    """
    raise NotImplementedError
        
