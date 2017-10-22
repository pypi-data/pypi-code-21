import types
from gc import get_referrers as Referrers

from itertools import chain
from decorator import decorator
from datetime import datetime
import sys
import traceback

from peewee import SqliteDatabase, Model, JOIN, fn, OperationalError
from peewee import CharField, SmallIntegerField, DateTimeField
from peewee import ForeignKeyField, FloatField, TextField


PYSTAS_DB_ARG = '-pystasdb'
DB_FILENAME = 'pystas.db'
ALLOW_CUSTOM_DB = True

if ALLOW_CUSTOM_DB:
    if PYSTAS_DB_ARG in sys.argv:
        idx = sys.argv.index(PYSTAS_DB_ARG)
        sys.argv.pop(idx)
        DB_FILENAME = sys.argv.pop(idx)

DB = SqliteDatabase(DB_FILENAME)


@decorator
def retry(f, *args, **kw):
    while True:
        try:
            with DB.atomic():
                return f(*args, **kw)
        except OperationalError:
            e = sys.exc_info()[1]
            msg = e.message
            if not (msg.startswith("database is locked")):
                raise


class Compat:
    if sys.version_info[0] == 2:
        @staticmethod
        def get_code(f):
            return f.func_code

        @staticmethod
        def get_f_globals(f):
            return f.func_globals

        @staticmethod
        def get_f_name(f):
            return f.func_name

        @staticmethod
        def class_types():
            return (types.ClassType, types.TypeType)

        @staticmethod
        def class_from_method(m):
            return m.im_class

        @staticmethod
        def class_from_instance_method(m):
            return m.im_self
    else:
        @staticmethod
        def get_code(f):
            return f.__code__

        @staticmethod
        def get_f_globals(f):
            return f.__globals__

        @staticmethod
        def get_f_name(f):
            return f.__name__

        @staticmethod
        def class_types():
            return type

        @staticmethod
        def class_from_method(m):
            return m.__self__.__class__

        @staticmethod
        def class_from_instance_method(m):
            return m.__self__


class BaseModel(Model):
    @retry
    def save(self, *args, **kw):
        return super(BaseModel, self).save(*args, **kw)

    @classmethod
    @retry
    def get_or_create(cls, **kwargs):
        return super(BaseModel, cls).get_or_create(**kwargs)

    class Meta:
        database = DB


class PreFunctionSave:
    def __init__(self, module_name, name):
        self.name = name
        self.klass = None
        self.module = module_name

    @classmethod
    def For(cls, _function):
        _module = getattr(_function, '__module__', '')
        return cls(_module, Compat.get_f_name(_function))

    def getFunc(self, klass, arg_string):
        classname = None if klass is None else klass.__name__
        return Function.get_or_create(module=self.module, klass=classname,
                                      name=self.name, args=arg_string)


class Function(BaseModel):
    module = CharField(db_column='package')
    klass = CharField(db_column='class', null=True)  # actually, class's name..
    name = CharField(db_column='function')
    args = CharField(null=True)

    def __repr__(self):
        klass = '' if self.klass is None else self.klass+'.'
        args = ' (%s)' % self.args if self.args is not None else ''
        return '%s:%s%s%s' % (self.module, klass, self.name, args)


class Src(BaseModel):
    name = CharField(db_column='filename')
    line = SmallIntegerField()

    @classmethod
    def For(cls, _function):
        func_code = Compat.get_code(_function)
        name = getattr(func_code, 'co_filename', '')
        line = getattr(func_code, 'co_firstlineno', -1)
        ent, created = cls.get_or_create(name=name, line=line)
        return ent

    def __repr__(self):
        return '<%s:%d>' % (self.name, self.line)


class ProgExecution(BaseModel):
    start = DateTimeField()

    def __repr__(self):
        return '#%d' % self.id


class Errors(BaseModel):
    excep = CharField(db_column='Exception')
    error = TextField(db_column='Data')

    @classmethod
    def For(cls, exc):
        ent, create = cls.get_or_create(excep=exc.__class__.__name__,
                                        error=traceback.format_exc())
        return ent

    def __repr__(self):
        return self.excep


class Execution(BaseModel):
    function = ForeignKeyField(Function, related_name='executions')
    src = ForeignKeyField(Src, related_name='executions')
    prg = ForeignKeyField(ProgExecution, related_name='executions')
    start = DateTimeField(default=datetime.now)
    duration = FloatField(null=True)
    error = ForeignKeyField(Errors, related_name='executions', null=True)

    def __repr__(self):
        excp = '[%r]' % self.error if self.error else ''
        duration = self.duration if self.duration is not None else -1
        return '%s| %3.02fs. %s %s' % (self.prg, duration, self.function, excp)


ExecutionStart = None


class Pistas(object):
    # noinspection PyUnusedLocal
    @staticmethod
    def save_1_arg(is_func, args, kw):
        _args = args if is_func else args[1:]
        return repr(_args[0])

    @staticmethod
    def save_all_args(is_func, args, kw):
        _args = args if is_func else args[1:]
        return repr((_args, kw))[1:-1]

    @staticmethod
    def function_check_name(suspect_name, name):
        return name == suspect_name or suspect_name.endswith('.' + name)

    @classmethod
    def search_class(cls, where, classname):
        for name, obj in where.items():
            if cls.function_check_name(name, classname):
                yield obj

    @classmethod
    def get_class(cls, f, args):
        fname = f.dbfunc.name
        guessed_classname = f.guessed_classname
        if len(args) > 0:
            call_self = args[0]
            bound = getattr(call_self, fname, None)
            if bound is not None:
                if isinstance(call_self, Compat.class_types()):
                    # first arg is a class, so it's a class method..
                    return Compat.class_from_instance_method(bound)
                return Compat.class_from_method(bound)

        # else..
        if guessed_classname == "<module>":
            return
        for candidate_class in chain(
                cls.search_class(Compat.get_f_globals(f), guessed_classname),
                cls.hard_class_search(f, guessed_classname)):
            method = getattr(candidate_class, fname, None)
            if method is None:
                continue
            if cls.function_check(method, f):
                return candidate_class

    @staticmethod
    def function_check(suspect_f, wrapped_f):
        return suspect_f.f == wrapped_f

    @classmethod
    def hard_class_search(cls, func, _name):
        _already = set()
        frames = (x for x in Referrers(func) if isinstance(x, types.FrameType))
        for frame in frames:
            while frame is not None:
                if frame in _already:
                    frame = frame.f_back
                    continue
                if False:  # two version of same code..
                    for d in [frame.f_globals, frame.f_locals]:
                        for name, obj in d.items():
                            if cls.function_check_name(name, _name):
                                yield obj
                else:
                    # looks like we only require to inspect f_locals
                    for name, obj in frame.f_locals.items():
                        if cls.function_check_name(name, _name):
                            yield obj
                    # for name, obj in frame.f_globals.items():
                    #     if cls.function_check_name(name, _name):
                    #         yield obj
                frame = frame.f_back
                _already.add(frame)

    @classmethod
    def log(cls, f, fargs=lambda have_self, args, kw: None):
        f.dbsrc = Src.For(f)
        f.dbfunc = PreFunctionSave.For(f)
        f.fargs = fargs

        guess = traceback.extract_stack()[-2]
        f.guessed_classname = guess[2]

        def decorated(*args, **kw):
            klass = cls.get_class(f, args)
            x, _ = f.dbfunc.getFunc(klass, f.fargs(klass is None, args, kw))
            x.save()
            execution = Execution(function=x, src=f.dbsrc, prg=ExecutionStart)
            execution.save()
            try:
                return f(*args, **kw)
            except Exception:
                exc = sys.exc_info()[1]
                execution.error = Errors.For(exc)
                execution.save()
                raise
            finally:
                end = datetime.now()
                execution.duration = (end-execution.start).total_seconds()
                execution.save()
        decorated.f = f
        return decorated

    def __init__(self):
        raise RuntimeError("No instances of this class are required!")


logpista = Pistas.log
logw1arg = lambda f: Pistas.log(f, Pistas.save_1_arg)
logwargs = lambda f: Pistas.log(f, Pistas.save_all_args)


@retry
def init():
    try:
        DB.create_tables([Function, Src, Execution, Errors, ProgExecution])
    except OperationalError:
        e = sys.exc_info()[1]
        msg = str(e)  # .message
        if not (msg.startswith("table ") and msg.endswith(" already exists")):
            raise


if not __name__ == "__main__":
    # loaded as helper module..
    init()
    ExecutionStart = ProgExecution(start=datetime.now())
    ExecutionStart.save()
else:
    from texttable import Texttable

    def get_last_exec():
        for prgexec in ProgExecution.select().order_by(
                ProgExecution.start.desc()).limit(1):
            return prgexec

    def ts(sec):
        m = 60
        h = 60*m
        d = 24*h
        if sec<60:
            return '%.02fs'%sec
        _d, _sec = divmod( sec, d)
        _h, _sec = divmod( _sec, h)
        _m, _sec = divmod( _sec, m)
        _s, _sec = divmod( _sec, 1)
        r = ''
        for c, s in zip([_d,_h,_m,_s], 'dhms'):
            if c==0:
                continue
            n = '%d%c'%(c,s)
            if r=='':
                r = n
            else:
                r += ' '+n
                return r
        if _sec!=0:
            s = '%.02fs' % _sec
            if s[0]=='0': s=s[1:]
            s = ' '+s
        else:
            s=''
        return r+s

    def show_stats(condition, title):
        print("")
        print(title)
        table = Texttable(100)
        table.set_deco(Texttable.HEADER)
        table.set_chars(['', '', '+', '-'])
        table.set_cols_dtype(['i', 'i', ts, ts, 't'])
        table.set_cols_align(["r", "r", "r", "r", "l"])
        table.header(['calls', 'excp.', 't.total', 'media', 'function'])
        table.set_precision(2)
        total = fn.SUM(Execution.duration)
        for _function in Function.select(Function,
                                         fn.Count(Execution.id).alias('count'),
                                         total.alias('total'),
                                         fn.Count(Errors.id).alias('errors'),
                                         ).join(Execution
                                         ).join(Errors, JOIN.LEFT_OUTER
                                         ).where(
                                         condition).group_by(Function
                                         ).order_by(-total):
            table.add_row([_function.count, _function.errors, _function.total,
                _function.total / _function.count, _function
            ])
        print(table.draw())


    # loaded as executable..
    lastprg = get_last_exec()
    print('last execution is: %r started: %s complete dump:' % (lastprg,
                                                                lastprg.start))
    for _execution in Execution.select(
                        ).where(Execution.prg == lastprg
                        ).order_by(Execution.start.desc()):
        print(_execution)

    show_stats(Function.id == Function.id, "all-history")
    show_stats(Execution.prg == lastprg, "last-exec")
