import os
from typing import Any, Union
from datetime import datetime

from hues import huestr

from golgi import Config

from amino import List, Either, IO, Right, curried, L, _, Maybe, __
from amino.regex import Regex
from amino.logging import amino_root_logger
from amino.io import IOException

from kallikrein.run.line import Line, SpecLine, PlainLine, ResultLine, FatalLine
from kallikrein.run.data import SpecLocation
from kallikrein.run.lookup_loc import lookup_loc, LookupFailure, LookupFailures
from kallikrein.expectation import Expectation, ExpectationResult, FatalSpec, ExpectationFailed
from kallikrein.unsafe import unsafe_expectation_result, FailedUnsafeSpec
from kallikrein.run.result import SpecResult, SpecsResult


class SpecRunner:

    def __init__(self, location: SpecLocation, lines: List[Line]) -> None:
        self.location = location
        self.lines = lines

    @property
    def valid_lines(self) -> List[Line]:
        return (
            self.location.meth /
            __.exclude_by_name /
            self.lines.filter_not |
            self.lines
        )

    @property
    def spec_cls(self) -> type:
        return self.location.cls

    def _run_line(self, line: Line) -> IO[Line]:
        return (
            IO.now(line)
            if isinstance(line, PlainLine) else
            self.run_spec(line)
            if isinstance(line, SpecLine) else
            IO.failed('invalid line in spec: {}'.format(line))
        )

    @property
    def run(self) -> IO[List[Line]]:
        return self.valid_lines.traverse(self._run_line, IO)

    @property
    def run_lazy(self) -> List[IO[Line]]:
        return self.valid_lines / self._run_line

    @property
    def unsafe(self) -> bool:
        return hasattr(self.spec_cls, '__unsafe__')

    def run_spec(self, line: SpecLine) -> IO[ResultLine]:
        def recover(error: IOException) -> Expectation:
            cause = error.cause
            return (
                FailedUnsafeSpec(line, cause)
                if isinstance(cause, ExpectationFailed) else
                FatalSpec(line.name, cause)
            )
        def evaluate(expectation: Expectation) -> IO[ExpectationResult]:
            err = 'spec "{}" did not return an Expectation, but `{}`'
            return (
                expectation.evaluate
                if isinstance(expectation, Expectation) else
                IO.now(unsafe_expectation_result)
                if self.unsafe else
                IO.failed(err.format(line.text, expectation)))
        def run(inst: Any) -> IO[ResultLine]:
            start = datetime.now()
            def init() -> None:
                os.environ['KALLIKREIN_SPEC'] = line.name
                if hasattr(inst, 'setup'):
                    inst.setup()
            def teardown(a: Expectation) -> IO[Expectation]:
                del os.environ['KALLIKREIN_SPEC']
                return (
                    IO.delay(inst.teardown)
                    if hasattr(inst, 'teardown')
                    else IO.pure(None)
                )
            def result(r: ExpectationResult) -> ResultLine:
                return ResultLine(line.text, inst, r, datetime.now() - start)
            return (
                IO.delay(init)
                .and_then(IO.delay(line.spec, inst))
                .recover(recover)
                .flat_map(evaluate)
                .ensure(teardown)
                .map(result)
            )
        return IO.delay(self.spec_cls) // run

    def __str__(self) -> str:
        return '{}({}, {})'.format(self.__class__.__name__, self.spec_cls, self.lines)


def collect_specs(specs: List[str]) -> Either[LookupFailure, List[SpecLocation]]:
    return specs.flat_traverse(lookup_loc, Either)


def spec_line(spec: SpecLocation, attr: str, line: str) -> Maybe[SpecLine]:
    err = 'spec class `{}` does not define a spec `{}`'
    return (
        Maybe.getattr(spec.cls, attr)
        .to_either(err.format(spec.cls, attr))
        .map(L(SpecLine)(spec, attr, line, _))
    )


spec_regex = r'\s*(?P<text>[^#\s][^\$]+)\$(?P<spec>\w+)'


@curried
def parse_line(spec: Any, line: str) -> Line:
    match = Regex(spec_regex).match(line)
    match_data = lambda m: m.group('spec') & m.group('text')
    return (
        (match // match_data)
        .map2(L(spec_line)(spec, _, _)) |
        Right(PlainLine(line))
    )


def construct_runner(loc: SpecLocation) -> Either[str, SpecRunner]:
    doc = loc.doc.o(Right('')) if loc.allow_empty else loc.doc
    return (
        doc /
        List.lines //
        __.traverse(parse_line(loc), Either) /
        L(SpecRunner)(loc, _)
    )


def construct_runners(specs: List[SpecLocation]) -> Either[str, List[SpecRunner]]:
    return specs.traverse(construct_runner, Either)


def run_spec_class(runner: SpecRunner) -> IO[List[SpecResult]]:
    return runner.run / SpecResult


def run_specs(runners: List[SpecRunner]) -> IO[SpecsResult]:
    return runners.traverse(run_spec_class, IO) / SpecsResult


def run_specs_lazy(runners: List[SpecRunner]) -> List[List[IO[Line]]]:
    return runners.map(_.run_lazy)


def runners(specs: List[str]) -> Either[Union[LookupFailure, str], List[SpecRunner]]:
    return collect_specs(specs) // construct_runners


def specs_run_task(specs: List[str]) -> Either[Union[LookupFailure, str], IO[SpecsResult]]:
    return runners(specs) / run_specs


def specs_run_task_lazy(specs: List[str]) -> Either[Union[LookupFailure, str], List[List[IO[Line]]]]:
    return runners(specs) / run_specs_lazy


def convert_lazy_result(result: List[List[Line]], log: bool=False) -> SpecsResult:
    def convert_spec(spec: IO[ExpectationResult]) -> Line:
        line = spec.attempt.right_or_map(FatalLine)
        if log:
            line.print_report()
        return line
    def convert_loc(loc: List[IO[ExpectationResult]]) -> SpecsResult:
        return SpecResult(loc / convert_spec)
    result = SpecsResult(result / convert_loc)
    if log:
        result.print_stats()
    return result


def run_error(e: Any) -> None:
    if isinstance(e, Exception):
        msg = e.cause if isinstance(e, IOException) else e
        if Config['general'].verbose:
            amino_root_logger.caught_exception('running spec', msg)
        else:
            amino_root_logger.error('exception in spec run:')
            amino_root_logger.error(huestr(str(msg)).red.bold.colorized)
    elif isinstance(e, LookupFailures):
        amino_root_logger.error(e.report)
    else:
        amino_root_logger.error('error in spec run:')
        amino_root_logger.error(huestr(str(e)).red.bold.colorized)


def kallikrein_run(specs: List[str]) -> Either[Exception, SpecsResult]:
    return (
        (specs_run_task(specs) % __.print_report())
        .attempt
        .leffect(run_error)
    )


def kallikrein_run_lazy(specs: List[str]) -> Either[Exception, SpecsResult]:
    return (
        specs_run_task_lazy(specs) /
        L(convert_lazy_result)(_, True)
    ).leffect(run_error)

__all__ = ('kallikrein_run', 'kallikrein_run_lazy')
