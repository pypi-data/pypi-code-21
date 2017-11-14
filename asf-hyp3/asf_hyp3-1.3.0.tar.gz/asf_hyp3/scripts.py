# encoding: utf-8
# scripts.py
# Rohan Weeden, William Horn
# Created: June 5, 2017

# Defines a few useful user scripts

import os
import re
import requests
import sys
import threading
import time
import io

try:
    import curses
except:
    pass


def download_products(
        api,
        directory="hyp3-products/",
        id=None,
        sub_id=None,
        sub_name=None,
        creation_date=None,
        verbose=True,
        threads=0):
    try:
        product_list = api.get_products(id, sub_id, sub_name, creation_date)
    except requests.ConnectionError:
        if verbose:
            print("Could not connect to the api")
        return
    # Check that the api call succeeded
    if 'message' in product_list:
        return product_list['message']

    ###################################
    # Define Helper functions/classes #
    ###################################

    # Downloading without progress tracking
    def download(url, out_name):
        resp = requests.get(url, stream=True)
        with open(out_name, 'wb') as out_f:
            out_f.write(resp.content)

    # Download with progress tracking
    def download_with_progress(url, out_name, bar):
        if bar is not None:
            bar.download(url, out_name)
        elif sys.stdout.isatty():
            # If curses is available on this platform, use it for clearing
            # the terminal
            try:
                curses.setupterm()
                bar = CursesBar()
            except NameError:
                # If Windows, we're out of luck... No progress tracking
                if os.name == 'nt':
                    download(url, out_name)
                    return
                else:
                    bar = AsciiBar()
            download_with_progress(url, out_name, bar)
        else:
            download(url, out_name)
        return bar

    # Progress bar template
    class DownloadBar(object):
        def __init__(self):
            self.bar_length = 50
            self.bar_template = "|{}{}| {}% "
            pass

        def download(self, url, out_name):
            resp = requests.get(url, stream=True)
            self.size = int(resp.headers['content-length'])
            with open(out_name, 'wb') as out_f:
                self.done = 0
                for data in resp.iter_content(chunk_size=4096):
                    out_f.write(data)
                    self.done += len(data)
                    self.progress = int(self.bar_length * self.done / self.size)
                    # Clear the bar
                    self.clear()
                    sys.stdout.write(self.bar_template.format(
                        "█" * self.progress, " " * (self.bar_length - self.progress), 100 * self.done / self.size))
                    sys.stdout.flush()

    # Progress bar using curses function for clearing and getting terminal size
    class CursesBar(DownloadBar):
        def __init__(self):
            try:
                # Python 3
                super().__init__()
            except:
                # Python 2
                super(CursesBar, self).__init__()
            self.bar_length = curses.tigetnum('cols') - 15

        def clear(self):
            sys.stdout.write(str(curses.tigetstr('cr')) + str(curses.tigetstr('el')))

    # Progress bar using basic terminal. Does not work correctly on windows
    class AsciiBar(DownloadBar):
        def clear(self):
            sys.stdout.write("\r")

    class DownloadThread(threading.Thread):
        def __init__(self, url, out_name):
            super(DownloadThread, self).__init__()
            self._stop_event = threading.Event()
            self.url = url
            self.out_name = out_name

        def stop(self):
            self._stop_event.set()

        def stopped(self):
            return self._stop_event.is_set()

        def run(self):
            resp = requests.get(self.url, stream=True)
            with open(self.out_name, 'wb') as out_f:
                for data in resp.iter_content(chunk_size=4096):
                    if self.stopped():
                        out_f.close()
                        os.remove(self.out_name)
                        break
                    out_f.write(data)

    ###################################
    #  End Helper functions/classes   #
    ###################################

    # Create the download directory
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Check each product and download it if it doesnt exist already
    failed_products = 0
    total_products = 0
    active_threads = 0
    threads_list = [None] * threads
    thread_index = 0
    bar = None
    for product in product_list:
        name = product['name']
        # Check if it has already been downloaded
        file_name = os.path.join(directory, name)
        if not os.path.isfile(file_name):
            if verbose:
                print("Getting new product: {}".format(name))
            try:
                total_products += 1
                # Check if a thread slot is available and we are using threads
                if threads > 0 and active_threads < threads:
                    # Fire off a new download thread
                    threads_list[thread_index] = DownloadThread(product['url'], file_name)
                    threads_list[thread_index].start()
                    thread_index = (thread_index + 1) % threads
                    active_threads += 1
                    # Check if thread slots are full
                    if active_threads == threads:
                        try:
                            # wait for the first thread to complete
                            while threads_list[thread_index].isAlive():
                                time.sleep(0.05)
                                thread_index = (thread_index + 1) % threads
                        except KeyboardInterrupt:
                            for t in threads_list:
                                if t.isAlive():
                                    t.stop()
                                    failed_products += 1
                            if verbose:
                                print("")
                            break
                        active_threads -= 1
                else:
                    if verbose:
                        bar = download_with_progress(product['url'], file_name, bar)
                        print("Done")
                    else:
                        download(product['url'], file_name)
            except KeyboardInterrupt:
                if verbose:
                    print("Failed")
                failed_products += 1
                if os.path.isfile(file_name):
                    os.remove(file_name)
                if verbose:
                    print("")
                break
            except requests.ConnectionError:
                if verbose:
                    print("Failed")
                failed_products += 1
                if os.path.isfile(file_name):
                    os.remove(file_name)
    if verbose:
        print("Attempted to download {} products: {} succeeded, {} failed".format(
            total_products, total_products - failed_products, failed_products))


# General Pattern for detecting granules
_granule_pattern = re.compile(
    r'(S1[A-D]_\w\w_(GRD|SLC|OCN)\w_[12]\w{3}_\w{15}_\w{15}_\w{6}_\w{6}_\w{4})')


def _is_open_file(possible_file):
    isFile = False

    try:
        isFile = isinstance(possible_file, io.IOBase)
    except:
        isFile = isinstance(possible_file, file)
    finally:
        return isFile


# Searches a text file for granules and returns a list of all granules found.
# Takes a string of the filepath/name
def load_granules(filename):
    # If a str, treat it as a path
    if isinstance(filename, str):
        with open(filename, 'r') as granule_file:
            data = granule_file.read()

    # If a file object is passed
    elif _is_open_file(filename):
        data = filename.read()
    else:
        raise TypeError(
            "Hyp3::scripts - Invalid arg ({}) passed to load_granules".format(filename))

    granules = set()
    # Iterat through adding matches to granules
    for match in re.finditer(_granule_pattern, data):
        granules.add(match.group(0))
    # Return all the granules found in the file with no repeats
    return list(granules)


def __test_load_granules(path):

    print("|-------- TESTING load_granules (string)-------|")
    granules = load_granules(path)
    for g in granules:
        print(g)

    print("|-------- TESTING load_granules (file obj) -------|")
    f = open(path)
    granules = load_granules(f)
    print(granules)


if __name__ == '__main__':

    while True:
        try:
            path = str(raw_input("path to file with granules: "))
        except:
            print("error with input")
        else:
            break

    __test_load_granules(path)
