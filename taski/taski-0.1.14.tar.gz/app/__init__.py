#coding: utf-8
from __future__ import print_function
import todoist_wrapper
import elo
import os
import argparse
import sys
from datetime import datetime
from planner import PriorityPlanner
import time
import yaml
import coloredlogs
import logging as log


VERSION="0.1.14"

def get_config(args):
    try:
        fs = open(args.config)
    except IOError as e:
        log.error("Can't open config file: %s\n" % args.config)
        raise e

    cfg = yaml.load(fs)
    fs.close()
    # TODO validate config
    # keys in config file:
    # email:
    # password:
    # plan_skip_projects:
    # rank_skip_projects:
    # timezone:  # https://pypi.python.org/pypi/tzlocal
    return cfg

def get_app(cfg):

    app = todoist_wrapper.Todoist()
    app.init(cfg)

    return app

def show_old_tasks(app, args, cfg):
    tasks = app.get_tasks()
    tasks = sorted(tasks, key=lambda x: x.ts_added)
    now = datetime.now()
    for t in tasks:
        delta = (now - t.ts_added).days
        if delta > 180:
            print(delta, "days\t", t)

def show_completed_tasks(app, args, cfg):
    tasks = app.get_completed_tasks(since=args.since, until=args.until)
    tasks = sorted(tasks, key=lambda x: x.ts_done)
    for t in tasks:
        print(t.ts_done, t)


def show(app, args, cfg):
    if args.show_cmd == "api_token":
        print(app.get_token())
    elif args.show_cmd == "stats":
        print(app.get_stats())
    elif args.show_cmd == "config":
        print(yaml.dump(cfg))
    elif args.show_cmd == "old_tasks":
        show_old_tasks(app, args, cfg)
    elif args.show_cmd == "completed_tasks":
        show_completed_tasks(app, args, cfg)


def rank(app, args, cfg):
    projects = app.get_projects()

    for p in projects:
        if p.name in cfg["rank_skip_projects"]:
            log.info("Skip project: " + p.name)
            continue
        if args.project is not None and p.name != args.project:
            log.info("Skip project: " + p.name)
            continue
        print(p.name, "[", len(p.tasks), "]")
        tasks = elo.sort(p.tasks)
        p.tasks = tasks
        #app.update_project(p)

        i = 0
        for t in p.tasks:
            app.update_task(t, item_order=i)
            i += 1
        if args.dryrun:
            log.info("Dry run mode, will not commit")
        else:
            app.update()

    print("OK")

def choose_func(planner_item):
    tasks = planner_item.item.tasks
    if len(tasks) > 0:
        r = tasks[0]
        planner_item.item.tasks = tasks[1:]
        return r
    else:
        return None

def schedule(app, res, offset=0, tasks_per_day=10):
    """ offset is the position that we should start plan for today's taks. That
        means if today we've finished n tasks, we skip the first n finished
        tasks and start to plan the n+1 task.
    """
    if offset >= tasks_per_day:
        log.warn("offset too large: %d", offset)
        offset = tasks_per_day # Good job! Award him/her with more tasks!

    j = offset
    for task in res:
        # schedule t for today
        seq = j
        #tp.schedule_for(t.id, j)
        day = seq / tasks_per_day
        minute = seq % tasks_per_day
        date_string = "in {day} days at 22:{minute:02}".format(day=day, minute=minute)
        app.update_task(task, date_string=date_string)
        log.info("Task planned at \"%s\". Task: %-20s", date_string, task)
        #t: Pytodoist Task
        app.mark_as_planned(task)
        j += 1

def plan(app, args, cfg):
    def adjust_for_completed_tasks(stats):
        total = 0
        done = 0
        # completed tasks are sorted from new to old
        tasks = app.get_completed_tasks()
        now = datetime.now()
        for t in tasks:
            if (now - t.ts_done).total_seconds() > 3 * 24 * 3600:
                # larger than 3 days
                break
            pid = t.pid
            if stats.has_key(pid):
                stats[pid] += 1
            else:
                stats[pid] = 1
            total += 1

            if t.done:
                done += 1
        stats['total'] = total
        stats['done'] = done

    projects = app.get_projects()
    project_blacklist = cfg["plan_skip_projects"]
    for p in projects[:]:
        if p.name in project_blacklist:
            log.info("skip project when planning: %s", p.name)
            projects.remove(p)

    planner = PriorityPlanner(cfg, preprocess=adjust_for_completed_tasks)

    n = 0
    res = []
    for t in planner.plan(projects, choose_func):
        res.append(t)
        n += 1
        if n >= args.limit:
            break
    offset = app.num_tasks_completed_today(cfg["timezone"])
    log.debug("Schedule offset: %d" % offset)

    log.debug("Plan result:")
    for item in res:
        log.debug("%s", item)
    #planner.run(projects)
    schedule(app, res, offset=offset, tasks_per_day=args.daily_goal)

    app.clean_up()

    if args.dryrun:
        log.info("Dry run mode, will not commit")
    else:
        app.update()

    print("OK")


def check_positive_int(val):
    ival = int(val)
    if ival <= 0:
        raise argparse.ArgumentTypeError("%s is not a positive integer" % val)
    return ival

def str2unicode(val):
    return unicode(val, sys.getfilesystemencoding())

def test(app, args, cfg):
    print(args)
    #offset = app.num_tasks_completed_today(cfg["timezone"])
    print(app.user.is_premium)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="config file path")
    parser.set_defaults(config=os.path.expanduser("~") + "/.taski.yaml")

    parser.add_argument('-d', '--dryrun', help="dryrun", action='store_true')
    parser.add_argument('-v', '--verbose', help="enable debugging", action='store_true')

    subparsers = parser.add_subparsers(help='available commands')

    plan_parser = subparsers.add_parser('plan', help='plan tasks')
    plan_parser.add_argument('-l', '--limit',
                             help='limit number of tasks to plan',
                             type=check_positive_int, default=30)
    plan_parser.add_argument('-n', '--daily-goal',
                             help='number of tasks scheduled per day',
                             type=check_positive_int, default=10)
    plan_parser.set_defaults(func=plan)

    rank_parser = subparsers.add_parser('rank', help='rank tasks')
    rank_parser.add_argument('-p', '--project', help='project name',
                             type=str2unicode)
    rank_parser.set_defaults(func=rank)

    show_parser = subparsers.add_parser('show', help='show things')
    show_parser.add_argument('show_cmd', help='show things',
            choices=["api_token", "stats", "config", "old_tasks", "completed_tasks"])
    show_parser.add_argument('--since', help='show completed task since this date. Format "2007-4-29T10:13"')
    show_parser.add_argument('--until', help='show completed task until this date. Format "2007-4-29T10:13"')
    show_parser.set_defaults(since=None)
    show_parser.set_defaults(until=None)
    show_parser.set_defaults(func=show)

    version_parser = subparsers.add_parser('version', help='print version number')
    version_parser.set_defaults(quick_func=lambda args: sys.stdout.write(VERSION + "\n"))

    test_parser = subparsers.add_parser('test', help=u"¯\_(ツ)_/¯")
    test_parser.set_defaults(func=test)

    args = parser.parse_args()

    FORMAT = "%(asctime)-15s %(levelname)-6s %(message)s"
    os.environ['COLOREDLOGS_LOG_FORMAT'] = FORMAT
    if args.verbose:
        coloredlogs.install(level='DEBUG')
    else:
        coloredlogs.install(level='INFO')

    if hasattr(args, "quick_func"):
        args.quick_func(args)


    if hasattr(args, "func"):
        cfg = get_config(args)
        app = get_app(cfg)
        args.func(app, args, cfg)
