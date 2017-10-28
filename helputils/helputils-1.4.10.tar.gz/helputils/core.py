import copy
import errno
import inspect
import itertools
import itertools
import hashlib
import locale
import logging
import logging.handlers
import math
import os
import requests
import socket
import subprocess
import sys
import time
import traceback

from collections import Callable, Counter, OrderedDict
from difflib import SequenceMatcher
from functools import wraps
from math import ceil
from six import iteritems
from six.moves.urllib.parse import urlparse, parse_qs, urljoin
from subprocess import Popen, PIPE
from time import sleep

from PIL import Image
from pymongo import MongoClient
try:
    from gymail.core import send_mail
    has_gymail = True
except:
    has_gymail = False
from .defaultlog import log

tor_proxies = {
    'http': 'socks5://127.0.0.1:9050',
    'https': 'socks5://127.0.0.1:9050'
}
if sys.version_info[0] > 2:
    text_type = str
    string_types = (str,)


    def to_bytes(text):
        if not isinstance(text, bytes):
            text = bytes(text, 'utf8')
        return text
else:
    text_type = unicode
    string_types = (str, unicode)


    def to_bytes(text):
        if not isinstance(text, string_types):
            text = text_type(text)
        return text


try:
    from pathlib import Path


    def touch(fname):
        Path(fname).touch()
except:
    def touch(fname, times=None):
        with open(fname, 'a'):
            os.utime(fname, times)


def kill_defuncts(name):
    """Kill the pid and parent pid of any process that matches given name"""
    p1 = Popen(["ps", "-ef"], stdout=PIPE)
    out = p1.communicate()[0].decode("UTF-8").split("\n")
    pids = []
    ppids = []
    for x1 in out:
        if name in x1 and not "grep" in x1:
            x2 = x1.split()
            pids.append(x2[1])
            ppids.append(x2[2])
    log.info("Killing %s" % (pids + ppids))
    subprocess.call(["kill", "-9"] + pids + ppids)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def del_url_params(url):
    """Removes all GET parameters from the URL."""
    return urljoin(url, urlparse(url).path)


def get_redirected(url, del_params=False, timeout=6):
    """Get the url that a link eventually redirects to"""
    if not url:
        return None
    try:
        response = requests.get(url, timeout)
    except:
        sleep(20)
        try:
            response = requests.get(url, timeout)
        except:
            if has_gymail:
                send_mail(
                    event="error",
                    subject=os.path.basename(__file__),
                    message="Download from %s failed. Site possibly down." % url
                )
            log.error("Download from %s failed. Site possibly down." % url)
            return None
    if response.history:
        print("Request was redirected")
        for resp in response.history:
            print(resp.status_code, resp.url)
        print("Final destination:")
        url = response.url
        print(response.status_code, url)
        if del_params:
            url = del_url_params(url)
        return url
    else:
        print("Request was not redirected")
        return None


def evenspread(sequence, num):
    """Return specified number of items out of sequence eavenly

    - If num=1, then evenspread picks the first in the list,
    """
    length = float(len(sequence))
    for i in range(num):
        yield sequence[int(ceil(i * length / num))]


def computehash(stream, algorithm, length=None):
    """Compute hash of file using :attr:`algorithm`."""
    hashobj = hashlib.new(algorithm)
    for data in stream:
        hashobj.update(to_bytes(data))
    hash = hashobj.hexdigest()
    if length:
        hash = hash[:length]
    return hash


def youtube_id(url):
    """Return youtube id from a youtube link"""
    url_data = urlparse(url)
    query = parse_qs(url_data.query)
    try:
        yt_id = query["v"][0]
    except:
        log.error("Link is not a youtube video, maybe a playlist? %s" % url)
        return None
    return yt_id


def _isfile(f, hn=False):
    """Checks if file is a file, either locally or remotely."""
    cmd = ["file", "-b", f]
    if hn and not islocal(hn):
        cmd = ["ssh", hn] + cmd
    p1 = Popen(cmd, stdout=PIPE)
    out = p1.communicate()[0].decode("UTF-8")
    if "No such file" in out:
        return None
    elif "directory" in out:
        return False
    else:
        return True


def islocal(hn1):
    """Checks if the hostname is the local hostname"""
    hn2 = socket.gethostname()
    log.debug("hn1: %s hn2: %s" % (hn1, hn2))
    if hn1 in hn2 or hn2 in hn1:
        return True
    else:
        return False


def rsync(src, dst, exclude=list(), tor=False, rsync_args=None, strict=True, ssh_key=None, port=None):
    """Rsync wrapper with exclude and remote_host.

    If you need a remote host simply write e.g. as src `phserver01:/root/some_dir/`. Doesn't support keys with
    passphrases.
    """
    src = os.path.normpath(src)
    src = src + "/"
    torsocks = ["torsocks"] if tor else []
    if not rsync_args:
        rsync_args = ["-avHAXx"]
    ssh_args = list()
    if not strict:
        ssh_args.append("-o StrictHostKeyChecking=no")
    if port:
        ssh_args.append("-p %s" % port)
    if ssh_key:
        ssh_args.append("-i %s" % ssh_key)
    if ssh_args:
        rsync_args += ["-e", "ssh %s" % " ".join(ssh_args)]  # -e [specifies] the remote shell to use
    p1 = Popen(torsocks + ["rsync"] + rsync_args + exclude + [src, dst], stdout=PIPE)
    stdout = p1.communicate()[0].decode("UTF-8")
    log.info(stdout[:100])  # truncating string if it's too long
    log.info(p1.returncode)
    if p1.returncode != 0:
        log.error("Rsync error. sendmail")


def is_number(s):
    """Checks if given parameter is a number or not"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def find_mountpoint(path, hn=False):
    """Returns mountpoint from local or given remote system (requires ssh alias for hostname to be configured)."""
    cmd = ["findmnt", "-T", path, "-n", "-o", "TARGET"]
    log.debug("hn: %s, path %s" % (hn, path))
    if hn and not islocal(hn):
        cmd = ["ssh", hn] + cmd
        log.debug("cmd: %s" % str(cmd))
    p1 = Popen(cmd, stdout=PIPE, stderr=PIPE)
    path, err = p1.communicate()
    path = path.decode("UTF-8").strip()
    log.debug("err: %s" % err)
    log.info("mountpoint is: %s" % path)
    return path


def format_exception(e):
    """Usage:  except Exception as e: log.error(format_exception(e))"""
    exception_list = traceback.format_stack()
    exception_list = exception_list[:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))
    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    exception_str = exception_str[:-1]  # Removing the last \n
    return exception_str


def listdir_fullpath(d, match=[]):
    """List dirs in given directory with their fullpath."""
    if match:
        return [os.path.join(d, f) for f in os.listdir(d) if any(x in f for x in match)]
    else:
        return [os.path.join(d, f) for f in os.listdir(d)]


def listdir_fullpath_not(d, match=[]):
    """List dirs in given directory with their fullpath."""
    return [os.path.join(d, f) for f in os.listdir(d) if not any(x in f for x in match)]


def listdir_fullpath_not_shadowfile(d, prefix, d2=None):
    """List files in given directory that have not a shadow file with the given prefix.

    E.g. when the prefix is 307_432, then the shadow file of /a/example would be
    /a/307_432_example. If `d2 = b` then the shadowfile would be /b/307_432_example.
    """
    d3 = d2 if d2 else d
    return [
        os.path.join(d, f) for f in os.listdir(d) if not os.path.isfile(os.path.join(d3, "%s_%s" % (prefix, f)))
        and not prefix in f
        ]


def remote_file_content(hn, fn):
    """Returns files content UTF-8 decoded via ssh by the given hostname and filename."""
    log.info("content of %s:%s (hn:filename)" % (hn, fn))
    p1 = Popen(["ssh", "-tt", hn, "sudo", "cat", fn], stdout=PIPE)
    return p1.communicate()[0].decode("UTF-8").split("\n")


def try_func(func, *args, **kwargs):
    """Try except wrapper."""
    try:
        val = func(*args, **kwargs)
        return val
    except Exception as e:
        log.error(format_exception(e))
        return False


def similar(a, b):
    """Returns float from 0 to 1 of how similar two strings are."""
    return SequenceMatcher(None, a, b).ratio()


def mkdir_p(dirs):
    """Equivalent to linux command `mkdir -p`. Also accepts list of directories."""
    if isinstance(dirs, str):
        dirs = [dirs]
    elif isinstance(dirs, list):
        pass
    else:
        log.error("Pass a string or a list of strings to this function. Returning.")
        return
    for x in dirs:
        if not os.path.exists(x):
            try:
                os.makedirs(x)
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else:
                    log.error("Could not create directory")
                    pass
        else:
            log.info("Directory exists already.")


def umount(mp, lazy=False, fuser=False):
    """Umounts given mountpoint. Can umount also with lazy switch."""
    cmd_umount, cmd_lazy_umount = (["umount"], ["umount", "-l"])
    if fuser:
        cmd_umount, cmd_lazy_umount = (["fusermount", "-u"], ["fusermount", "-u", "-z"])
    cmd = cmd_lazy_umount if lazy else cmd_umount
    log.debug(cmd)
    p1 = Popen(cmd + [mp], stdout=PIPE, stderr=PIPE)
    out, err = p1.communicate()
    log.info("umount: out: %s, err: %s" % (out, err))
    log.info("Unmounted mp %s" % mp)


def mount(dev, mp):
    """Mounts a dev to mountpoint. If mp is occupied it'll try to umount first."""
    if os.path.ismount(mp):
        log.warning("Already mounted. Trying to unmount.")
        umount(mp)
        if os.path.ismount(mp):
            log.warning("Still mounted. Trying lazy unmount.")
            try_func(umount, mp, lazy=True)
            if os.path.ismount(mp):
                log.error("Couldn't be unmounted.")
                return False
    cmd_mount = ["mount", dev, mp]
    try:
        p1 = Popen(cmd_mount, stdin=PIPE)
        out, err = p1.communicate()
        log.debug("out: %s, err: %s" % (out, err))
        if p1.returncode == 0 and os.path.ismount(mp):
            log.info("Mounted %s to %s" % (dev, mp))
            return True
        else:
            log.error("Mounting failed. Error: %s\n%s" % (out, err))
            return False
    except Exception as e:
        log.error(format_exception(e))
        return False


def systemd_services_up(services):
    """Checks if given systems services are up, if not it exists."""
    for x in services:
        p = Popen(["systemctl", "is-active", x], stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        out = out.decode("utf-8").strip()
        if "failed" == out:
            log.info("Exiting, because dependent services are down: %s" % services)
            sys.exit()


def my_ip(proxies=None, timeout=6):
    kwargs = { "proxies": proxies } if proxies else {}
    url = 'http://myip.dnsomatic.com'
    try:
        r = requests.get(url, timeout, **kwargs)
    except:
        if has_gymail:
            send_mail(
                event="error",
                subject=os.path.basename(__file__),
                message="Download from %s failed. Site possibly down." % url
            )
        log.error("Download from %s failed. Site possibly down." % url)
        return None
    return r.text


def download(filename, download_link, timeout=6, proxies=None, tor=False, display_ip=False):
    """Download file from given download link to given local filename path.

    timeout := Nearly all production code should use this parameter in nearly all requests. Failure to do so can cause
               your program to hang indefinitely:
    """
    with open(filename, 'wb') as f:
        kwargs = {}
        if tor:
            log.debug("requests with tor enabled, using requests >=2.10 with socks5 support.")
            log.debug("Current IP: %s" % my_ip(proxies=tor_proxies))
            kwargs = { "proxies": tor_proxies }
        elif proxies:
            log.debug("Using custom proxies.")
            if display_ip:
                log.debug("Current IP: %s" % my_ip(proxies=proxies))
            kwargs = { "proxies": proxies }
        # Preventing exceptions when it times out due to temporary network issues
        # Try/Except is important here, because during network issues it will cause an exception.
        try:
            log.debug("Starting HTTP request to %s" % download_link)
            response = requests.get(download_link, timeout=timeout, stream=True, **kwargs)
        except:
            if has_gymail:
                send_mail(event="error", subject=os.path.basename(__file__),
                        message="Download from %s failed. Site possibly down." % download_link)
            log.error("Download from %s failed. Site possibly down." % download_link)
            return False
        try:
            if not response.ok:
                if has_gymail:
                    send_mail(event="error", subject=os.path.basename(__file__),
                            message="Download from %s failed. Site possibly down." % download_link)
                log.error("Download from %s failed. Site possibly down.")
                return False
            for block in response.iter_content(1024):
                f.write(block)
        except:
            if has_gymail:
                send_mail(event="error", subject=os.path.basename(__file__),
                        message="Download from %s failed. Site possibly down." % download_link)
            log.error("Download from %s failed. Site possibly down." % download_link)
            return False
    return True


def newest_dir(b='.'):
    """Returns newest (=last modified) directory of given path."""
    all_dirs = []
    for d in os.listdir(b):
        bd = os.path.join(b, d)
        if os.path.isdir(bd): all_dirs.append(bd)
    newest_dir = max(all_dirs, key=os.path.getmtime)
    return newest_dir


def handle_exceptions(fn):
    """Decorator for functions/methods to catch exceptions, apply with @handle_exception above method."""
    @wraps(fn)
    def wrapper(self, *args, **kw):
        try:
            return fn(self, *args, **kw)
        except Exception as e:
            log.error("Catched error with handle_exception decorator")
            log.error(format_exception(e))
    return wrapper


def multilog(only_first=False, **kwargs):
    """Convenience method, which prints the formated kwargs to log.debug(). If only_first is True, then only first
    element of a list is printed to the logs, though strings are still printed completely."""
    merged = str()
    for k, v in iteritems(kwargs):
        if only_first and isinstance(v, list):
            if v:
                v = v[0]
        m = "{0}: {1},".format(k, v)
        if len(m) > 80:
            m = "\n{0}\n".format(m)
        merged += m
    log.debug(merged)


def replace_all(text, d):
    """Allows you to replace multiple strings. It uses the key of the given dictionary d to match a string in the text
    and the associated value as replacement. E.g. d = {"hi": "bye", "no": "yes"} will replace hi with bye and no with
    yes."""
    for i, j in d.items():
        text = text.replace(i, j)
    return text


def createmongo(database, collection):
    """Connects to given database and returns specified collection."""
    client = MongoClient()
    db = getattr(client, database)
    collection = getattr(db, collection)
    return collection


def grep(path, match):
    """grep wrapper"""
    p1 = Popen(["grep", "-lR", match, path], stdout=PIPE)
    fn = p1.communicate()[0].decode("UTF-8").split()
    return fn


def find(path, match):
    """Simple wrapper around the linux command `find`

    Linux command find is faster than iterating over os.listdir().
    """
    p1 = Popen(["find", path, "-iname", "*%s*" % match], stdout=PIPE)
    fn = p1.communicate()
    fn = fn[0]
    fn = fn.decode("UTF-8").split()
    return fn


def rfind(path, rmatch, rexclude="", newest=False):
    """Regex match and exclude files using linux command `find`.

    Linux command `find` is faster than iterating over os.listdir().
    """
    p1 = Popen(["find", path, "-regex", rmatch, "-not", "-regex", rexclude], stdout=newest(stream))
    fns = p1.communicate()
    fns = fns[0]
    fns = fns.decode("UTF-8").split()
    if newest:
        fns = [max(fns , key=os.path.getctime)]
    return fns


def liget(l, idx, default=None):
    """Tries to get element of list by index, similar to dict.get(). If it fails it returns default"""
    try:
        return l[idx]
    except IndexError:
        return default


def isempty(fn, isfile=None):
    """Returns True if file is empty, if not empty False and if the file doesn't exist None."""
    try:
        res = (os.stat(fn).st_size == 0)
        if isfile:
            if os.path.isfile(fn):
                return res
        else:
            return res
    except:
        return None


def consecutive_comb(li):
    """Alternatively:
    for x, y in itertools.combinations(range(len(li) + 1), 2):
        yield li[x:y]
    """
    combs= list()
    for x in range(len(li)):
        for y in range(len(li)):
             z = li[x:y+1]
             if z:
                 combs.append(z)
    return combs


class DefaultOrderedDict(OrderedDict):
    """ Source: http://stackoverflow.com/a/6190500/562769"""

    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
           not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))

    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                               OrderedDict.__repr__(self))


def rchown(path, user, group):
    """Recursively chowns given path with given user/group"""
    p = Popen(["chown", "-R", "%s:%s" % (user, group), path], stdout=PIPE, stderr=PIPE)
    o, e = p.communicate()
    if e:
        log.error(e)


class Map(dict):
    """Extends the dictionary object, so that you can access the dictionary keys like attributes.

    Example: m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    Then you'd be able to access the dictionary as such: `person.age`. So it's a convenience class.
    Source: http://stackoverflow.com/a/32107024
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


def ismount_remote(host, path):
    """Checks if a directory is mounted on a host accessible with SSH.

    Alternatively with shlex.quote: ["ssh", host, "mountpoint {}".format(shlex.quote(path))])
    """
    status = subprocess.call(
        ["ssh", host, "mountpoint", path])
    if status == 0:
        return True
    if status == 1:
        return False
    raise Exception('SSH failed')


def prettydict(d, indent=0):
    """Print dictionary pretty"""
    for key, value in iteritems(d):
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent+1)
        else:
            print('\t' * (indent+1) + str(value))


def setlocals():
    """Gets your default locales and sets them for your current python instance.

    This is useful when you work with datetime.strptime and want to make use of %b.
    """
    my_locals = ".".join(locale.getdefaultlocale())
    locale.setlocale(locale.LC_TIME,(my_locals, my_locals))


def isup(host, port=22, timeout=60):
    """Check if port is available on host."""
    socket.setdefaulttimeout(10)
    timeout = time.time() + timeout
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
            log.info("Port %s on host %s is reachable." % (port, host))
            s.close()
            return True
        except socket.error as e:
            log.error("Error on connect: %s" % e)
            s.close()
        if time.time() > timeout:
            return False
        sleep(6)


def validate_ip(s):
    """Validate IPv4 address format."""
    a = s.split('.')
    if len(a) != 4:
        return None
    for x in a:
        if not x.isdigit():
            return None
        i = int(x)
        if i < 0 or i > 255:
            return None
    return s


class ResizeImg():

    def __init__(self, dest=None, imgdir=None, size=None):
        self.imgdir = imgdir
        self.dest = dest
        self.size = size

    def run_all(self):
        log.info("Resizing all files in %s" % self.imgdir)
        imgs = listdir_fullpath(self.imgdir)
        for x in imgs:
            self.resize(x, self.size)

    def resize(self, x, size):
        log.info("Resizing %s to %sx%s" % ((x,) + size))
        im = Image.open(x)
        if not self.dest:
            dirname = os.path.dirname(x)
        else:
            dirname = self.dest
        basename = os.path.basename(x)
        log.debug("Dirname of image %s" % dirname)
        log.debug("Basename of image %s" % basename)
        im.thumbnail(size, Image.ANTIALIAS)
        fn = os.path.join(dirname, "%s_%s_%s" % (size + (basename,)))
        try:
            im.save(fn)
            log.info("Saved %s" % fn)
            return fn
        except Exception as e:
            log.error(format_exception(e))
            log.error("Skipping resize. Traceback: %s" % format_exception(e))
            return None


def cosine_similarity(c1, c2):
    """Return the cosine similarity of two lists of strings."""
    c1 = Counter(c1)
    c2 = Counter(c2)
    terms = set(c1).union(c2)
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms)
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    return dotprod / (magA * magB)


def compare_permutations(a, b):
    """Find match between elements of two lists, no matter the permutation."""
    if any(x for x in itertools.permutations(a) if x in itertools.permutations(b)):
        return True
    else:
        return False
