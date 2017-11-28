from colorama import init
init()
from colorama import Back, Style, Fore
def pretty_print(cpu_stat):
    pretty = ""
    data = ["name", "user", "nice", "system", "iowait", "irq","softirq", "idle"]
    for element in data:
        value = cpu_stat.get(element)
        if value is not None:
            pretty += element +": " + str(value) + "  "
    return pretty

def create_colors():
    colors_dic = {}
    colors_dic["user"] = Back.RED
    colors_dic["nice"] = Back.CYAN
    colors_dic["system"] = Back.GREEN
    colors_dic["iowait"] = Back.YELLOW
    colors_dic["irq"] = Back.MAGENTA
    colors_dic["softirq"] = Back.BLUE
    colors_dic["idle"] = Back.WHITE
    return colors_dic

def print_legend():
    legend = ""
    color_dic = create_colors()
    for load_type, color in color_dic.iteritems():
        legend += load_type + ":" + color + " " + Style.RESET_ALL + " "
    print (legend)


def graphic_print(cpu_stat):
    colors_dic = create_colors()
    data = ["name","user", "nice", "system", "iowait", "irq","softirq", "idle"]
    percent_bar = ""
    size_of_num = 0
    for element in data:
        value = cpu_stat.get(element)
        if (element=="name"):
            print value

        elif value is not None:
            percent_bar_part = " "  * value
            color = colors_dic.get(element)
            if color:
                percent_bar_part = color  + percent_bar_part + Style.RESET_ALL
                percent_bar_part, size_of_num_tmp = insert_percent_value(percent_bar_part, value, color)
                size_of_num += size_of_num_tmp
                percent_bar += percent_bar_part

    percent_bar_size = percent_bar.count(" ") + size_of_num
    if (percent_bar_size < 100):
        percent_bar += colors_dic.get("idle") + " " * (100 - percent_bar_size) + Style.RESET_ALL
    print percent_bar


def insert_percent_value(percent_bar_part, value, color):
    if (value != 0):
        str_value = str(value)
        size_value = len(str_value)
        size_bar = percent_bar_part.count(" ")
        index_value = 0
        list_bar = list(percent_bar_part)
        for index_percent_bar in range(size_bar/2, size_bar/2 + size_value):
            list_bar[index_percent_bar + len(color)] = str_value[index_value]
            index_value += 1
        return "".join(list_bar), size_value
    else:
        return percent_bar_part, 0
