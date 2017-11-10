from datetime import timedelta

from amino import _, List
from amino.logging import Logging
from amino.instances.std.datetime import TimedeltaInstances  # NOQA
from amino.lazy import lazy

from kallikrein.run.line import Line, ResultLine
from kallikrein.util.string import green_check, red_cross, yellow_clock


class SpecResult(Logging):

    def __init__(self, results: List[Line]) -> None:
        self.results = results

    @property
    def report_lines(self) -> List[str]:
        return self.results // _.output_lines


class SpecsResult(Logging):

    def __init__(self, specs: List[SpecResult]) -> None:
        self.specs = specs

    @property
    def report_lines(self) -> List[str]:
        return self.specs // _.report_lines

    @property
    def report(self) -> str:
        return self.report_lines.join_lines

    @lazy
    def results(self) -> List[ResultLine]:
        return (self.specs // _.results).filter_type(ResultLine)

    @lazy
    def duration(self) -> timedelta:
        return (self.results / _.duration).fold(timedelta)

    @property
    def duration_fmt(self) -> str:
        d = self.duration
        total = d.total_seconds()
        ms = int(d.microseconds / 1000)
        s = d.seconds % 60
        m = int((total / 60) % 60)
        h = int(total / 3600)
        return (
            '{}ms'.format(ms)
            if d < timedelta(seconds=1) else
            '{}.{:0>3}s'.format(s, ms)
            if d < timedelta(seconds=10) else
            '{}s'.format(s)
            if d < timedelta(minutes=1) else
            '{}min {}s'.format(m, s)
            if d < timedelta(hours=1) else
            '{}h {}min'.format(h, m)
        )

    @lazy
    def success_count(self) -> int:
        return self.results.filter(_.success).length

    @lazy
    def pending_count(self) -> int:
        return self.results.filter(_.pending).length

    @lazy
    def failure_count(self) -> int:
        return self.results.length - self.success_count - self.pending_count

    @property
    def success(self) -> bool:
        return self.failure_count == 0

    @property
    def stats(self) -> str:
        def fmt(count: int, sign: str) -> str:
            return f'  {sign} {count}' if count > 0 else ''
        successes = fmt(self.success_count, green_check)
        failures = fmt(self.failure_count, red_cross)
        pending = fmt(self.pending_count, yellow_clock)
        counts = f'{successes}{failures}{pending}'
        return '{} specs in {}{}'.format(
            self.results.length,
            self.duration_fmt,
            f':{counts}' if counts else ''
        )

    @property
    def stats_lines(self) -> List[str]:
        return List(self.stats)

    def print_stats(self) -> None:
        self.stats_lines % self.log.info

    @property
    def report_with_stats_lines(self) -> List[str]:
        return self.report_lines.cat(self.stats_lines)

    @property
    def report_with_stats(self) -> str:
        return self.report_with_stats_lines.join_lines

    def print_report(self) -> None:
        self.report_with_stats_lines % self.log.info

__all__ = ('SpecResult', 'SpecsResult')
