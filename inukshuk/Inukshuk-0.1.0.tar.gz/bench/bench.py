import os.path
import sys
import math
import time
import argparse
import platform
import importlib.util
import yaml
import colorama


bench_base_dir = os.path.dirname(__file__)


class BenchmarkRunner:
    def __init__(self, times=1):
        self.times = times
        self._active = False
        self._left_col_width = 30
        self._rank_bar_width = 30
        self._results = []

    def __enter__(self):
        self._beforeFirstRun()
        self._active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val

        self._report()
        self._active = False

    def run(self, bench_name, func):
        if not self._active:
            raise Exception("The benchmark runner is not active.")

        elapsed = []

        for i in range(self.times):
            start_t = time.perf_counter()
            func()
            end_t = time.perf_counter()
            elapsed.append(end_t - start_t)

        med = elapsed[int(math.floor(float(len(elapsed)) / 2.0))]
        self._results.append([bench_name, med, elapsed])

    def _beforeFirstRun(self):
        width = self._left_col_width
        uname = platform.uname()
        sys_info = [
            ("python", platform.python_version()),
            ("python executable", sys.executable),
            ("platform", platform.platform()),
            ("machine", uname.node)
        ]
        for i in sys_info:
            print('%s: %s' % (i[0].ljust(width), i[1]))

        print()
        print("Bench output >>>>>>>>>>>>>>")
        print(colorama.Style.DIM)

    def _report(self):
        width = self._left_col_width
        total_width = self._left_col_width + self._rank_bar_width

        print(colorama.Style.NORMAL)
        print("<<<<<<<<<<<<<< Bench output")

        print()

        print('%s  %s' % ("# Bench".ljust(width), "# Time"))
        sorted_results = sorted(self._results, key=lambda r: r[1])
        for name, med, _ in sorted_results:
            print('%s: %8.6fs' %
                  (name.ljust(width), med))

        if len(sorted_results) > 1:
            print()
            print("# Ranking (first is best):")
            min_med = sorted_results[0][1]
            max_med = sorted_results[-1][1]
            for name, med, _ in sorted_results:
                bar_len = int(
                    self._rank_bar_width *
                    (med - min_med) / (max_med - min_med))
                print('%s: %s' % (name.ljust(width), bar_len * '*'))

        if self.times > 1:
            print()
            print(total_width * '=')

            for name, med, elapsed in sorted_results:
                print()
                print('# ' + name)

                min_elapsed = min(elapsed)
                max_elapsed = max(elapsed)
                variance = max_elapsed - min_elapsed
                avg = sum(elapsed) / len(elapsed)
                print('%s: %8.6fs' % ('Median'.ljust(width), med))
                print('%s: %8.6fs' % ('Average'.ljust(width), avg))
                print('%s: %8.6fs' % ('Variance'.ljust(width), variance))

                if variance == 0:
                    continue

                for i, e in enumerate(sorted(elapsed)):
                    print('%s: %8.6fs' % (('  #%d' % i).ljust(width), e))

                run_bar_len = self._left_col_width + self._rank_bar_width
                scale = float(run_bar_len) / variance
                if avg < med:
                    min_to_avg = avg - min_elapsed
                    avg_to_med = med - avg
                    med_to_max = max_elapsed - med
                    segments = [
                        ('a', int(min_to_avg * scale)),
                        ('m', int(avg_to_med * scale)),
                        int(med_to_max * scale)
                    ]
                else:
                    min_to_med = med - min_elapsed
                    med_to_avg = avg - med
                    avg_to_max = max_elapsed - avg
                    segments = [
                        ('m', int(min_to_med * scale)),
                        ('a', int(med_to_avg * scale)),
                        int(avg_to_max * scale)
                    ]
                run_bar = '['
                run_bar += segments[0][1] * '-'
                run_bar += segments[0][0]
                run_bar += segments[1][1] * '-'
                run_bar += segments[1][0]
                run_bar += segments[2] * '-'
                run_bar += ']'
                print(run_bar)

        print()


class _ArgForOne:
    def __init__(self, args):
        self.reuse = False
        self.num_loops = 1
        self._args = args

    def __getattr__(self, name):
        return getattr(self._args, name)


def main():
    colorama.init()

    bench_engines = list(bench_functions.keys())
    bench_engines.remove('empty')

    parser = argparse.ArgumentParser(
        description='Benchmark Utility for Inukshuk')
    parser.add_argument('bench_name')
    parser.add_argument('-n', '--num-loops', default=100, type=int)
    parser.add_argument('-t', '--num-times', default=1, type=int)
    parser.add_argument('-e', '--engine', default=None,
                        action='append', choices=bench_engines)
    parser.add_argument('--reuse', action='store_true')
    parser.add_argument('--inuk-compiled', action='store_true')
    parser.add_argument('--hard-join', action='store_true')
    args = parser.parse_args()

    if not args.bench_name:
        print("Please specify a benchmark name. Possible names:")
        for n in os.listdir(bench_base_dir):
            if os.path.isdir(os.path.join(bench_base_dir, n)):
                print(n)
        print("")
        return

    bench_dir = os.path.join(bench_base_dir, args.bench_name)
    if not os.path.isdir(bench_dir):
        raise Exception("No such benchmark: %s" % args.bench_name)

    print("Loading context data...")
    with open(os.path.join(bench_dir, 'context.yaml')) as f:
        data = yaml.load(f)

    all_engines = bench_engines
    all_engines.append('empty')
    # Quik doesn't seem to work.
    # (see https://github.com/avelino/quik/issues/9)
    all_engines.remove('quik')

    engines = args.engine or all_engines

    runner = BenchmarkRunner(times=args.num_times)
    with runner:
        for e in engines:
            bench_func = bench_functions[e]
            assert bench_func

            print("Generating %s template..." % e)
            try:
                filename, tpl_text = generate_template(args.bench_name, e)
            except OSError:
                print("No templates for engine '%s'... skipping." % e)
                continue

            print("Rendering %s templates..." % e)

            out_path = os.path.join(
                bench_dir, 'output', 'bench_%s.output.html' % e)
            if not os.path.isdir(os.path.dirname(out_path)):
                os.makedirs(os.path.dirname(out_path))

            args_for_one = _ArgForOne(args)
            output = bench_func(filename, tpl_text, data, args_for_one)
            with open(out_path, 'w') as f:
                f.write(output)

            def render():
                bench_func(filename, tpl_text, data, args)

            runner.run(e, render)


def generate_template(bench_name, engine):
    tpl_text = ''
    tpl_name = 'bench_%s.html' % engine
    bench_dir = os.path.join(bench_base_dir, bench_name)
    tpl_dir = os.path.join(bench_dir, 'templates')
    with open(os.path.join(tpl_dir, '_header.html'), 'r') as f:
        tpl_text += f.read()
    with open(os.path.join(tpl_dir, tpl_name), 'r') as f:
        tpl_text += f.read()
    with open(os.path.join(tpl_dir, '_footer.html'), 'r') as f:
        tpl_text += f.read()

    gen_dir = os.path.join(bench_dir, 'generated')
    filename = os.path.join(gen_dir, 'bench_%s.generated.html' % engine)
    if not os.path.isdir(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, 'w') as f:
        f.write(tpl_text)

    return filename, tpl_text


def bench_empty(filename, tpl_text, data, args):
    for i in range(args.num_loops):
        output = tpl_text
    return output


def bench_hardcoded(filename, tpl_text, data, args):
    module_name = 'bench_hardcoded.py'
    bench_dir = os.path.join(bench_base_dir, args.bench_name)
    module_path = os.path.join(bench_dir, module_name)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    if args.hard_join:
        func = getattr(module, 'render_join')
    else:
        func = getattr(module, 'render_io')
    for i in range(args.num_loops):
        output = func(data)
    return output


def bench_inukshuk(filename, tpl_text, data, args):
    bench_dir = os.path.join(bench_base_dir, args.bench_name)
    sys.path.append(os.path.dirname(bench_base_dir))
    import inukshuk
    import inukshuk.loader
    from inukshuk.rendering import DICT_FIRST_ACCESS
    compiled_path = None
    if args.inuk_compiled:
        compiled_path = os.path.join(bench_dir, 'output',
                                     'bench_inukshuk.tpl.py')
    gen_dir, n = os.path.split(filename)
    if args.reuse:
        e = inukshuk.Engine(loader=inukshuk.loader.FileSystemLoader([
            gen_dir, os.path.join(bench_dir, 'templates')]))
        e.access_mode = DICT_FIRST_ACCESS
        tpl = e.getTemplate(n, compiled=args.inuk_compiled)
        tpl._compiled_module_filename = compiled_path
        for i in range(args.num_loops):
            output = tpl.render(data)
    else:
        for i in range(args.num_loops):
            e = inukshuk.Engine(loader=inukshuk.loader.FileSystemLoader([
                gen_dir, os.path.join(bench_dir, 'templates')]))
            e.access_mode = DICT_FIRST_ACCESS
            tpl = e.getTemplate(n, compiled=args.inuk_compiled)
            tpl._compiled_module_filename = compiled_path
            output = tpl.render(data)
    return output


def bench_jinja2(filename, tpl_text, data, args):
    bench_dir = os.path.join(bench_base_dir, args.bench_name)
    import jinja2
    gen_dir, n = os.path.split(filename)
    if args.reuse:
        e = jinja2.Environment(loader=jinja2.FileSystemLoader([
            gen_dir, os.path.join(bench_dir, 'templates')]))
        tpl = e.get_template(n)
        for i in range(args.num_loops):
            output = tpl.render(**data)
    else:
        for i in range(args.num_loops):
            e = jinja2.Environment(loader=jinja2.FileSystemLoader([
                gen_dir, os.path.join(bench_dir, 'templates')]))
            tpl = e.get_template(n)
            output = tpl.render(**data)
    return output


def bench_tenjin(filename, tpl_text, data, args):
    global escape, to_str  # Yay Tenjin
    import tenjin
    from tenjin.helpers import escape, to_str  # NOQA
    if args.reuse:
        engine = tenjin.Engine(cache=True)
        for i in range(args.num_loops):
            output = engine.render(filename, data)
    else:
        for i in range(args.num_loops):
            engine = tenjin.Engine(cache=False)
            output = engine.render(filename, data)
    return output


def bench_wheezy(filename, tpl_text, data, args):
    from wheezy.template.engine import Engine
    from wheezy.template.ext.core import CoreExtension
    from wheezy.template.loader import DictLoader

    def conv(i):  # Yay Wheezy
        return str(i)

    def inc_rowno():
        data['rowno'] += 1
        return ''

    def is_odd_row():
        return data['rowno'] % 2 != 0

    loader = DictLoader({'t': tpl_text})
    data['tostr'] = conv
    data['rowno'] = 0
    data['incrowno'] = inc_rowno
    data['isoddrow'] = is_odd_row
    if args.reuse:
        engine = Engine(
            loader=loader,
            extensions=[CoreExtension()]
        )
        tpl = engine.get_template('t')
        for i in range(args.num_loops):
            output = tpl.render(data)
    else:
        for i in range(args.num_loops):
            engine = Engine(
                loader=loader,
                extensions=[CoreExtension()]
            )
            output = engine.render('t', data, {}, {})
    return output


def bench_quik(filename, tpl_text, data, args):
    import quik
    loader = quik.FileLoader(os.path.dirname(filename))
    if args.reuse:
        template = loader.load_template(os.path.basename(filename))
        for i in range(args.num_loops):
            output = template.render(data, loader=loader)
    else:
        for i in range(args.num_loops):
            template = loader.load_template(os.path.basename(filename))
            output = template.render(data, loader=loader)
    return output


def bench_mako(filename, tpl_text, data, args):
    from mako.template import Template
    if args.reuse:
        tpl = Template(tpl_text)
        for i in range(args.num_loops):
            output = tpl.render(**data)
    else:
        for i in range(args.num_loops):
            tpl = Template(tpl_text)
            output = tpl.render(**data)
    return output


bench_functions = {
    'empty': bench_empty,
    'hardcoded': bench_hardcoded,
    'inukshuk': bench_inukshuk,
    'jinja2': bench_jinja2,
    'tenjin': bench_tenjin,
    'wheezy': bench_wheezy,
    'quik': bench_quik,
    'mako': bench_mako
}


if __name__ == '__main__':
    """ To profile any single engine in this benchmark, you can run:

    $ python -m cProfile -o profile.stat bench/bench.py --engine inukshuk

    And then:

    $ pyprof2calltree -k -i profile.stat

    """
    main()
