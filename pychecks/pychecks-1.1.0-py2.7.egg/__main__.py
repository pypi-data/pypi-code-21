# coding : utf8

import os
import sys
import commands


def main():
    if len(sys.argv) < 2:
        dir = commands.getoutput("pwd")
    else :
        dir = sys.argv[1]

    datas = {}
    for path, dirs, files in os.walk(dir):
        files = filter(lambda i:i.endswith(".py"), files)
        if 'egg' in path:
            continue
        if not files:
            continue
        files = map(lambda i:os.path.join(path,i), files)
        for file in files:
            cmd = "pylint {file}".format(file=file)
            output = commands.getoutput(cmd)
            score = output.split(':')[-1].split('/')[0].strip()
            try:
                datas[file] = float(score)
            except:
                continue

    print 'All python file is rated by pylint. Rank:'
    for file, score in sorted(datas.items(), key=lambda x:x[1], reverse=True):
        print file, score
    return 0


if __name__ == "__main__":
    sys.exit(main())