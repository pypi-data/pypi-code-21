import argparse
import sys

APP_DESC = """
这就是描述
"""
print(APP_DESC)
if len(sys.argv) == 1:
    sys.argv.append('--help')

helpString = {
    'quality': "download video quality : 1 for the standard-definition; 3 for the super-definition",
    'verbose': "print more debugging information",
    'store': "保存流媒体文件到指定位置",
    'config': "读取~/.danmu.fm配置,请~/.danmu.fm指定数据库",
    'url': "zhubo page URL (http://www.douyutv.com/*/)"
}

parser = argparse.ArgumentParser()
parser.add_argument('-q', '--quality', type=int, default=0, help=helpString.get('quality'))
parser.add_argument('-v', '--verbose', default=0, help=helpString.get('verbose'))
parser.add_argument('-s', '--store', help=helpString.get('store'))
parser.add_argument('-c', '--config', default=0, help=helpString.get('config'))
parser.add_argument('url', metavar='URL', nargs='+', help=helpString.get('url'))
args = parser.parse_args()


# 获取对应参数只需要 args.quality, args.url之类
def main():
    url = (args.url)[0]
    print(url)


if __name__ == '__main__':
    main()
