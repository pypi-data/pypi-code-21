


from plotly.graph_objs import Scatter, Figure, Layout
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import re


def get_log_fp(filename):
    return open(filename, "r")

def get_data_from_file(fp):
    chunk_list = []
    actual_chunk = {}
    actual_chunk_list = None
    data_names = ["name", "user", "nice", "system", "iowait", "irq","softirq", "idle"]
    while True: #sorry
        line = fp.readline()
        if (line == ""): #dirty sorry
            break

        if (line[0] == "["): #timestamp and New Chunk
            if (actual_chunk_list):
                chunk_list.append(actual_chunk_list)
            actual_chunk_list = []
            line = re.sub("[^0-9.]","", line)
            time_stamp = float(line)
            print time_stamp
            actual_chunk["timestamp"] = time_stamp
        else:
            temp_chunk = {}
            temp_chunk["timestamp"] = actual_chunk["timestamp"]
            actual_chunk = temp_chunk
            for data_name in data_names:
                actual_chunk[data_name] = extract_from_line(data_name, line)
            actual_chunk_list.append(actual_chunk)

    if (actual_chunk_list):
        chunk_list.append(actual_chunk_list)
    return chunk_list




def build_x_values(chunk_list_list):
    x_values = []
    for values_for_a_timestamp in chunk_list_list:
        x_values.append(values_for_a_timestamp[0].get("timestamp"))
    return x_values


def build_value_list(chunk_list_list, data_name):
    result_list = []
    if (len(chunk_list_list) >= 1):
        nb_cpu = len(chunk_list_list[0])
        for i in range (0, nb_cpu):
            result_list.append([])

    for values_for_a_timestamp in chunk_list_list:
        result_list_number = 0
        for data_for_a_cpu in values_for_a_timestamp:
            result_list[result_list_number].append(data_for_a_cpu[data_name])
            result_list_number += 1

    return result_list


def extract_from_line(data_name, line):
    regexp = ":[ ][a-z]*[0-9]*"
    data_to_match = data_name + regexp
    matching_result = re.search(data_to_match, line)
    extracted = matching_result.group().replace(data_name + ": ", "")
    return extracted


def get_name_list(chunk_list_list):
    cpu_name_list = []
    if (len(chunk_list_list) > 1):
        element = chunk_list_list[0]
        if (len(element) >= 1):
            for cpu in element:
                cpu_name_list.append(cpu["name"])
    return cpu_name_list

def build_option(cpu_names):
    option_list =[]
    for name in cpu_names:
        actual_dict = {}
        actual_dict["label"] = name
        actual_dict["value"] = name
        option_list.append(actual_dict)
    return option_list


def draw_graph(logfilename):
    chunk_list_list = get_data_from_file(get_log_fp(logfilename))# chunk_list_list =[[{name: "bla"...}, {name: "blo"...}], [{name: "bla"...}, {name: "blo"...}]]
    cpu_name_list = get_name_list(chunk_list_list)
    dash_options = build_option(cpu_name_list)
    x_values = build_x_values(chunk_list_list)

    data_available = ["user", "nice", "system", "iowait", "irq","softirq"]#, "idle"]
    data_dict = {}
    for element in data_available:
        data_dict[element] = build_value_list(chunk_list_list,element)

    nb_cpu = len(data_dict[element])
    data_per_cpu_list = [] #one dict per cpu, each dict contain data lists for this cpu#[{idle: [], user: [] ...} {}]
    for i in range(0, nb_cpu):
        actual_cpu_dict = {}
        for data in data_available:
            actual_cpu_dict[data] = data_dict[data][i]
        data_per_cpu_list.append(actual_cpu_dict)

    scatter_per_cpu_list = []

    for i in range(0, nb_cpu):
        actual_cpu_dict = []
        for data_name in data_available:
            actual_cpu_dict.append(Scatter(x = x_values, y = data_per_cpu_list[i][data_name], name = data_name))
        scatter_per_cpu_list.append(actual_cpu_dict)

    data_for_server = []
    for i in range(0, nb_cpu):
        actual_cpu_list = []
        for data_name in data_available:
            actual_data_dict = {}
            actual_data_dict["name"] = data_name
            actual_data_dict["x"] = x_values
            actual_data_dict["y"] = data_per_cpu_list[i][data_name]
            actual_cpu_list.append(actual_data_dict)
        data_for_server.append(actual_cpu_list)

    app = dash.Dash()

    app.layout = html.Div([
        html.H1('CPU-monitor'),
        dcc.Dropdown(
            id='my-dropdown',
            options=dash_options,
            value='cpu'
        ),
        dcc.Graph(id='my-graph')
    ])

    @app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
        print selected_dropdown_value
        a = re.findall(r'\d+', selected_dropdown_value)
        index = 0
        if len(a) > 0:
            index = int(a[0]) + 1
        return {
            'data': data_for_server[index]
        }
    app.run_server()