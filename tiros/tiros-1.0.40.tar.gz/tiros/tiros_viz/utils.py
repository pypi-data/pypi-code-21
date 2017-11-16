import os
import json
from datetime import datetime
from werkzeug import secure_filename


# For a given file, return whether it's an allowed type or not
def allowed_file(app, filename, typ):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in [typ]


def rm_dir(path):
    import shutil
    for root, dirs, _ in os.walk(path):
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    return


def mk_dir(root, name):
    timed_dir = datetime.now().isoformat()
    dir_name = name.split('.json')[0] + "_" + timed_dir
    data = os.path.join(root, 'static', 'data')
    rm_dir(data)
    dir_name = os.path.join(data, dir_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name


def check_input_file(input_file, app, typ):
    return input_file and allowed_file(app, input_file.filename, typ)


def save_upload_file(input_file, app):
    filename = secure_filename(input_file.filename)
    snap_dir = mk_dir(app.root_path, filename)
    snap_file = os.path.join(snap_dir, filename)
    input_file.save(snap_file)
    return snap_dir, snap_file


def save_snap(snap_data, snap_name, app):
    try:
        snap_dir = mk_dir(app.root_path, snap_name)
        snap_file = os.path.join(snap_dir, snap_name + ".json")
        js = json.loads(snap_data)
        js_results = js.get('results', {})
        with open(snap_file, 'w') as fp:
            json.dump(js_results, fp)
        return snap_dir, snap_file
    except ValueError:
        return None, None


def get_queries(request):
    uuid = request.form['instrument-uuid']
    queries, messages, colors = list(), list(), list()
    c_dir = os.path.dirname(os.path.realpath(__file__))
    dashboard = os.path.join(c_dir, 'static', 'dashboard.json')
    policy = None
    with open(dashboard, 'r') as f:
        policy = json.load(f)
    instrument = policy[int(uuid) - 1]
    queries_tag = instrument['Queries']
    for q in queries_tag:
        queries.append(q['QueryString'])
        colors.append(q['PulseColor'])
        messages.append(q['ResultHeader'])
    variables = request.form.keys()
    for variable in variables:
        var_request = request.form.get(variable)
        queries = _mk_entity(queries, variable, var_request)
        messages = _mk_entity(messages, variable, var_request)
    return {"colors": colors, "queries": queries, "messages": messages}


def _mk_entity(queries, variable, var_request):
    out = list()
    for query in queries:
        var = variable.split('-', 1)[0]
        q = (query.replace("${%s}" % var, var_request))
        out.append(q)
    return out
