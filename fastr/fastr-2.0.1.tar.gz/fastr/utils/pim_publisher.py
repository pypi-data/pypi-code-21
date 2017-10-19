import itertools
import json

import requests
import fastr

from fastr.execution.job import JobState
from fastr.execution.sinknoderun import SinkNodeRun
from fastr.execution.sourcenoderun import ConstantNodeRun, SourceNodeRun


class PimPublisher(object):
    """
    Class to publish to PIM
    """
    PIM_STATUS_MAPPING = {
        JobState.nonexistent: 'unknown',
        JobState.created: 'idle',
        JobState.queued: 'idle',
        JobState.hold: 'idle',
        JobState.running: 'running',
        JobState.execution_done: 'running',
        JobState.execution_failed: 'running',
        JobState.processing_callback: 'running',
        JobState.finished: 'success',
        JobState.failed: 'failed',
        JobState.cancelled: 'failed',
    }

    def __init__(self, uri=None):
        if uri is None and fastr.config.pim_host == '':
            fastr.log.info("No valid PIM host given, PIM publishing will be disabled!")
            self.pim_uri = None
        else:
            self.pim_uri = uri or fastr.config.pim_host
        self.registered = False
        self.run_id = None

        # Some data
        self.counter = itertools.count()
        self.scopes = {None: 'root'}
        self.nodes = {}

    def pim_update_status(self, network_run, job):
        if self.pim_uri is None:
            return

        if not self.registered:
            fastr.log.debug('Did not register a RUN with PIM yet! Cannot'
                            ' send status updates!')
            return

        node = network_run[job.node_global_id]

        # Create PIM job data
        pim_job_data = {
            "id": job.id,
            "node_id": self.nodes[node],
            "run_id": network_run.id,
            "sample_id": str(job.sample_id),
            "status": self.PIM_STATUS_MAPPING[job.status]
        }

        # Send the data to PIM
        fastr.log.debug('Updating PIM job status {} => {} ({})'.format(job.id,
                                                                       job.status,
                                                                       self.PIM_STATUS_MAPPING[job.status]))
        uri = '{pim}/api/runs/{run_id}/jobs/{job_id}'.format(pim=fastr.config.pim_host,
                                                             run_id=network_run.id,
                                                             job_id=job.id)

        fastr.log.debug('Send PUT to pim at {}:\n{}'.format(uri, pim_job_data))
        try:
            response = requests.put(uri, json=pim_job_data)
        except requests.ConnectionError as exception:
            fastr.log.error('Could no publish status to PIM, encountered exception: {}'.format(exception))

    def pim_serialize_network(self, network, scope=None, network_data=None):
        """
        Serialize Network in the correct for to use with PIM.

        :return: json data for PIM
        """
        node_classes = {
            'NodeRun': 'node',
            'SourceNodeRun': 'source',
            'ConstantNodeRun': 'constant',
            'SinkNodeRun': 'sink'
        }

        if network_data is None:
            network_data = {
                "description": network.description,
                "nodes": [],
                "links": [],
                "groups": [],
            }

        # Add the steps to the network
        for step in network.stepids.keys():
            group_id = '{}_{}'.format(next(self.counter), step)
            self.scopes['_'.join(x for x in [scope, step] if x)] = group_id

            group_data = {
                "id": group_id,
                "description": "undefined",
                "parent_group": self.scopes[scope]
            }

            network_data['groups'].append(group_data)

        # Add the nodes
        for node in network.nodelist.values():
            if type(node).__name__ == 'MacroNodeRun':
                # MacroNodes are a weird tool-less Node that will fail

                group_id = '{}_{}'.format(next(self.counter), node.id)
                new_scope = "{}_{}".format(scope, node.id) if scope else node.id
                self.scopes[new_scope] = group_id

                # Add a scope group for the new macro
                network_data['groups'].append(
                    {
                        "id": group_id,
                        "description": "undefined",
                        "parent_group": self.scopes[scope]
                    }
                )

                # Serialize the internal macro network
                self.pim_serialize_network(
                    node.network_run,
                    scope=new_scope,
                    network_data=network_data
                )
            else:
                node_class = node.__class__.__name__
                step = None
                for stepid, nodes in network.stepids.items():
                    if node in nodes:
                        step = stepid
                        break

                group_id = self.scopes['_'.join(x for x in [scope, step] if x) or None]
                node_id = "{}_{}".format(next(self.counter), node.id)
                self.nodes[node] = node_id

                node_data = {
                    "group_id": group_id,
                    "id": node_id,
                    "in_ports": [{'id': 'in_' + x.id, 'description': x.description} for x in node.tool.inputs.values()],
                    "out_ports": [{'id': 'out_' + x.id, 'description': x.description} for x in node.tool.outputs.values()],
                    "type": node_classes[node_class] if node_class in node_classes else 'node'
                }

                # Add special pass-through ports to source and sink if we are in a macro
                if scope and isinstance(node, SourceNodeRun) and not isinstance(node, ConstantNodeRun):
                    node_data['in_ports'].append({
                        "id": "in_source",
                        "description": "The feed of the source data to the internal macro network",
                    })

                if scope and isinstance(node, SinkNodeRun):
                    node_data['out_ports'].append({
                        "id": "out_sink",
                        "description": "The result sink data from the internal macro network to be transported back",
                    })

                network_data["nodes"].append(node_data)

        # Add the links
        for link in network.linklist.values():
            # If links go to/from macro network, set them to the source/sink inside instead
            if type(link.source.node).__name__ == 'MacroNodeRun':
                from_node = self.nodes[link.source.node.network_run.sinklist[link.source.id]]
                from_port = "out_sink"
            else:
                from_node = self.nodes[link.source.node]
                from_port = 'out_' + link.source.id

            if type(link.target.node).__name__ == 'MacroNodeRun':
                to_node = self.nodes[link.target.node.network_run.sourcelist[link.target.id]]
                to_port = 'in_source'
            else:
                to_node = self.nodes[link.target.node]
                to_port = 'in_' + link.target.id

            # Generate and save link data
            link_data = {
                "id": '{}_{}'.format(next(self.counter), link.id),
                "from_node": from_node,
                "from_port": from_port,
                "to_node": to_node,
                "to_port": to_port,
                "type": link.source.resulting_datatype.id
            }

            network_data["links"].append(link_data)

        return network_data

    def pim_register_run(self, network):
        if self.pim_uri is None:
            fastr.log.debug('No valid PIM uri known. Cannot register to PIM!')
            return

        self.run_id = network.id
        pim_run_data = {
            "collapse": False,
            "description": "Run of {} started at {}".format(network.id,
                                                            network.timestamp),
            "id": self.run_id,
            "network": self.pim_serialize_network(network),
            "workflow_engine": "fastr"
        }

        uri = '{pim}/api/runs/'.format(pim=fastr.config.pim_host)
        fastr.log.info('Registering {} with PIM at {}'.format(self.run_id, uri))

        fastr.log.debug('Send PUT to pim at {}:\n{}'.format(uri, json.dumps(pim_run_data, indent=2)))

        # Send out the response and record if we registered correctly
        try:
            response = requests.put(uri, json=pim_run_data)
            if response.status_code in [200, 201]:
                self.registered = True
        except requests.ConnectionError as exception:
            fastr.log.error('Could no register network to PIM, encountered'
                            ' exception: {}'.format(exception))
