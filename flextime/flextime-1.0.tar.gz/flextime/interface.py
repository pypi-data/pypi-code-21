import click
import yaml
import flextime

from datetime import date
from functools import reduce

class Menu:
    def __init__(self, tasktree, pagify=True, input_type='char'):
        self._exit = False
        self._unsaved = False

        self.tasktree = tasktree
        self.pagify = pagify
        self.input_type = input_type
        self._items = []
        self.page_offset = 0
        self.char_options = {
            'q': ('[q]uit', self.set_quit),
            'w': ('[w]rite unsaved changes', self.write, self.unsaved_changes),
            'n': ('[n]ext page', self.next_page, self.has_next_page),
            'p': ('[p]rev page', self.prev_page, self.has_prev_page),
        }
        self.cond_options = [(lambda x: x.isdigit(), self.select_item)]
        self.char_option_display = ['wq', 'pn']

    def run(self):
        while not self._exit:
            click.clear()
            click.echo(self.option_str())
            click.echo()
            click.echo(self.item_str())
            click.echo('> ', nl=False)
            if self.input_type == 'char':
                self.handle_option(click.getchar())
                click.echo()
            else:
                self.handle_option(input())

    def write(self):
        self.tasktree.save()
        self._unsaved = False
                
    def handle_option(self, choice):
        if choice in self.char_options:
            name, f, *rest = self.char_options[choice]
            if len(rest) == 0 or (len(rest) > 0 and rest[0]()):
                f()
                
        else:
            for o in self.cond_options:
                check, f = o
                if check(choice):
                    f(choice)
            
    def reset_offset(self):
        self.page_offset = 0

    def unsaved_changes(self):
        return self._unsaved
    
    def set_unsaved(self):
        self._unsaved = True
        
    def set_quit(self, *args):
        if self.unsaved_changes():
            if click.confirm('Exit without saving?'):
                self._exit = True
        else:
            self._exit = True

    def select_item(self, page_item_index):
        pass
       
    def has_prev_page(self):
        return self.page_offset > 0

    def has_next_page(self):
        num_items = len(self._items)
        return num_items > (self.page_offset + 1) * 10

    def get_item(self, page_item_index):
        if self.pagify:
            item_index = int(page_item_index) + self.page_offset*10
        else:
            item_index = int(page_item_index)

        if item_index < len(self._items):
            return self._items[item_index]
        else:
            return False

        
    def get_page_items(self):
        start = 0 + 10*self.page_offset
        end = 10 + 10*self.page_offset

        if start < len(self._items) and self.pagify:
            return self._items[start:end]
        else:
            return self._items

    def option_str(self):
        def option_to_str(o):
            if o in self.char_options:
                display_str, f, *rest = self.char_options[o]
                if len(rest) > 0 and not rest[0]():
                    return ''
                return display_str
            else:
                return ''
            
        strs = list(map(lambda s: list(map(option_to_str, s)), self.char_option_display))
        if len(strs) == 0:
            strs = [list(map(option_to_str, self.char_options.values()))]

        return '\n'.join([
            ' | '.join(filter(lambda s: s, line)) for line in filter(any, strs)
        ])
                
    def item_str(self):
        items = self.get_page_items()
        return "\n".join(["[{}] {}".format(i, str(item)) for i, item in enumerate(items)])
    
    def prev_page(self):
        if self.has_prev_page():
            self.page_offset -= 1

    def next_page(self):
        if self.has_next_page():
            self.page_offset += 1

class Add(Menu):
    def __init__(self, tasktree, path, merge_files, **kwargs):
        super(Add, self).__init__(tasktree, **kwargs)
        self.char_options.update({
            'a': ('easy [a]dd', self.add_interactive),
            'y': ('edit [y]aml', self.edit_yaml),
            'm': ('[m]erge files at current path', self.merge_files, self.merge_files_present),
            'u': ('[u]p a level', self.up_level),
        })

        self.char_option_display = [
            'wqaym',
            'upn',
        ]

        self._merge_files = merge_files
        self._path = flextime.utils.guess_path(tasktree.tree(), path) if len(path) > 0 else []
        self.reset_items()

    def merge_files_present(self):
       return len(self._merge_files) > 0

    def merge_files(self):
        if self.merge_files_present():
            merger = reduce(
                lambda acc, f: {**acc, **flextime.utils.file_to_dict(f)},
                self._merge_files,
                {}
            )

            click.echo('Current tree:')
            click.echo(flextime.utils.dump_dict(self.tasktree.branch_from_path(self._path)))
            click.echo('Tree from files:')
            click.echo(flextime.utils.dump_dict(merger))

            if click.confirm('Really merge?'):
                self.tasktree.merge_branch(self._path, merger)
                self._merge_files = []
                self.reset_items()
                self.set_unsaved()

    def option_str(self):
        return "Path: {}\n{}".format(' > '.join(map(str, self._path)), super(Add, self).option_str())
        
    def reset_items(self):
        self._items = self.tasktree.keys_from_path(self._path)
        
    def select_item(self, page_item_index):
        item = self.get_item(page_item_index)
        
        if item:
            self._path.append(item)
            self.reset_offset()
            self.reset_items()
 
    def up_level(self):
        if len(self._path) > 0:
            self._path.pop()
            
        self.reset_offset()
        self.reset_items()

    def add_interactive(self):
        click.echo()
        title = click.prompt('Task name', default='cancel')
        if title != 'cancel':
            due = click.prompt('Due date', default='none')
            time = click.prompt('Estimated time', default='none')
            new_branch = {title: {}}

            if due != 'none':
                new_branch[title]['_d'] = due

            if time != 'none':
                new_branch[title]['_t'] = time

            self.tasktree.merge_branch(self._path, new_branch)
            self.reset_items()
            self.set_unsaved()
        
    def edit_yaml(self):
        task_str = click.edit(flextime.utils.dump_dict(self.tasktree.branch_from_path(self._path)))
        if task_str is not None:
            data = yaml.safe_load(task_str)
            self.tasktree.replace_branch(self._path, data)
            self.reset_items()
            self.set_unsaved()
    
class SubMenu(Menu):
    def __init__(self, tasktree, **kwargs):
        super(SubMenu, self).__init__(tasktree, **kwargs)
        self.char_options['a'] = ('run [a]dd menu', self.run_add)
        self.char_option_display = [
            'wqa',
            'pn',
        ]

    def run_add(self):
        a = Add(self.tasktree, [], [])
        if self.unsaved_changes():
            a.set_unsaved()
        a.run()

        self.tasktree = a.tasktree
        self._unsaved = a.unsaved_changes()
        self.reset_items()
    
class List(SubMenu):
    def __init__(self, tasktree, sort_keys, **kwargs):
        super(List, self).__init__(tasktree, **kwargs)

        self._sort_keys = sort_keys
        self.reset_items()

    def reset_items(self):
        self._items = self.tasktree.sorted_leaves(self._sort_keys)
        
    def select_item(self, page_item_index):
        leaf = self.get_item(page_item_index)
        
        if leaf:
            self.tasktree.delete_branch(leaf.path)
            self.reset_items()
            self.set_unsaved()

class Show(SubMenu):
    def __init__(self, tasktree, schedule_file, **kwargs):
        super(Show, self).__init__(tasktree, **kwargs)
        self.schedule_file = schedule_file
        self.char_options['r'] = ('[r]eload solution', self.reset_solution)
        self.char_option_display = ['wqra', 'pn']

        self.reset_schedule()
        self.reset_items()
        
    def reset_solution(self):
        self.reset_schedule()
        self.reset_items()

    def reset_schedule(self):
        scheduler = flextime.Scheduler(self.tasktree, self.schedule_file)
        self.unscheduled, self.time_blocks = scheduler.scheduled_tasks()
        
    def reset_items(self):
        utups = [(-1, i, task) for i, task in enumerate(self.unscheduled)]
        ttups = [(i, ti, task) for i, tb in enumerate(self.time_blocks) for ti, task in enumerate(tb.tasks) if tb.has_tasks()]
        self._items = utups + ttups

    def select_item(self, page_item_index):
        item = self.get_item(page_item_index)
        
        if item:
            tb_ind, task_ind, task = item
            tmins, task = task
            
            self.tasktree.complete_task(task)
            if tb_ind == -1:
                self.unscheduled.pop(task_ind)
            else:
                self.time_blocks[tb_ind].tasks.pop(task_ind)

            self.reset_items()
            self.set_unsaved()

    def item_str(self):
        items = self.get_page_items()
        ret_lines = []
        prev_tb = -2

        for i, item in enumerate(items):
            tb_ind, task_ind, task = item
            tmins, task = task
            
            if tb_ind != prev_tb:
                if tb_ind == -1:
                    ret_lines.append('Unscheduled')
                else:
                    ret_lines.append(str(self.time_blocks[tb_ind]))

            prev_tb = tb_ind
            ret_lines.append(' [{}] ({} / {}) {}'.format(i, tmins, task.time(), str(task)))

        return '\n'.join(ret_lines)
