import os
import glob
import pprint
import json
import random
from flask import Markup
from tiros.tiros_viz.snapshot_data import SData
from tiros.tiros_viz.d3_data import D3Data
from tiros.tiros_viz.query_data import QData
from tiros import server as tiros_server
from tiros import util as tiros_util


class TirosVizProc(object):
    """
    Tiros Snapshot Viz Processor
    """

    def __init__(self, debug):
        self.snapshot_name = None
        self.snapshot_dir = None
        self.debug = debug
        self.sData = SData(debug)
        self.d3Data = D3Data(debug)
        return

    def mk_snap_dir(self, snap_dir):
        """
        For a given snapshot create a directory to store viz_data
        """
        self.snapshot_dir = os.path.join(snap_dir, 'viz_data')
        if not os.path.exists(self.snapshot_dir):
            os.makedirs(self.snapshot_dir)
        return

    def run(self, snap_file, snap_dir):
        """
        Main run.
        snap_file : Tiros snapshot file
        snap_dir : dir where output will be stored
        config: tiros config
        """
        try:
            print('Processing: {}'.format(snap_file))
            self.snapshot_name = os.path.basename(snap_file).split('.')[0]
            self.mk_snap_dir(snap_dir)
            proc_data = self.sData.process_snapshot(snap_file)
            vsi_data = self.d3Data.mk_vsi(proc_data)
            vsi_path = self.mk_path(vsi_data, 'main')
            return vsi_path
        except Exception as e:
            print("Error: {}".format(e))
            return None

    def mk_path(self, data, name):
        """
        Create a file for data viz
        """
        viz_filename = "_".join([name, self.snapshot_name, ".json"])
        viz_filepath = os.path.join(self.snapshot_dir, viz_filename)
        with open(viz_filepath, 'w') as fp:
            json.dump(data, fp)
        print('{} View : {}'.format(name, viz_filepath))
        return viz_filepath

    def tiros_proc(self, config, snap_file, query):
        """
        Tiros Service Proc
        """
        snap_contents = [json.loads(tiros_util.file_contents(snap_file))]
        response = tiros_server.query(
            config['session'],
            query,
            backend="souffle-compiler",
            host=config['host'],
            raw_snapshots=None,
            snapshot_sessions=None,
            snapshots=snap_contents,
            source='viz',
            ssl=config['ssl'],
            throttle=config['throttle'],
            transforms=['magic-sets'],
            unsafe_ignore_classic=config['uic'],
            user_relations=None)
        return response.status_code, response.text

    def take_a_snap(self, config):
        """
        Take a snapshot
        """
        response = tiros_server.snapshot(
            host=config['host'],
            raw_snapshots=[],
            paranoid=config['paranoid'],
            signing_session=config['session'],
            snapshot_sessions=config['snapshot_sessions'],
            snapshots=[],
            source='viz',
            ssl=config['ssl'],
            throttle=config['throttle'],
            unsafe_ignore_classic=config['uic']
        )
        return response.status_code, response.text

    def _mk_err_msg(self, error):
        msg = ""
        if "Invalid input" in error:
            msg = "Invalid input"
        elif "Authentication" in error:
            msg = "Authentication Failure. Check AWS credentials"
        else:
            msg = error
        return msg

    def mk_solutions(self, query_data, snap_file):
        """
        Parse query solutions
        """
        is_error = type(query_data) is dict
        results = list()
        colors = ["green", "red", "blue", "black", "yellow"]
        if is_error:
            error_data = query_data.get('error')
            err = error_data.get('message', 'Tiros Service Error')
            err_msg = self._mk_err_msg(err)
            html_msg = "<font color=\"red\">%s</font>" % err_msg
            out = Markup(html_msg)
            return [{"result": out, 'label': 'Tiros result'}]
        for res in query_data:
            body = res.get('body', {})
            label = res.get('label', 'Tiros Result')
            out = list()
            try:
                solutions = body.get('substitutions')
                q_data = QData()
                out = q_data.proc_query_data(solutions, snap_file)
            except AttributeError:
                out = body
            label = 'Tiros Result (No Label)' if label is None else label
            color = random.choice(colors)
            results.append({'result': out, 'label': label, 'color': color})
        return results
