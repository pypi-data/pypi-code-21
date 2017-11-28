

import time
import re
import argparse
from cpu_info import get_cpu_info
from graphic_output import pretty_print, graphic_print, print_legend
from graph_maker import draw_graph
from loader import launch_cpu_load
import os

def pars_args():
    parser = argparse.ArgumentParser(description="A cpu usage logging software")
    parser.add_argument("--no_display", action="store_true", default=False, help="programm run without displaying and can"
                                                                              " still log")
    parser.add_argument("--version", action="version", version='%(prog)s 0.01')
    parser.add_argument("--load", action="store", dest="load_nb_threads", help="Define the number of threads to load during the monitoring"
                                                                           "If not used the cpu won't be loaded")
    parser.add_argument("--load_standalone", action="store_true", default=False, help="Does not monitor the CPU usage but "
                                                                                 "only launch load the "
                                                                                 "N threads provided by the --load "
                                                                                 "option, if --load option is not "
                                                                                 "provided only one thread will have "
                                                                                 "workload.")
    parser.add_argument("--display_operations_per_second", action="store_true", default=False, help="display number of "
                                                                                                 "operation per "
                                                                                                 "second if "
                                                                                                 "--loadstandalone "
                                                                                                 "option is used.")

    parser.add_argument("--cpu_info", action="store_true", default=False, help="Display informations about the CPU used and "
                                                                           "exit.")
    parser.add_argument("--cpu_info_detailed", action="store_true", default=False, help="Display extended informations "
                                                                                   "about the CPU used and exit.")
    parser.add_argument("--monitoring_freq", action="store", default=1, help="Monitoring frequency in Hz")
    parser.add_argument("--log_to_file", action="store", dest="filename", help="Log gathered results to a file")
    parser.add_argument("--graph_from_log", action="store", dest="logfile", help="Draw  graph for each core and one for the "
                                                                             "whole cpu from the LOGFILE argument")
    parser.add_argument("--fancy", action="store_true", default=False, help="Display fancy percent color bars during cpu "
                                                                        "monitoring.")

    parser.add_argument("--log_size", action="store", default=-1, help="Define the maximum number of lines to keep in the "
                                                                  "log file")

    return parser.parse_args()






def read_proc(proc_file):
    proc_content = proc_file.read()
    proc_file.seek(0)
    proc_lines = proc_content.split("\n")
    revelant_lines = []
    for line in proc_lines:
        if ("cpu" in line):
            revelant_lines.append(line)
    return revelant_lines

def calculate_percent(part, all):
    return (part * 100) / all

def calculator(actual_line_arg_str, previous_line_arg_str):
    actual_line_str = re.split("\s*", actual_line_arg_str)
    previous_line_str = re.split("\s*", previous_line_arg_str)
    name = actual_line_str[0]
    actual_line = []
    previous_line = []
    for i in range(1, len(actual_line_str)):
        previous_line.append(int(previous_line_str[i]))
        actual_line.append(int(actual_line_str[i]))

    actual_user = actual_line[0]
    actual_nice = actual_line[1]
    actual_system = actual_line[2]
    actual_idle = actual_line[3]
    actual_iowait = actual_line[4]
    actual_irq = actual_line[5]
    actual_softirq = actual_line[6]

    previous_user = previous_line[0]
    previous_nice = previous_line[1]
    previous_system = previous_line[2]
    previous_idle = previous_line[3]
    previous_iowait = previous_line[4]
    previous_irq = previous_line[5]
    previous_softirq = previous_line[6]

    #time per task type
    user = actual_user - previous_user
    nice = actual_nice - previous_nice
    system = actual_system - previous_system
    idle = actual_idle - previous_idle
    iowait = actual_iowait - previous_iowait
    irq = actual_irq - previous_irq
    softirq = actual_softirq - previous_softirq

    time_spent = user + nice + system + idle + iowait + irq + softirq

    relevant = True
    if (time_spent == 0):
        relevant = False

    if(relevant):
        result = {}
        user_percent = calculate_percent(user, time_spent)
        nice_percent = calculate_percent(nice, time_spent)
        system_percent = calculate_percent(system, time_spent)
        idle_percent = calculate_percent(idle,time_spent)
        iowait_percent = calculate_percent(iowait, time_spent)
        irq_percent = calculate_percent(irq, time_spent)
        softirq_percent = calculate_percent(softirq, time_spent)
        result["user"] = user_percent
        result["nice"] = nice_percent
        result["system"] = system_percent
        result["idle"] = idle_percent
        result["iowait"] = iowait_percent
        result["irq"] = irq_percent
        result["softirq"] = softirq_percent
        result["name"] = name
        return result
    else:
        return None


def set_time_stamp(actual_log_size, log_file):
    if(log_file):
        time_stamp = "[ " + str(time.time()) + " ]\n"
        log_file.write(time_stamp)
        actual_log_size += 1
    return actual_log_size

def write_to_log(actual_log_size, max_logsize, value_to_write, log_fp):
    if(value_to_write is not None and log_fp):
        log_fp.write(str(value_to_write) + "\n")
        actual_log_size += 1
    return actual_log_size

def log(log_file_pointer, max_log_file_size, update_freq, fancy, proc_file, no_display):
    sleep_time = 1 / float(update_freq)
    previous_lines = None
    actual_log_size = 0
    while True:
        revelant_lines = read_proc(proc_file)
        if (previous_lines and previous_lines != revelant_lines):
            actual_log_size = set_time_stamp(actual_log_size, log_file_pointer)
            for i in range(0, len(revelant_lines)):
                result = calculator(revelant_lines[i], previous_lines[i])
                to_print_or_save = pretty_print(result)
                if(no_display == False):
                    if (fancy):
                        graphic_print(result)
                    else:
                        print to_print_or_save
                actual_log_size = write_to_log(actual_log_size,max_log_file_size,
                                                                 to_print_or_save, log_file_pointer)
        previous_lines = revelant_lines
        time.sleep(sleep_time)
        os.system('clear')
        if fancy:
            print_legend()
        if log_file_pointer is not None:
            log_file_pointer.flush()
            if actual_log_size >= max_log_file_size and max_log_file_size > -1:
                log_file_pointer.seek(0)
                print actual_log_size
                actual_log_size = 0


def main():
    parsed_args = pars_args()
    display = parsed_args.display_operations_per_second
    standalone = parsed_args.load_standalone
    max_log_size = int(parsed_args.log_size)
    #display values
    fancy = parsed_args.fancy
    no_display = parsed_args.no_display

    freq = int(parsed_args.monitoring_freq)
    filename = parsed_args.filename
    proc_file = open("/proc/stat", "r")
    fp = None
    if filename:
        fp = open(filename, 'w')  # not closed !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if(parsed_args.logfile):
        draw_graph(parsed_args.logfile)
        exit(0)
    if(parsed_args.load_nb_threads):
        load = int(parsed_args.load_nb_threads)
    else:
        load = None
    if (parsed_args.cpu_info):
        get_cpu_info(to_display=True)
        exit()
    if (parsed_args.cpu_info_detailed):
        get_cpu_info(to_display=True, detailed=True)
        exit()
    if (display):
        if (not standalone):
            display = False
    if (load is not None or standalone):
        if (load is not None):
            launch_cpu_load(display, standalone, no_of_cpu_to_be_consumed=load)
        else:
            launch_cpu_load(display, standalone)
        if standalone:
            while True:
                time.sleep(1)
    log(fp, max_log_size, freq, fancy, proc_file, no_display)

if __name__ == '__main__':
    main()

main()
