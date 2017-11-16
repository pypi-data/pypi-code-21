"""
Tiros Visualization Flask App
"""
import os
import sys
import random
import json
from time import sleep
from flask import Flask, render_template, request, jsonify, Response
from flask import redirect, url_for, session, escape


from tiros.tiros_viz.process_viz import TirosVizProc
from tiros.tiros_viz import utils
from tiros.tiros_viz import render_error
from tiros import server
from tiros import util as cli_util


TIROS_CONFIG = {'host': 'localhost:9000',
                'ssl': False}

app = Flask(__name__)
app.secret_key = os.urandom(24)
viz = TirosVizProc(False)


# Render main view
@app.route('/')
def index():
    return render_template('index.html')


# Route to take a snapshot
@app.route('/mk_snapshot', methods=['POST'])
def mk_snaphot():
    app.logger.info('Snapping AWS Network.')
    viz = TirosVizProc(False)
    code, snap_data = viz.take_a_snap(TIROS_CONFIG)
    if code != 200:
        app.logger.error("Return Code: %s", code)
        return render_error.snap_error(code, snap_data)
    snap_name = 'aws_tiros_snap'
    snap_dir, snap_path = utils.save_snap(snap_data, snap_name, app)
    app.logger.info('Snap Dir Name: %s', snap_dir)
    if not snap_dir:
        app.logger.error("Storing Snapped file")
        return render_error.error("Problem storing snapshot file")
    viz_path = viz.run(snap_path, snap_dir)
    if not viz_path:
        return render_error.error("Invalid Tiros Snapshot")
    rel = os.path.relpath(viz_path)
    relative_viz_path = rel.split('tiros_viz/')[1]
    set_session(snap_path, snap_dir, relative_viz_path)
    policy = get_policy()
    if not policy:
        return render_error.error("Dashboard policy not found")
    return render_template('dashboard.html',
                           policy=policy,
                           enumerate=enumerate,
                           snapshot_file=relative_viz_path)


# Route to render a refresh of the snapshot
@app.route('/refresh')
def refresh():
    current_session = get_session()
    # if there is no session data go back to index
    if not current_session['snap_file']:
        return redirect(url_for('index'))
    policy = get_policy()
    if not policy:
        return render_error.error("Dashboard policy not found")
    return render_template('dashboard.html',
                           policy=policy,
                           enumerate=enumerate,
                           snapshot_file=current_session['rel_path'])


# Route to render the uploaded snapshot
@app.route('/snapshot', methods=['POST'])
def snapshot():
    viz = TirosVizProc(False)
    app.logger.info('Render Snapshot View')
    input_file = request.files.get("file")
    file_ok = utils.check_input_file(input_file, app, 'json')
    if not file_ok:
        return render_error.error("Wrong file format")
    snap_dir, snap_path = utils.save_upload_file(input_file, app)
    viz_path = viz.run(snap_path, snap_dir)
    if not viz_path:
        return render_error.error("Invalid Tiros Snapshot")
    rel = os.path.relpath(viz_path)
    relative_viz_path = rel.split('tiros_viz/')[1]
    set_session(snap_path, snap_dir, relative_viz_path)
    policy = get_policy()
    if not policy:
        return render_error.error("Dashboard policy not found")
    return render_template('dashboard.html',
                           policy=policy,
                           enumerate=enumerate,
                           snapshot_file=relative_viz_path)


# route to make policy (general) queries
@app.route('/policy_query', methods=['POST'])
def policy_query():
    resp = Response("")
    resp.headers['Content-Type'] = 'application/json'
    app.logger.info('Policy Query')
    query_data = utils.get_queries(request)
    results = list()
    current_session = get_session()
    snap_file = current_session['snap_file']
    if not snap_file:
        return redirect(url_for('index'))
    for query in query_data["queries"]:
        print('Query: {}'.format(query))
        res = get_results(snap_file, query)
        if res is None:
            err = render_error.async_error("Contacting Tiros Service")
            return jsonify(err)
        res = res[0].get('result')
        print('Result: {}'.format(res))
        results.append(res)
    return jsonify({'results': results,
                    'messages': query_data["messages"],
                    'colors': query_data["colors"]})


# route to make inline queries
@app.route('/inline_query', methods=['POST'])
def inline_query():
    resp = Response("")
    resp.headers['Content-Type'] = 'application/json'
    query = request.form['inlinequery']
    print('Query: {}'.format(query))
    current_session = get_session()
    snap_file = current_session['snap_file']
    if not snap_file:
        return redirect(url_for('index'))
    results = get_results(snap_file, query)
    if results is None:
        err = render_error.async_error("Contacting Tiros Service")
        return jsonify(err)
    result = [r.get('result') for r in results]
    messages = [r.get('label') for r in results]
    colors = [r.get('color') for r in results]
    return jsonify({'results': result,
                    'messages': messages,
                    'colors': colors})


def get_results(snap_file, query):
    """
    Get results for a single query
    """
    code, response = viz.tiros_proc(TIROS_CONFIG, snap_file, query)
    try:
        query_dict = json.loads(response)
        just_results = query_dict if code !=200 else query_dict.get('results', {})
        results = viz.mk_solutions(just_results, snap_file)
        return results
    except ValueError:
        return None


@app.after_request
def add_header(r):
    """
    Add headers to render in different browsers
    also no caching
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


def set_session(snap_file, snap_dir, relative_path):
    """
    Set session data
    """
    session['snap_file'] = snap_file
    session['snap_dir'] = snap_dir
    session['current_viz_data'] = relative_path
    return


def get_session():
    return {'snap_file': session.get('snap_file'),
            'current_view': session.get('current_view'),
            'rel_path': session.get('current_viz_data'),
            'snap_dir': session.get('snap_dir'),
            'main_vsi_view': session.get('main_vsi_view')}


def get_policy():
    c_dir = os.path.dirname(os.path.realpath(__file__))
    dashboard = os.path.join(c_dir, 'static', 'dashboard.json')
    policy = None
    with open(dashboard, 'r') as f:
        policy = json.load(f)
    return policy


def wrap_args(args, snap_sessions, throttle):
    cli_session = cli_util.new_session(profile_name=args.profile,
                                       region_name=args.region)
    if args.region:
        cli_session = cli_util.change_session_region(cli_session, args.region)
    ssl = not args.no_ssl
    host = args.host or (server.DEV_HOST if args.dev else server.PROD_HOST)
    if not snap_sessions:
        snap_sessions = [cli_session]
    return {'profile': args.profile,
            'host': host,
            'ssl': ssl,
            'session': cli_session,
            'paranoid': args.paranoid,
            'snapshot_sessions': snap_sessions,
            'throttle': throttle,
            'uic': args.unsafe_ignore_classic}


def main(args, snap_sessions, throttle):
    global TIROS_CONFIG
    TIROS_CONFIG = wrap_args(args, snap_sessions, throttle)
    app.run(
        host="0.0.0.0",
        port=args.viz_port,
        debug=False
    )
