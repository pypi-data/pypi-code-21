from __future__ import print_function
from termcolor import cprint
import re
import sys
import os

# 全局 代码区域定义


def py_is_fun(vv):
    global py_is
    if vv == '``` py':
        py_is = True

    elif vv == '```':
        py_is = False


def input_w(file, value):
    file.write('\n' + value + '\n')

# 匹配中文


def is_zh(line):
    xx = u"([\u4e00-\u9fff]+)"
    pattern = re.compile(xx)
    results = pattern.findall(line)
    return bool(results) and (len(results[0]) == len(line))
# 匹配中英文


def is_en_zh(line):
    xx = u"([\u4e00-\u9fff]+)"
    ch_pat = re.compile(xx)
    en_pat = re.compile('[a-zA-Z]+')
    ch_words = ch_pat.findall(line)
    en_words = en_pat.findall(line)

    return len(ch_words) and len(en_words)


global py_is
py_is = False


def main():
    input_value = {
        'h2': "## ",
        'start_tcode': "``` py\n",
        'end_code': '```\n'
    }

    # 获得 文本文字
    try:
        Path = sys.argv[1]
        mkfileopen = open(Path)
        lines = mkfileopen.readlines()
        mkfileopen.close()
    except Exception as identifier:
        helpput = """useag:
    $ doc2md2 file1 file2
        file2.md is create markdown from file1.md
        
    $ doc2md2 file1
        file1.md is create markdown from file1
            """
        return print(helpput)

    # 不需要改变，直接写入,开头匹配
    res = [r"``` py", r"更好的方法", r"#", r"```", r'---', '<!-- more -->']
    match_value_s = []

    for k, line in enumerate(lines):
        for re_value in res:
            if line.isspace():
                # \n 换行 直接 插入
                # print('直接原文空格\n',)
                match_value_s.append(line)
                break

            match_value = re.match(re_value, line.strip(), re.M | re.I)

            if match_value:

                # 代码开始—结束的区域固定
                # ``` py
                # ```
                # print('两个```py 代码', line)
                if py_is and re_value == r'``` py':
                    match_value_s.append(input_value['end_code'] + line)
                    py_is_fun('```')
                    break
                elif re_value == r'``` py':
                    py_is_fun(re_value)
                    # print('本来开始代码', line)
                    match_value_s.append(line)
                    break
                elif re_value == r'```':
                    # print('本来结束代码', line)
                    match_value_s.append(line)
                    py_is_fun('```')
                    break
                elif py_is:
                    # print('其他白名单前代码闭合', line)
                    match_value_s.append(input_value['end_code'] + line)
                    py_is_fun('```')
                    break
                else:
                    # print('原文白名单', line)
                    match_value_s.append(line)
                    break

        else:

            # 有中文有英文，不做处理
            # 多个中文片段
            if is_en_zh(line) is not 0 or is_zh(line) > 1:
                if py_is:
                    match_value_s.append(input_value['end_code'] + line)
                    # print('end', line)
                    py_is_fun('```')

                else:
                    # print('原本中文或英文不用加', line)
                    match_value_s.append(line)

            # 单个中文片段，加 h2
            elif is_zh(line) and is_zh(line) <= 1:
                if py_is:
                    match_value_s.append(
                        input_value['end_code'] + input_value['h2'] + line)
                    # print('加h2+end', line)
                    py_is_fun('```')

                else:
                    # print('加h2', line)
                    match_value_s.append(input_value['h2'] + line)
            # 默认
            elif py_is is False:

                match_value_s.append(input_value['start_tcode'] + line)
                # print('start', str(k), repr(line))
                py_is_fun('``` py')

            else:
                # print('默认原文', line)
                match_value_s.append(line)

    if py_is is True:
        match_value_s.append('\n' + input_value['end_code'])

    try:
        if len(sys.argv) > 2:
            write_file = sys.argv[2]
        else:
            write_file = Path

        if write_file.find('md') <= 0:
            write_file = write_file + '.md'

        file = open(write_file, 'w+')
        for i in match_value_s:
            file.write(i)
        file.close()

        output = "< {} >file is create markdown from < {} >".format(
            write_file, Path)
        cprint(output, 'green')

    except Exception as identifier:
        raise Exception(write_file, 'error', identifier)


if __name__ == '__main__':
    main()
