import csv
import os
import httplib2
import sys
import os

'''
Amazon get file command
- g -generate file
'''


class Amazon_File:

    directory = os.path.dirname(__file__)
    dir_file = os.path.join(directory, 'amazon_uni.csv')
    print("current folder .. {}".format(dir_file))
    # dir_file = 'amazon_uni.csv'

    def __init__(self):
        self.csv_file = open(self.dir_file, 'r')
        self.file = csv.reader(self.csv_file)
        self.cache = []

    def __iter__(self):
        self.cache_index = 1
        return self

    def __next__(self):
        self.cache_index += 1

        if len(self.cache) >= self.cache_index:
            return self.cache[self.cache_index - 1]

        # if self.file.
        if self.csv_file.closed:
            raise StopIteration

        # line = self.file.readline()
        line = next(self.file, None)
        if not line:
            self.csv_file.close()
            raise StopIteration

        tup = (line[0], line[1], line[2])
        self.cache.append(tup)
        # print(tup)

        return tup


files = Amazon_File()

# for folder_name, file_name, uri in files:D


def rename_file(folder_name):
    ok = "\033[32m OK \033[0m"
    os.chdir(folder_name)
    for folder in os.listdir(os.curdir):
        if os.path.isfile(os.path.join(os.curdir, folder)):
            continue
        for _file_name in os.listdir(os.path.join(os.curdir, folder)):
            file_name = os.path.join(os.curdir, folder, _file_name)
            if _file_name == 'viewed.csv':
                os.rename(file_name, os.path.join(
                    os.curdir, folder, 'most_viewed.csv'))
            if _file_name == 'viewed_low.csv':
                os.rename(file_name, os.path.join(
                    os.curdir, folder, 'low_stock.csv'))
            print('dont - {}'.format(file_name))


def structure_folder(folder_name):
    ok = "\033[32m OK \033[0m"
    os.chdir(folder_name)
    for folder in os.listdir(os.curdir):
        if os.path.isfile(os.path.join(os.curdir, folder)):
            continue

        print("\"{}\" =>".format(folder), end=' ')
        print("[")
        for _file_name in os.listdir(os.path.join(os.curdir, folder)):
            print("\'{}\',".format(_file_name))
        print("],")


def generate_file_and_folder(folder_name):
    ok = "\033[32m OK \033[0m"
    error = "\033[31m ERROR \033[0m"

    path = None

    try:
        path = os.environ['P3_REPORT_PATH']
    except KeyError:
        print("No Key: set to default..")

    if not path:
        path = os.path.expanduser("~/")

    os.chdir(path)

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    os.chdir(folder_name)
    # hacky shit that skip the header
    skip = True

    for folder_name, file_name, uri in files:

        if skip:
            skip = False
            continue

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        try:
            h = httplib2.Http(
                os.path.join(path, '.cache'))
            # with open(os.path.join(folder_name, file_name), 'wb') as a_file:
            #     print(uri)
            #     with urllib.request.urlopen(uri) as response:
            #         a_file.write(response.read())
            #         print("{} - {}".format(ok, os.path.join(folder_name,
            #                                                 file_name)))

            # this is how you parse date string in python
            # d = datetime.datetime.strptime(
            # response.dict["last-modified"], '%a, %d %b %Y %H:%M:%S GMT')
            with open(os.path.join(folder_name, file_name), 'wb') as a_file:
                print(uri)
                response, content = h.request(uri)
                a_file.write(content)
                print("s:{} p:{} c:{}".format(ok, os.path.join(
                    folder_name, file_name), response.fromcache))
                # print("{} - {} - cached: {}".format(ok,
                #                                     os.path.join(folder_name, file_name)), response.fromcache)

        except Exception as identifier:
            print("Error when opening the file or url {}".format(identifier))
            raise identifier


def main():
    # if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--generate", help="generate files",
                        action="store_true")

    parser.add_argument("-r", "--rename", help="rename files",
                        action="store_true")

    parser.add_argument("-s", "--struc", help="rename files",
                        action="store_true")
    args = parser.parse_args()
    if args.generate:
        while True:
            folder_name = input(
                'Please key in the folder name, format has to be like this d/m/ yy (1-3-86): ')

            if folder_name:
                generate_file_and_folder(folder_name)
                break
    elif args.rename:
        folder_name = input(
            'Please key in the folder name, format has to be like this d/m/ yy (1-3-86): ')
        rename_file(folder_name)
    elif args.struc:
        folder_name = input(
            'Please key in the folder name, format has to be like this d/m/ yy (1-3-86): ')
        structure_folder(folder_name)

    else:
        parser.print_help()
