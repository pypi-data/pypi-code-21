import random
from pyecharts import *
from pyecharts.constants import DEFAULT_HOST
from flask import Flask, render_template
from datatoaster import *

app = Flask(__name__)

Width, Height = 700, 500


def generate_example_data():
    result = []
    for i in range(0, random.randint(20, 50)):
        result.append({"OS": ["Android", "Windows", "iOS"][random.randint(0, 2)],
                       "PaidAmount": int(max(0, random.randint(0, 1000) - 500) * random.random())})
    return result


def format_json(src):
    return str(src).replace("}, ", "}, \n").replace("'", "\"")


@app.route("/")
def index():
    demo_data = generate_example_data()

    bar_chart_1_raw = datatoaster.DataSet(demo_data) \
        .set_x(lambda i: i["OS"]) \
        .set_y(datatoaster.DataSet.NumberOfAppearance) \
        .get_result()

    bar_chart_1 = Bar("Amount of Users Per OS", "How many users use each OS?", width=Width, height=Height)
    bar_chart_1.add("OS", list(bar_chart_1_raw.keys()), list(bar_chart_1_raw.values()), mark_point=["max", "min"])

    pie_chart_1_raw = datatoaster.DataSet(demo_data) \
        .set_x(lambda i: i["OS"]) \
        .set_y(datatoaster.DataSet.Percentage) \
        .get_result()

    pie_chart_1 = Pie("Percentage of OS", width=Width, height=Height)
    pie_chart_1.add("", list(pie_chart_1_raw.keys()), list(pie_chart_1_raw.values()), is_label_show=True)

    bar_chart_2_raw = datatoaster.DataSet(demo_data) \
        .set_x(lambda i: i["OS"]) \
        .set_y(datatoaster.DataSet.PercentageWithinGroup) \
        .add_constraint(lambda i: i["PaidAmount"] != 0) \
        .get_result()

    bar_chart_2 = Bar("Percentage of Paid Users", width=Width, height=Height)
    bar_chart_2.add("", list(bar_chart_2_raw.keys()), list(bar_chart_2_raw.values()), is_label_show=True)

    bar_chart_3_raw = datatoaster.DataSet(demo_data) \
        .set_x(lambda i: i["OS"]) \
        .set_y(lambda d: [max([i["PaidAmount"] for i in d]), round(sum([i["PaidAmount"] for i in d])/len(d), 2)]) \
        .get_result()

    bar_chart_3 = Bar("The Maximum and Average Payment per OS", width=Width, height=Height)
    series = ["Maximum", "Average"]
    for i in range(0, len(next(iter(bar_chart_3_raw.values())))):
        bar_chart_3.add(series[i], list(bar_chart_3_raw.keys()), [j[i] for j in list(bar_chart_3_raw.values())], is_label_show=True)

    pie_chart_2_raw = datatoaster.DataSet(demo_data) \
            .set_x(datatoaster.DataSet.Single) \
            .set_y(datatoaster.DataSet.Percentage) \
            .add_constraint(lambda i: i["PaidAmount"] > 100)\
            .set_single(True)\
            .get_result()

    pie_chart_2 = Pie("Percentage of OS", width=Width, height=Height)
    pie_chart_2.add("", ["More than 100", "Less than 100"], [pie_chart_2_raw, 1-pie_chart_2_raw], is_label_show=True)

    return render_template('index.html',
                           bar_chart_1=bar_chart_1.render_embed(),
                           bar_chart_1_raw=format_json(bar_chart_1_raw),
                           pie_chart_1=pie_chart_1.render_embed(),
                           pie_chart_1_raw=format_json(pie_chart_1_raw),
                           bar_chart_2=bar_chart_2.render_embed(),
                           bar_chart_2_raw=format_json(bar_chart_2_raw),
                           bar_chart_3=bar_chart_3.render_embed(),
                           bar_chart_3_raw=format_json(bar_chart_3_raw),
                           pie_chart_2=pie_chart_2.render_embed(),
                           pie_chart_2_raw=format_json(pie_chart_2_raw),
                           dataset=format_json(demo_data),
                           host=DEFAULT_HOST,
                           script_list=bar_chart_1.get_js_dependencies())


if __name__ == '__main__':
    app.run()
