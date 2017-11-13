#from bgionline.cli import PATH_MATCHES
from bgionline import config
from bgionline.utils import get_fully_path


def find_char_last_index(char, string):
    pos = len(string)
    while pos > 0:
        pos = string[:pos].rfind(char)
        if pos == -1:
            return -1
        num_backslashes = 0
        test_index = pos - 1
        while test_index >= 0 and string[test_index] == '\\':
            num_backslashes += 1
            test_index -= 1
        if num_backslashes % 2 == 0:
            return pos
    return -1


def split_unescaped(char, string, include_empty_strings=False):

    words = []
    pos = len(string)
    lastpos = pos
    while pos >= 0:
        pos = find_char_last_index(char, string[:lastpos])
        if pos >= 0:
            if pos + 1 != lastpos or include_empty_strings:
                words.append(string[pos + 1: lastpos])
            lastpos = pos
    if lastpos != 0 or include_empty_strings:
        words.append(string[:lastpos])
    words.reverse()
    return words


def get_next_path(path, path_list):
    new_path_list = []
    if path is '':
        for i in path_list:
            new_path_list.append(i.partition('/')[0])
        return new_path_list
    if path.endswith('/'):
        for i in path_list:
            if i.startswith(path) and i != path:
                try:
                    new_path_list.append(path + (i.partition(path)[2]).partition('/')[0])
                except:
                    pass
    else:
        for i in path_list:
            if i.startswith(path) and i != path:
                try:
                    new_path = path + i.partition(path)[2].split('/')[0]
                    # print (new_path)
                    # print (i)
                    if new_path != i:
                        new_path += '/'
                    new_path_list.append(new_path)
                except:
                    pass
    return list(set(new_path_list))


class BOCompleter:
    command = ['login', 'logout', 'new', 'select', 'pwd', 'sh', 'tree', 'ls', 'cd', 'mkdir', 'rm', 'mv',
               'upload', 'download', 'find', 'transfer']

    subcommands = {'find': ['data ', 'app ', 'job ', 'project '],
                   'new': ['project ', 'user '],
                   }

    silent_commands = set(['export'])

    def __init__(self,path_matches):
        self.commands = [subcmd + ' ' for subcmd in self.command if subcmd not in self.silent_commands]
        self.matches = []
        self.text = None
        self.path_matches = path_matches

    def get_command_matches(self, prefix):
        self.matches = [cmd for cmd in self.commands if cmd.startswith(prefix)]

    def get_subcommand_matches(self, command, prefix):
        if command in self.subcommands:
            self.matches = [command + ' ' + sub for sub in self.subcommands[command] if sub.startswith(prefix)]

    def get_matches(self, text, want_prefix=False):
        self.text = text
        space_pos = find_char_last_index(' ', text)
        words = split_unescaped(' ', text)

        if len(words) > 0 and space_pos == len(text) - 1:
            words.append('')
        num_words = len(words)
        self.matches = []
        if num_words == 0:
            self.get_command_matches('')
        elif num_words == 1:
            self.get_command_matches(words[0])
        elif num_words == 2 and words[0] in self.subcommands:
            self.get_subcommand_matches(words[0], words[1])
        else:
            if words[0] in ['tree', 'ls', 'cd', 'mkdir', 'rm', 'mv', 'upload', 'download']:
                path = get_fully_path(words[1], False)
                if words[1]=='':
                    if path != '/':
                        path += '/'
                path_addrs = get_next_path(path, self.path_matches)
                self.matches = []
                for match in path_addrs:
                    if match.startswith(config.current_wd):
                        match = match.replace(config.current_wd, '', 1)
                    if match != '':
                        self.matches.append(text[:space_pos + 1] + match)
        return self.matches

    def complete(self, text, state):
        if state == 0:
            # print (text)
            self.get_matches(text, want_prefix=True)

        if state < len(self.matches):
            return self.matches[state]
        else:
            return None