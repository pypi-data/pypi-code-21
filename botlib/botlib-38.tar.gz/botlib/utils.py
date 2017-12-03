# BOTLIB Framework to program bots
#
# botlib/utils.py
#
# Copyright 2017 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" lib local helper functions. """

from .error import ENODATE
from .trace import get_exception
from .static import basic_types, histfile, resume, year_formats, monthint, bdmonths, dirmask, filemask

import rlcompleter
import datetime
import readline
import optparse
import _thread
import termios
import hashlib
import logging
import string
import random
import atexit
import botlib
import shutil
import time
import types
import stat
import json
import sys
import re
import os
import os.path

def expect(s, l):
    """ scan list for matched on string. """
    for i in l:
        if type(i) in [[], ()]:
            for ii in i:
                if s in ii:
                    yield ii
        if s in str(i):
            return True
    return False

def get_name(name):
    """ return a variable value, used in tests. """
    from botlib.template import varnames
    n = varnames.get(name, None)
    if not n:
        n = randomname()
    return n

def randomname():
    """ return a random value. """
    s = ""
    for x in range(8):
        s += random.choice(string.printable)
    return s

def high(target, file_name):
    """ get the newest of filenames ending in the highest .digit. """
    highest = 0
    for i in os.listdir(target):
        if file_name in i:
            try:
                seqnr = i.split('.')[-1]
            except IndexError:
                continue
            try:
                if int(seqnr) > highest:
                    highest = int(seqnr)
            except ValueError:
                pass
    return highest

def highest(target, filename):
    """ return the file with the highest filename ending (after the last . there is supposed to be a digit. """
    nr = high(target, filename)
    return "%s.%s" % (filename, nr+1)

def locatedir(path, match=""):
    """ locate subdirectory of path. """
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if root == path:
                continue
            if match and match not in d:
                continue
            yield root

def copydir(orig, dest):
    """ copy directory from orig to destination. """
    for root, dirs, files in os.walk(orig):
        for d in dirs:
            if root == orig:
                continue
            nr = copydir(dir, os.path.join(dest, d))
            counter = 0
            for fn in files:
                shutil.copy(os.path.join(root, d, fn), os.path.join(dest, fn))
                yield fn

def smooth(obj):
    """ return a JSON representation of an object. """
    if type(obj) not in basic_types:
        return repr(obj)
    return obj

def make_signature(obj):
    """ make an signature based on the values of an object. """
    data = json.dumps(obj, indent=4, ensure_ascii=True, sort_keys=True)
    return str(hashlib.sha1(bytes(str(data), "utf-8")).hexdigest())

def verify_signature(obj, signature):
    """ verify an object's integrty based on the object's signature. """
    signature2 = make_signature(obj)
    return signature2 == signature

def split_txt(what, l=375):
    """ split text into <l> sized portions """
    txtlist = []
    start = 0   
    end = l     
    length = len(what)
    for i in range(int(length/end) + 1):
        endword = what.find('\n', end)
        if not endword:
            endword = what.find(' ', end)
        if endword == -1:
            endword = start + l
        res = what[start:endword]
        if res:
            txtlist.append(res)
        start = endword
        end = start + l
    return txtlist

def cdir(path):
    """ create a directory. """
    res = ""
    for p in path.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass
        except OSError as ex:
            logging.error(get_exception())
    return True

def strip_html(text):
    """ strip html markup code. """
    if text.startswith("http"):
        return text
    import bs4
    soup = bs4.BeautifulSoup(text, "lxml")
    res = ""
    for chunk in soup.findAll(text=True):
        if isinstance(chunk, bs4.CData): res += str(chunk.content[0]) + " "
        else: res += str(chunk) + " "
    return res

def stripped(jid):
    """ strip trailing part of a JID, the part after the / """
    try:
        return str(jid).split("/")[0]
    except:
        return str(jid)

def userhost(u):
    """ strip the nick name of an IRC users ident. """
    try:
        return str(u).split("!")[-1]
    except:
        return str(u)

def parse_cli(*args, **kwargs):
    """ parse the command line options. """
    from .object import Config
    from .options import opts_defs
    opts, arguments = make_opts(opts_defs)
    cfg = Config()
    cfg.template("kernel")
    cfg.args = arguments
    cfg.merge(vars(opts))
    return cfg

def termsetup(fd):
    """ preserve the old terminal attributes. """
    old = termios.tcgetattr(fd)
    return old

def termreset(fd, old):
    """ reset the terminale to previous serssion attributes. """
    termios.tcsetattr(fd, termios.TCSADRAIN, old)

class Completer(rlcompleter.Completer):

    """ Completer class used to complete bot commands. """

    def __init__(self, options):
        super().__init__()
        self.options = options

    def complete(self, text, state):
        """ the complete function itself. """
        if state == 0:
            if text:
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        try:
            return self.matches[state]
        except IndexError:
            return None

def set_completer(optionlist):
    """ set the completer as part of readline functionality. """
    readline.parse_and_bind("tab: complete")
    completer = Completer(optionlist)
    readline.set_completer(completer.complete)
    atexit.register(lambda: readline.set_completer(None))

def enable_history():
    """ enable history written to file. """
    if not os.path.exists(histfile):
        d, f = os.path.split(histfile)
        cdir(d)
        touch(histfile)
    readline.read_history_file(histfile)
    atexit.register(close_history)

def close_history():
    """ write the command history to file. """
    readline.write_history_file(histfile)

def reset():
    """ reset the terminal. """
    close_history()
    if "old" in resume:
        termreset(resume["fd"], resume["old"])

def startup():
    """ function to call on startup of the program, preserving previous terminal settings. """
    global resume
    resume["fd"] = sys.stdin.fileno()
    resume["old"] = termsetup(sys.stdin.fileno())
    atexit.register(reset)

def make_opts(options, args=None, usage="bot [options]"):
    """" create options to check when command line is parsed. """
    parser = optparse.OptionParser(usage=usage, version=str(botlib.__version__))
    for option in options:
        optiontype, default, dest, helptype = option[2:]
        if "store" in optiontype:
            try:
                parser.add_option(option[0], option[1], action=optiontype, default=default, dest=dest, help=helptype)
            except Exception as ex:
                logging.error("%s option %s" % (str(ex), option))
                continue
        else:
            try:
                parser.add_option(option[0], option[1], type=optiontype, default=default, dest=dest, help=helptype)
            except Exception as ex:
                logging.error("^%s option %s" % (str(ex), option))
                continue
    if args:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args(args)
    return args

def reboot():
    """ perform a reboot. """
    os.execl(sys.argv[0], *(sys.argv + ["-r", "-z"]))

def name(obj):
    """ return the name destilled from the repr of an object. """
    txt = repr(obj)
    return fromstring(txt)

def fromstring(txt):
    """ derive an object from the repr string ."""
    if " at " in txt:
        txt = txt.split(" at ")[0]
    #if " object " in txt:
    #    txt = txt.split(" object ")[0]
    #elif "bound method" in txt:
    #    txt = txt.split("bound method")[1].split()[0]
    if " of " in txt:
        t1, t2 = txt.split(" of ")
        txt = t2.split(".")[-1] + "." + t1.split(".")[-1]
    #if " from " in txt:
    #    txt = txt.split(" from ")[0].split()[1][1:-1]
    if "," in txt:
        txt = txt.split(",")[0]
    txt = txt.replace("<function ", "")
    return txt.strip()

def pname(obj):
    """ just return the repr string of an object. """
    return repr(obj)

def sname(obj):
    """ return the name after the last dot. """
    return tname(obj).split(".")[-1]

def tname(obj):
    """ function to return a printable string of threads. """
    return name(obj).split("(")[-1]

def n(obj):
    """" use __class___ to return a named string of an object. """
    return str(obj.__class__).split()[-1].split(".")[-1][:-2].lower()

def pathname(p):
    """ return that part of a pathname that tails the working directory. """
    from .space import cfg
    d = cfg.workdir.split(os.sep)[-1]
    return d + p.split(cfg.workdir)[-1]

def fn_time(daystr):
    """ determine the time used in a BOTLIB filename. """
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.split(".")[0]
    try:
        t = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
    except ValueError:
        t = 0
    return t

def now():
    """ turn a datetime string of the current time. """
    return str(datetime.datetime.now())

def rtime():
    """ return a filestamp usable in a filename. """
    res =  str(datetime.datetime.now()).replace(" ", os.sep)
    return res

def spath(path):
    return os.sep.join(path.split(os.sep)[-3:])

def hms():
    """ return hour:minutes:seconds of toda=y. """
    return str(datetime.datetime.today()).split()[1].split(".")[0]

def day():
    """" return the current day. """
    return str(datetime.datetime.today()).split()[0]

def year():
    """ return the year we are living in. """
    return str(datetime.datetime.now().year)

def get_hour(daystr):
    """ get the hour from the string provided. """
    try:
        hmsre = re.search(r'(\d+):(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmsre.group(1)))
        hoursmin = hours  + int(hmsre.group(2)) * 60
        hms = hoursmin + int(hmsre.group(3))
    except AttributeError:
        pass
    except ValueError:
        pass
    try:
        hmre = re.search(r'(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmre.group(1)))
        hms = hours + int(hmre.group(2)) * 60
    except AttributeError:
        return 0
    except ValueError:
        return 0
    return hms

def get_time(txt):
    """ get time from a string containing day and/or hour. """
    try:
        target = get_day(txt)
    except ENODATE:
        target = to_day(day())
        hour = get_hour(txt)
        if hour:
            target += hour
    return target

def parse_time(txt):
    """" parse a string for a time mentioned. also parse for a diff in seconds. """
    seconds = 0
    target = 0
    txt = str(txt)
    for word in txt.split():
        if word.startswith("+"):
            seconds = int(word[1:])
            return time.time() + seconds
        if word.startswith("-"):
            seconds = int(word[1:])
            return time.time() - seconds
    if not target:
        try:
            target = to_time(txt)
        except ENODATE:
            target = to_day(day())
            hour = get_hour(txt)
            if hour:
                target += hour
    return target

def extract_time(daystr):
    """ use standard time timeformats to extract a time from a string. """
    for f in year_formats:
        try:
            res = time.mktime(time.strptime(daystr, f))
        except:
            res = None
        if res:
            return res

def to_day(daystring):
    """ try to detect a time in a string. """
    previous = ""
    line = ""
    daystr = str(daystring)
    for word in daystring.split():
        line = previous + " " + word
        previous = word
        try:
            res = extract_time(line.strip())
        except ValueError:
            res = None
        if res:
            return res
        line = ""

def to_time(daystr):
    """
         convert time/date string to a unix timestamp

         example: 2016-08-29 16:34:23.837288
         example: Sat Jan 14 00:02:29 2017

         example: 2017-07-05t22:00:00+00:00

    """
    daystr = str(daystr)
    daystr = daystr.split(".")[0]
    daystr = daystr.replace("GMT", "")
    daystr = daystr.replace("_", ":")
    daystr = " ".join([x.capitalize() for x in daystr.split() if not x[0] in ["+", "-"]])
    res = 0
    splitted = daystr.split(" ")
    dstr = ""
    for i in splitted:
        if "-" in i:
            dstr += i + " "
        if ":" in i:
            dstr += i
    daystr = dstr
    try:
        res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S"))
    except:
        pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S %z"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S %z"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %d %b %H:%M:%S %Y"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %b %d %H:%M:%S %Y"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %d %b %H:%M:%S %Y %z"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d %m %Y"))
        except:
            pass
    if not "-" in daystr:
        raise ENODATE(daystr)
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%d %H:%M:%S"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d-%m-%Y %H:%M:%S"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d-%m-%Y %H:%M"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%d %H:%M"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%d"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d-%m-%Y"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%dt%H:%M:%S+00:00"))
        except:
            pass
    if not res:
        raise ENODATE(daystr)
    return res

def file_time(timestamp):
    """ return a pseudo random time on today's start of the day. """
    return str(datetime.datetime.fromtimestamp(timestamp)).replace(" ", os.sep) + "." + str(random.randint(111111, 999999))

def to_date(*args, **kwargs):
    """ convert to date. """
    if not args:
        return None
    date = args[0]
    if not date:
        return None
    date = date.replace("_", ":")
    res = date.split()
    ddd = ""
    try:
        if "+" in res[3]:
            raise ValueError
        if "-" in res[3]:
            raise ValueError
        int(res[3])
        ddd = "{:4}-{:#02}-{:#02} {:6}".format(res[3], monthint[res[2]], int(res[1]), res[4])
    except (IndexError, KeyError, ValueError):
        try:
            if "+" in res[4]:
                raise ValueError
            if "-" in res[4]:
                raise ValueError
            int(res[4])
            ddd = "{:4}-{:#02}-{:02} {:6}".format(res[4], monthint[res[1]], int(res[2]), res[3])
        except (IndexError, KeyError, ValueError):
            try:
                ddd = "{:4}-{:#02}-{:02} {:6}".format(res[2], monthint[res[1]], int(res[0]), res[3])
            except (IndexError, KeyError):
                try:
                    ddd = "{:4}-{:#02}-{:02}".format(res[2], monthint[res[1]], int(res[0]))
                except (IndexError, KeyError):
                    try:
                        ddd = "{:4}-{:#02}".format(res[2], monthint[res[1]])
                    except (IndexError, KeyError):
                        try:
                            ddd = "{:4}".format(res[2])
                        except (IndexError, KeyError):
                            ddd = ""
    return ddd

def elapsed(seconds, short=True):
    """ return a string showing the elapsed days, hours, minutes, seconds. """
    txt = ""
    sub = str(seconds).split(".")[-1]
    nsec = float(seconds)
    year = 365*24*60*60
    week = 7*24*60*60
    day = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    days = int(nsec/day)
    nsec -= days*day
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    sec = nsec - minutes*minute
    if years:
        txt += "%sy" % years
    if weeks:
        days += weeks * 7
    if days:
        txt += "%sd" % days
    if years and short and txt:
        return txt
    if hours:
        txt += "%sh" % hours
    if days and short and txt:
        return txt
    if minutes:
        txt += "%sm" % minutes
    if hours and short and txt:
        return txt
    if sec == 0:
        txt += "0s"
    elif sec < 1 or not short:
        txt += "%.3fs" % sec
    else:
        txt += "%ss" % int(sec)
    txt = txt.strip()
    return txt

def today():
    """" return the day of a filename. """
    t = rtime().split(".")[0]
    ttime = time.strptime(t, "%Y-%m-%d/%H:%M:%S")
    result = time.mktime(ttime)
    return result

def get_day(daystring):
    """ get the day from the string provided. """
    day = 0
    try:
        ymdre = re.search(r'(\d+)-(\d+)-(\d+)', daystring)
        if ymdre:
            (year, month, day) = ymdre.groups()
    except:
        try:
            ymre = re.search(r'(\d+)-(\d+)', daystring)
            if ymre:
                (year, month) = ymre.groups()
                day = 1
        except:
            raise ENODATE(daystring)
    if not day:
        raise ENODATE(daystring)
    day = int(day)
    month = int(month)
    year = int(year)
    date = "%s %s %s" % (day, bdmonths[month], year)
    return time.mktime(time.strptime(date, "%d %b %Y"))

def urled(obj):
    """ return a url for the object so it can be fetched with the REST service. """
    from .space import cfg
    p = get_path(obj)
    p = p.split(cfg.workdir)[-1]
    return "http://%s:%s%s" % (cfg.hostname or "localhost", cfg.port, p)

def root():
    """ return the root directory. """
    from .space import cfg
    path = cfg.workdir
    path = os.path.abspath(path)
    check_permissions(path)
    return path

def days(obj):
    """ calculate the time passed since an object got logged. """
    t1 = time.time()
    #t2 = dated(object)
    t2 = timed(obj)
    if t2:
        time_diff = float(t1 - t2)
        return elapsed(time_diff)

def dated(obj):
    """ fetch the date from an object. """
    res = ""
    if "_container" in obj:
        obj = obj._container
    if not res:
        res = getattr(obj, "Date", None)
    if not res:
        res = getattr(obj, "date", None)
    if not res:
        res = getattr(obj, "published", None)
    if not res:
        res = getattr(obj, "added", None)
    if not res:
        res = getattr(obj, "saved", None)
    if not res:
        res = getattr(obj, "timed", None)
    if not res:
        raise ENODATE(res)
    return res

def timed(obj):
    """ calculated the time of an object. """
    try:
        return fn_time(obj._container.path)
    except:
        try:
            return fn_time(rtime())
        except:
            pass
    try:
        d = dated(obj._container)
    except (AttributeError, ENODATE):
        try:
            d = dated(obj)
        except ENODATE:
            d = None
    if d:
        try:
            return to_time(d)
        except ENODATE:
            pass

def get_path(obj):
    """ Return the path used to store the object's json dump. """
    try:
        return obj._container.path
    except:
        pass

def get_saved(obj):
    """ return the saved attribue of an object. """
    p = ""
    if "_container" in obj:
        p = getattr(obj._container, "saved", "")
        if p:
            return p

def check_permissions(p, dirmask=dirmask, filemask=filemask):
    """ set permission of the data dir to 0x700 or use provided dirmask/filemask. """
    uid = os.getuid()
    gid = os.getgid()
    try:
        stats = os.stat(p)
    except FileNotFoundError:
        return
    except OSError:
        d, fn = os.path.split(p)
        cdir(d)
        stats = os.stat(d)
    if stats.st_uid != uid:
        os.chown(p, uid, gid)
    if os.path.isfile(p):
        mask = filemask
    else:
        mask = dirmask
    m = oct(stat.S_IMODE(stats.st_mode))
    if m != oct(mask):
        os.chmod(p, mask)

def touch(fname):
    """ touch a file. """
    try:
        fd = os.open(fname, os.O_RDONLY | os.O_CREAT)
        os.close(fd)
    except TypeError:
        pass
    except Exception as ex:
        logging.error(get_exception())
