# !usr/bin/env python
# coding=gbk
import os


def modify_markdown(path_to_process='post'):
    for parent, dirnames, filenames in os.walk(path_to_process):
        for filename in filenames:
            file_path = os.path.join(parent, filename)
            file_md = open(file_path, 'r')
            all_lines = file_md.readlines()
            file_md.close()
            for line in all_lines:
                if 'category: ' in line:
                    value = line
                    insert_index = all_lines.index(value)
                    all_lines.remove(value)
                    all_lines.insert(insert_index, '- ' + value.split(' ')[1] + '\n')
                    all_lines.insert(insert_index, 'categories:\n')
            file_md = open(file_path, 'w')
            file_md.writelines(all_lines)
    return 0
